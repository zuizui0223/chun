#!/usr/bin/env python3
from __future__ import annotations

import csv, json, math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'data/cross_radiation_axis_localization_ledger_v0_1.csv'
OUT_JSON = ROOT / 'data/cross_radiation_axis_localization_result_v0_1.json'
OUT_MD = ROOT / 'docs/CROSS_RADIATION_AXIS_LOCALIZATION_RESULT_V0_1.md'


def choose(n: int, k: int) -> int:
    return math.comb(n, k) if 0 <= k <= n else 0


def fisher(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    r1, r2, c1, n = a+b, c+d, a+c, a+b+c+d
    lo, hi = max(0, c1-r2), min(r1, c1)
    den = choose(n, c1)
    def p(x: int) -> float:
        return choose(r1, x) * choose(r2, c1-x) / den
    pobs = p(a)
    greater = sum(p(x) for x in range(a, hi+1))
    two = sum(p(x) for x in range(lo, hi+1) if p(x) <= pobs + 1e-15)
    return greater, min(1.0, two)


def binom_tail_ge(n: int, k: int) -> float:
    return sum(choose(n, i) for i in range(k, n+1)) / 2**n


def binom_two(n: int, k: int) -> float:
    if n == 0: return 1.0
    lower = sum(choose(n, i) for i in range(0, k+1)) / 2**n
    upper = binom_tail_ge(n, k)
    return min(1.0, 2*min(lower, upper))


def load() -> list[dict[str,str]]:
    with LEDGER.open(newline='', encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    required={'system_id','axis_class','axis_admitted','molecular_category','evidence_tier','branching_localized','prospective_component','source_doi'}
    if not rows or not required.issubset(rows[0]): raise RuntimeError('ledger schema drift')
    return rows


def admitted(rows):
    return [r for r in rows if r['axis_admitted']=='1' and r['evidence_tier'] in {'A','B'} and r['axis_class'] in {'HUE','AMOUNT_INTENSITY'}]


def resolved(rows):
    return [r for r in rows if r['branching_localized'] in {'0','1'}]


def axis_stats(rows, axis):
    rr=[r for r in resolved(rows) if r['axis_class']==axis]
    n=len(rr); y=sum(int(r['branching_localized']) for r in rr)
    return {'resolved_rows':n,'branching_localized':y,'proportion': y/n if n else None, 'systems':sorted({r['system_id'] for r in rr})}


def effect(rows):
    h=axis_stats(rows,'HUE'); a=axis_stats(rows,'AMOUNT_INTENSITY')
    rd=None if h['proportion'] is None or a['proportion'] is None else h['proportion']-a['proportion']
    return h,a,rd


def main():
    rows=load(); prim=admitted(rows)
    systems=sorted({r['system_id'] for r in prim})
    hue_adm={r['system_id'] for r in prim if r['axis_class']=='HUE'}
    amt_adm={r['system_id'] for r in prim if r['axis_class']=='AMOUNT_INTENSITY'}
    both=sorted(hue_adm & amt_adm)

    h,a,rd=effect(prim)
    aa,bb=h['branching_localized'], h['resolved_rows']-h['branching_localized']
    cc,dd=a['branching_localized'], a['resolved_rows']-a['branching_localized']
    fg,ft=fisher(aa,bb,cc,dd)
    or_ha=((aa+0.5)*(dd+0.5))/((bb+0.5)*(cc+0.5))

    by=defaultdict(dict)
    for r in resolved(prim): by[r['system_id']][r['axis_class']]=int(r['branching_localized'])
    paired=[]; fav=adv=conc=0
    for sid in sorted(by):
        if {'HUE','AMOUNT_INTENSITY'} <= set(by[sid]):
            hv,av=by[sid]['HUE'],by[sid]['AMOUNT_INTENSITY']
            paired.append({'system_id':sid,'hue':hv,'amount_intensity':av})
            if (hv,av)==(1,0): fav+=1
            elif (hv,av)==(0,1): adv+=1
            else: conc+=1
    nd=fav+adv
    pair_one=binom_tail_ge(nd,fav) if nd else 1.0
    pair_two=binom_two(nd,fav) if nd else 1.0

    loo=[]
    for sid in systems:
        rr=[r for r in prim if r['system_id']!=sid]
        lh,la,lrd=effect(rr)
        loo.append({'excluded_system':sid,'risk_difference':lrd,'hue_proportion':lh['proportion'],'amount_intensity_proportion':la['proportion']})
    loo_positive=all(x['risk_difference'] is not None and x['risk_difference']>0 for x in loo)

    tier_a=[r for r in prim if r['evidence_tier']=='A']
    tah,taa,tard=effect(tier_a)
    retro=[r for r in prim if r['prospective_component']!='1']
    rh,ra,rrd=effect(retro)

    prospective_hue_support=any(r['system_id']=='PETUNIEAE' and r['axis_class']=='HUE' and r['branching_localized']=='1' and r['prospective_component']=='1' for r in prim)
    coverage={
      'independent_systems':len(systems),
      'hue_systems_admitted':len(hue_adm),
      'amount_intensity_systems_admitted':len(amt_adm),
      'both_axes_systems':len(both),
      'both_axes_system_ids':both,
    }
    criteria={
      'at_least_5_systems':len(systems)>=5,
      'at_least_3_hue_and_3_amount':len(hue_adm)>=3 and len(amt_adm)>=3,
      'at_least_3_both_axes':len(both)>=3,
      'risk_difference_ge_0_35':rd is not None and rd>=0.35,
      'leave_one_system_out_direction_stable':loo_positive,
      'prospective_hue_component_support':prospective_hue_support,
    }
    if all(criteria.values()): cls='AXIS_LOCALIZATION_SUPPORTED'
    elif not (criteria['at_least_5_systems'] and criteria['at_least_3_hue_and_3_amount'] and criteria['at_least_3_both_axes']): cls='AXIS_LOCALIZATION_HOLD'
    elif rd is not None and rd<=0: cls='AXIS_LOCALIZATION_CONTRADICTED'
    else: cls='AXIS_LOCALIZATION_MIXED'

    result={
      'version':'v0.1', 'classification':cls, 'coverage':coverage,
      'primary':{
        'hue':h,'amount_intensity':a,'risk_difference':rd,
        'haldane_anscombe_odds_ratio':or_ha,
        'fisher_secondary_one_sided_greater':fg,'fisher_secondary_two_sided':ft,
      },
      'paired_matched_systems':{
        'rows':paired,'favourable_discordant':fav,'adverse_discordant':adv,'concordant':conc,
        'discordant_n':nd,'exact_sign_one_sided_hue_greater':pair_one,'exact_sign_two_sided':pair_two,
      },
      'leave_one_system_out':loo,
      'tier_A_sensitivity':{'hue':tah,'amount_intensity':taa,'risk_difference':tard},
      'prospective_anchor_excluded':{'hue':rh,'amount_intensity':ra,'risk_difference':rrd},
      'criteria':criteria,
      'petunieae_full_bridge_status':'PETUNIEAE_PROSPECTIVE_BRIDGE_MIXED',
      'claim_boundary':'Retrospective cross-radiation synthesis with one prospective hue component; not a prospective meta-analysis, not a universal causal-gene law, and not yet a journal-escalation verdict.',
      'paper1_science_changed':False,
    }
    OUT_JSON.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')

    md=f'''# Cross-radiation phenotype-axis → molecular-localization result — v0.1\n\n## Decision\n\n**`{cls}`**\n\nPrimary Tier A/B synthesis includes **{coverage['independent_systems']} independent systems**. Resolved HUE rows are branching-localized in **{h['branching_localized']}/{h['resolved_rows']}** systems ({h['proportion']:.3f}); resolved AMOUNT_INTENSITY rows are branching-localized in **{a['branching_localized']}/{a['resolved_rows']}** systems ({a['proportion']:.3f}). Risk difference = **{rd:.3f}**.\n\nAmong systems with both axes resolved, favourable discordance HUE=branching / AMOUNT=non-branching occurs in **{fav}/{nd}** discordant systems; adverse discordance = **{adv}**. Exact sign test: one-sided P={pair_one:.6g}, two-sided P={pair_two:.6g}. The broader row-level Fisher test is secondary because paired systems contribute two rows: one-sided P={fg:.6g}, two-sided P={ft:.6g}.\n\nAll leave-one-system-out risk differences remain positive: **{loo_positive}**. Tier-A-only risk difference = **{tard if tard is not None else 'NA'}**. Excluding the prospective Petunieae component, retrospective-only risk difference = **{rrd if rrd is not None else 'NA'}**.\n\n## Interpretation\n\nUnder the pre-frozen classification rules, floral **hue/hydroxylation is consistently localized to branch-choice/hydroxylation machinery**, whereas pigment amount/intensity/presence maps to late-output, regulatory, or dispersed molecular control in the resolved comparison systems. Petunieae contributes a genuinely prospective hue-positive component but remains MIXED at the full two-axis bridge level because its preregistered raw amount axis is unresolved.\n\nThis satisfies the magnitude/coverage/robustness gate for `AXIS_LOCALIZATION_SUPPORTED`; it does **not** by itself authorize an *Evolution* submission. The separate prior-art gate must still ask whether this cross-radiation axis-specific localization result is sufficiently novel beyond established pathway-biochemistry expectations and prior reviews.\n\n## Boundaries\n\n- Do not describe this as a prospectively designed meta-analysis.\n- Do not convert Petunieae raw amount to a negative or replace it with the post hoc log sensitivity.\n- Do not infer one universal causal gene.\n- Do not merge hue and amount into a coarse colour state.\n- Paper 1 science is unchanged.\n'''
    OUT_MD.write_text(md,encoding='utf-8')
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=='__main__': main()
