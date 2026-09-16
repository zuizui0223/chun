#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'data/cross_radiation_evolution_letters_claim_registry_v0_1.json'
REFS=ROOT/'data/cross_radiation_el_reference_manifest_v0_1.json'
GATE=ROOT/'data/cross_radiation_evolution_letters_submission_gate_v0_2.json'
MAN=ROOT/'manuscript/CROSS_RADIATION_EVOLUTION_LETTERS_V0_2.md'


def words(s:str)->int:
    return len(re.findall(r"\b[\w'’-]+\b", s, flags=re.UNICODE))


def section(text:str, heading:str)->str:
    m=re.search(rf'^# {re.escape(heading)}\s*$', text, flags=re.M|re.I)
    if not m: raise AssertionError(f'missing section: {heading}')
    tail=text[m.end():]
    n=re.search(r'^# ', tail, flags=re.M)
    return tail[:n.start()] if n else tail


def subsection(text:str, heading:str)->str:
    m=re.search(rf'^## {re.escape(heading)}\s*$', text, flags=re.M|re.I)
    if not m: raise AssertionError(f'missing subsection: {heading}')
    tail=text[m.end():]
    n=re.search(r'^#{1,2} ', tail, flags=re.M)
    return tail[:n.start()] if n else tail


def main():
    reg=json.loads(REG.read_text())
    refs=json.loads(REFS.read_text())
    gate=json.loads(GATE.read_text())
    text=MAN.read_text()
    low=text.lower()

    assert reg['status']=='CROSS_RADIATION_EVOLUTION_LETTERS_CLAIM_REGISTRY'
    assert refs['status']=='CROSS_RADIATION_EL_REFERENCES_VERIFIED'
    assert refs['paper1_science_changed'] is False
    assert gate['status']=='SCIENCE_AND_JOURNAL_FORMAT_READY_METADATA_HOLD'
    assert gate['target_journal']=='Evolution Letters'
    assert gate['article_type']=='Letter'
    assert gate['paper1_science_changed'] is False
    assert len(gate['submission_metadata_holds'])==5

    title=section(text,'Title').strip().splitlines()[0].strip('* ')
    teaser=subsection(text,'Teaser text')
    abstract=section(text,'Abstract')
    intro=section(text,'Introduction')
    methods=section(text,'Methods')
    results=section(text,'Results')
    discussion=section(text,'Discussion')
    references=section(text,'References')
    main_text='\n'.join([intro,methods,results,discussion])

    fmt=gate['format_contract']
    assert words(title)<=fmt['title_max_words'], words(title)
    assert words(teaser)<=fmt['teaser_max_words'], words(teaser)
    assert words(abstract)<=fmt['abstract_max_words'], words(abstract)
    assert words(main_text)<=fmt['main_text_target_max_words'], words(main_text)

    km=re.search(r'^Keywords:\s*(.+)$', text, flags=re.M|re.I)
    assert km
    keywords=[x.strip() for x in km.group(1).split(';') if x.strip()]
    assert len(keywords)<=fmt['keywords_max'], len(keywords)

    for required in fmt['required_sections']:
        section(text, required)

    # Evolution Letters manuscript prose is normalized to US spelling; published reference titles may retain original spelling.
    before_refs=text.split('# References',1)[0]
    assert re.search(r'\bcolour\b|\bcolours\b|flower-colour|visible-colour', before_refs, flags=re.I) is None

    # No provisional square-bracket author-year citations remain.
    assert re.search(r'\[[A-Z][^\]]+\d{4}[^\]]*\]', before_refs) is None

    # Five figure legends and five explicit alt-text statements are required.
    legends=re.findall(r'^\*\*Figure [1-5]\.', text, flags=re.M)
    assert len(legends)==gate['figure_contract']['main_figures'], len(legends)
    assert text.count('**Alt text:**')==gate['figure_contract']['main_figures']

    # References are bound to a verified manifest and data sources are explicitly tagged.
    for r in refs['references']:
        token=r.get('doi') or r.get('identifier')
        assert token and token.lower() in references.lower(), r['key']
    for token in gate['required_reference_identifiers']:
        assert token.lower() in text.lower(), token
    assert references.count('[dataset]')==2
    assert '10.5061/dryad.r4xgxd2sc' in section(text,'Data and code availability')
    assert 'osf.io/zg9cu' in section(text,'Data and code availability')

    # Required in-text citations.
    for cite in (
        'Ng & Smith, 2016','Rausher, 2008','Sobel & Streisfeld, 2013','Wessinger & Rausher, 2012',
        'Tarasov, 2019','Vera-Ruiz et al., 2022','Roguz et al., 2020',
        'Sinnott-Armstrong et al. (2025, 2026)','Wheeler et al. (2023a, 2023b)'):
        assert cite in text, cite

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
    counts=f51['terminal_class_counts']
    assert counts['PROFILE_SIGNALLED_COARSE']==3
    assert f51['intermediate_unique_winner_count']==0
    assert counts['PROFILE_SIGNALLED_FINE']==3
    assert counts['PROFILE_SIGNALLED_TIED']==6
    assert counts['PROFILE_NO_PHYLOGENETIC_SIGNAL']==16

    assert mod['status']=='NO_MODERATOR_QUALIFIED_CURRENT_STANDARDIZED_TRAINING'
    assert len(mod['qualified_predictors'])==0
    assert pet['primary_frame']['eligible_tips']==47
    assert pet['observed']['AUC_fine']==c['petunieae']['AUC_fine']
    assert pet['p_signal_one_sided']['fine']==0.0001
    assert pet['p_winner_gt_runner']==0.0001
    assert pet['terminal_class']=='PROFILE_SIGNALLED_FINE'
    assert pet['do_not_count_as_new_prospective_replication'] is True
    assert ident['exact_profile_completed_total']==30
    assert ident['training_composition']['biochemical_composition']==1
    assert ident['representation_type_model_fit'] is False
    assert frontier['status']=='SECOND_NONVISIBLE_EXACT_PROFILE_NOT_YET_IDENTIFIED'

    # Claim ceilings remain enforced without keeping an internal-warning section in the submission draft.
    for bad in reg['forbidden_claim_fragments']:
        assert bad.lower() not in low, bad

    # Submission metadata are intentionally left as explicit holds rather than invented.
    assert 'To be completed using CRediT roles before submission.' in text
    assert '# Funding\n\nTo be completed before submission.' in text
    assert '# Acknowledgements\n\nTo be completed before submission.' in text
    assert 'will be archived with a persistent identifier before submission' in text

    print(json.dumps({
      'status':'SCIENCE_AND_JOURNAL_FORMAT_READY_METADATA_HOLD',
      'title_words':words(title),
      'teaser_words':words(teaser),
      'abstract_words':words(abstract),
      'main_text_words':words(main_text),
      'keywords':len(keywords),
      'references':len(refs['references']),
      'dataset_citations':references.count('[dataset]'),
      'figure_legends':len(legends),
      'metadata_holds':len(gate['submission_metadata_holds']),
      'iris_decision':iris['decision'],
      'flowerclades_completed':f51['clades_completed_exact_profile'],
      'petunieae_terminal_class':pet['terminal_class'],
      'representation_model_fit':ident['representation_type_model_fit']
    },indent=2))

if __name__=='__main__': main()
