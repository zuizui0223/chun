#!/usr/bin/env python3
"""Canonical, class-stratified recurrence before/after candidate-free remeasurement.

Literature edges are first oriented to a prespecified biological target and split into
anthocyanin-gain versus yellow-development classes. Unknown A/F/C/P cells are then
exhaustively completed by {up,down,same}. Optional candidate-free measurements use the
same state space but never borrow literature values for missing cells.
"""
from __future__ import annotations
import argparse,csv,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
AXES=("A","F","C","P"); STATES=("up","down","same"); RES=set(STATES)
FLIP={"up":"down","down":"up","same":"same","unknown":"unknown","mixed":"mixed"}

def read(p):
    with p.open(newline="",encoding="utf-8") as f:r=list(csv.DictReader(f))
    if not r: raise ValueError(f"empty input: {p}")
    return r

def collapse(v):
    k=[x for x in v if x!="unknown"]
    return "unknown" if not k else k[0] if len(set(k))==1 else "mixed"

def literature(reg,orient):
    om={r["edge_id"]:r for r in orient}; ids={r["edge_id"] for r in reg}
    if ids!=set(om): raise ValueError("orientation registry must match edge registry exactly")
    g=defaultdict(lambda:defaultdict(lambda:defaultdict(list))); edges=[]
    for r in reg:
        o=om[r["edge_id"]]; rev=o["orientation"].lower()=="reverse"
        e={"edge_id":r["edge_id"],"transition_class":o["transition_class"],
           "dependence_cluster":r["dependence_cluster"],"orientation":o["orientation"],
           "canonical_target":o["canonical_target"]}
        for a in AXES:
            x=r[f"{a}_change"].lower(); x=FLIP[x] if rev else x; e[a]=x
            g[o["transition_class"]][r["dependence_cluster"]][a].append(x)
        edges.append(e)
    sig={c:{k:[collapse(v[a]) for a in AXES] for k,v in z.items()} for c,z in g.items()}
    return sig,edges

def candidate(rows):
    req={"measurement_id","dependence_cluster","transition_class","axis","direction","status","source"}
    if not req<=set(rows[0]): raise ValueError(f"candidate-free columns missing: {sorted(req-set(rows[0]))}")
    g=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for r in rows:
        a=r["axis"]; x=r["direction"].lower(); st=r["status"].lower()
        if a not in AXES: raise ValueError(f"bad axis {a}")
        if st=="resolved" and x not in RES: raise ValueError("resolved direction must be up/down/same")
        if st not in {"resolved","unresolved"}: raise ValueError(f"bad status {st}")
        g[r["transition_class"]][r["dependence_cluster"]][a].append(x if st=="resolved" else "unknown")
    return {c:{k:[collapse(v.get(a,["unknown"])) for a in AXES] for k,v in z.items()} for c,z in g.items()}

def exact_rec(s):
    if len(s)<2:return None
    cc=Counter(tuple(v) for v in s.values()); n=len(s)
    return sum((x/n)**2 for x in cc.values())

def concord(s):
    k=list(s)
    if len(k)<2:return None
    q=[]
    for i in range(len(k)):
        for j in range(i+1,len(k)):
            q.append(sum(x==y for x,y in zip(s[k[i]],s[k[j]]))/4)
    return sum(q)/len(q)

def bounds(s):
    u=[(k,i) for k,v in s.items() for i,x in enumerate(v) if x=="unknown"]
    if len(s)<2:return {"status":"not_testable_single_cluster","n_clusters":len(s),"n_unresolved_cluster_axes":len(u)}
    n=3**len(u)
    if n>2_000_000: raise ValueError(f"completion space too large: {n}")
    er=[]; pc=[]
    for vals in itertools.product(STATES,repeat=len(u)):
        z={k:list(v) for k,v in s.items()}
        for (k,i),x in zip(u,vals):z[k][i]=x
        er.append(exact_rec(z)); pc.append(concord(z))
    return {"status":"exact_partial_identification","n_clusters":len(s),
            "n_unresolved_cluster_axes":len(u),"n_exact_completions":n,
            "exact_signature_recurrence":{"minimum":min(er),"maximum":max(er)},
            "pairwise_axis_concordance":{"minimum":min(pc),"maximum":max(pc)}}

def overlap(lit,cf):
    out={}
    for c in sorted(set(lit)&set(cf)):
        common=sorted(set(lit[c])&set(cf[c])); n=agree=0; conflicts=[]
        for k in common:
            for i,a in enumerate(AXES):
                x,y=lit[c][k][i],cf[c][k][i]
                if x in RES and y in RES:
                    n+=1
                    if x==y:agree+=1
                    else:conflicts.append({"cluster":k,"axis":a,"literature":x,"candidate_free":y})
        out[c]={"common_clusters":common,"n_comparable_resolved_cells":n,"n_agree":agree,
                "agreement_fraction":agree/n if n else None,"conflicts":conflicts}
    return out

def contraction(lit,cf):
    out={}
    for c in sorted(set(lit)&set(cf)):
        common=sorted(set(lit[c])&set(cf[c]))
        if len(common)<2:
            out[c]={"status":"not_testable_fewer_than_two_common_clusters","common_clusters":common};continue
        L=bounds({k:lit[c][k] for k in common}); C=bounds({k:cf[c][k] for k in common})
        lw=L["pairwise_axis_concordance"]["maximum"]-L["pairwise_axis_concordance"]["minimum"]
        cw=C["pairwise_axis_concordance"]["maximum"]-C["pairwise_axis_concordance"]["minimum"]
        out[c]={"status":"comparable_common_cluster_set","common_clusters":common,
                "literature_common_cluster_bounds":L,"candidate_free_common_cluster_bounds":C,
                "literature_width":lw,"candidate_free_width":cw,"width_reduction":lw-cw}
    return out

def write_sig(p,regime,s):
    rows=[{"regime":regime,"transition_class":c,"dependence_cluster":k,**dict(zip(AXES,v))}
          for c in sorted(s) for k,v in sorted(s[c].items())]
    if not rows:return
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["regime","transition_class","dependence_cluster",*AXES]);w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--registry",type=Path,required=True);ap.add_argument("--orientation",type=Path,required=True)
    ap.add_argument("--candidate-free",type=Path);ap.add_argument("--out-dir",type=Path,required=True);a=ap.parse_args()
    lit,edges=literature(read(a.registry),read(a.orientation)); a.out_dir.mkdir(parents=True,exist_ok=True)
    s={"status":"canonical_class_stratified_recurrence","axes":list(AXES),
       "literature":{"classes":{c:bounds(v) for c,v in sorted(lit.items())}},
       "interpretation":"Red/pink-gain and yellow-development trajectories are canonically oriented and analyzed separately; the former pooled all-colour recurrence is exploratory only.",
       "candidate_free_rule":"Candidate-free measurements are independent remeasurements and never borrow literature directions for missing cells."}
    write_sig(a.out_dir/"literature_canonical_signatures.csv","literature",lit)
    with (a.out_dir/"canonicalized_edges.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["edge_id","transition_class","dependence_cluster","orientation","canonical_target",*AXES]);w.writeheader();w.writerows(edges)
    if a.candidate_free:
        cf=candidate(read(a.candidate_free));write_sig(a.out_dir/"candidate_free_signatures.csv","candidate_free",cf)
        s["candidate_free"]={"classes":{c:bounds(v) for c,v in sorted(cf.items())}}
        s["literature_vs_candidate_free_overlap"]=overlap(lit,cf)
        s["identified_set_contraction_on_common_clusters"]=contraction(lit,cf)
    (a.out_dir/"summary.json").write_text(json.dumps(s,indent=2,ensure_ascii=False)+"\n",encoding="utf-8");print(json.dumps(s,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
