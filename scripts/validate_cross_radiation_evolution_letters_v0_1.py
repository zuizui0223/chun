#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'data/cross_radiation_evolution_letters_claim_registry_v0_1.json'
MAN=ROOT/'manuscript/CROSS_RADIATION_EVOLUTION_LETTERS_V0_1.md'


def words(s:str)->int:
    return len(re.findall(r"\b[\w'’-]+\b", s, flags=re.UNICODE))


def section(text:str, heading:str)->str:
    m=re.search(rf'^# {re.escape(heading)}\s*$', text, flags=re.M|re.I)
    if not m: raise AssertionError(f'missing section: {heading}')
    tail=text[m.end():]
    n=re.search(r'^# ', tail, flags=re.M)
    return tail[:n.start()] if n else tail


def main():
    reg=json.loads(REG.read_text())
    text=MAN.read_text()
    low=text.lower()

    assert reg['status']=='CROSS_RADIATION_EVOLUTION_LETTERS_CLAIM_REGISTRY'
    assert reg['paper1_science_changed'] is False
    assert reg['journal_format_contract']['article_type']=='Letter'

    title=section(text,'Title').strip().splitlines()[0].strip('* ')
    abstract=section(text,'Abstract')
    intro=section(text,'Introduction')
    methods=section(text,'Methods')
    results=section(text,'Results')
    discussion=section(text,'Discussion')
    main_text='\n'.join([intro,methods,results,discussion])
    assert words(title)<=reg['journal_format_contract']['title_max_words'], words(title)
    assert words(abstract)<=reg['journal_format_contract']['abstract_max_words'], words(abstract)
    assert words(main_text)<=reg['journal_format_contract']['main_text_target_max_words'], words(main_text)

    iris=json.loads((ROOT/reg['authoritative_sources']['iris']).read_text())
    f51=json.loads((ROOT/reg['authoritative_sources']['flowerclades51']).read_text())
    mod=json.loads((ROOT/reg['authoritative_sources']['tree_moderator']).read_text())
    pet=json.loads((ROOT/reg['authoritative_sources']['petunieae']).read_text())
    ident=json.loads((ROOT/reg['authoritative_sources']['representation_identifiability']).read_text())
    frontier=json.loads((ROOT/reg['authoritative_sources']['frontier']).read_text())
    c=reg['frozen_numeric_claims']

    assert iris['decision']==c['iris']['decision']=='FAIL'
    assert iris['primary_frame']['eligible_tips']==c['iris']['eligible_tips']==169
    assert iris['observed']['AUC_coarse']==c['iris']['AUC_coarse']
    assert iris['observed']['AUC_intermediate']==c['iris']['AUC_intermediate']
    assert iris['observed']['AUC_fine']==c['iris']['AUC_fine']
    assert iris['empirical_p_one_sided']['fine_gt_intermediate_for_fail_check']==c['iris']['p_fine_gt_intermediate']
    assert iris['post_hoc_upgrade_allowed'] is False

    assert f51['clades_total']==c['flowerclades51']['total']==51
    assert f51['clades_completed_exact_profile']==c['flowerclades51']['completed']==28
    assert f51['clades_hold']==c['flowerclades51']['hold']==23
    counts=f51['terminal_class_counts']
    assert counts['PROFILE_SIGNALLED_COARSE']==c['flowerclades51']['coarse_winners']==3
    assert f51['intermediate_unique_winner_count']==c['flowerclades51']['intermediate_winners']==0
    assert counts['PROFILE_SIGNALLED_FINE']==c['flowerclades51']['fine_winners']==3
    assert counts['PROFILE_SIGNALLED_TIED']==c['flowerclades51']['tied']==6
    assert counts['PROFILE_NO_PHYLOGENETIC_SIGNAL']==c['flowerclades51']['no_signal']==16

    assert mod['status']==c['tree_moderator']['status']
    assert len(mod['candidate_predictors'])==c['tree_moderator']['candidate_predictors']==4
    assert len(mod['qualified_predictors'])==c['tree_moderator']['qualified_predictors']==0
    assert mod['next_heldout_prediction_frozen'] is False

    assert pet['primary_frame']['eligible_tips']==c['petunieae']['eligible_tips']==47
    assert pet['observed']['AUC_coarse']==c['petunieae']['AUC_coarse']
    assert pet['observed']['AUC_intermediate']==c['petunieae']['AUC_intermediate']
    assert pet['observed']['AUC_fine']==c['petunieae']['AUC_fine']
    assert pet['p_signal_one_sided']['fine']==c['petunieae']['p_fine_signal']==0.0001
    assert pet['p_winner_gt_runner']==c['petunieae']['p_fine_gt_runner']==0.0001
    assert pet['terminal_class']==c['petunieae']['terminal_class']=='PROFILE_SIGNALLED_FINE'
    assert pet['do_not_count_as_new_prospective_replication'] is True
    assert c['petunieae']['prospective'] is False

    rt=c['representation_training']
    assert ident['exact_profile_completed_total']==rt['completed_total']==30
    assert ident['training_composition']['standardized_visible_colour']==rt['visible_standardized']==28
    assert ident['training_composition']['biochemical_composition']==rt['biochemical']==1
    assert ident['training_composition']['mixed_pigment_hue_prospective']==rt['mixed_prospective']==1
    assert ident['representation_type_model_fit'] is False
    assert rt['representation_moderator_identifiable'] is False
    assert frontier['status']=='SECOND_NONVISIBLE_EXACT_PROFILE_NOT_YET_IDENTIFIED'

    # Required manuscript anchors. Wording is deliberately loose enough for editing,
    # while requiring the scientific boundaries to remain visible.
    for phrase in ('no universal', 'prospect', '28', 'intermediate', 'petunieae', 'retrospective standardized', 'representation'):
        assert phrase in low, phrase

    for bad in reg['forbidden_claim_fragments']:
        # The internal claim-boundary section is allowed to quote a forbidden phrase
        # only when it is explicitly preceded by "Do not claim" or equivalent.
        if bad.lower() in low:
            occurrences=[m.start() for m in re.finditer(re.escape(bad.lower()),low)]
            for pos in occurrences:
                context=low[max(0,pos-80):pos]
                assert ('do not' in context or 'cannot' in context or 'forbidden' in context), bad

    # Paper 1 separation must be explicit and no Paper 1 authoritative result is edited here.
    assert 'separate cross-radiation paper' in low
    assert 'camellia paper 1' in low

    print(json.dumps({
      'status':'CROSS_RADIATION_EVOLUTION_LETTERS_V0_1_VALID',
      'title_words':words(title),
      'abstract_words':words(abstract),
      'main_text_words':words(main_text),
      'iris_decision':iris['decision'],
      'flowerclades_completed':f51['clades_completed_exact_profile'],
      'petunieae_terminal_class':pet['terminal_class'],
      'representation_model_fit':ident['representation_type_model_fit']
    },indent=2))

if __name__=='__main__': main()
