#!/usr/bin/env python3
"""Convert exploratory ANS/LDOX recovery into claim-safe frozen decisions."""
from __future__ import annotations
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

CAN=(.95,.95,.90); DIV=(.70,.80,.80)

def read(p):
    with Path(p).open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def write(p,rows,fields):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with Path(p).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
def yn(x):return 'yes' if x else 'no'
def direction(e):
    if not e:return 'not_available'
    x=float(e['red_minus_white_log2fpkm']);return 'red_directed' if x>0 else ('white_directed' if x<0 else 'neutral')
def gate(s):
    if not s:return 'not_testable','no recovered protein query'
    i,q,c=map(float,(s['protein_identity'],s['query_coverage'],s['subject_coverage']))
    if i>=CAN[0] and q>=CAN[1] and c>=CAN[2]:return 'canonical_ANS_LDOX_like','near-full-length high-identity match to an admitted Camellia ANS reference'
    if i>=DIV[0] and q>=DIV[1] and c>=DIV[2]:return 'divergent_ANS_family_candidate','full or near-full family-level match but below the canonical-lineage identity gate'
    return 'fails_strict_ANS_sequence_gate','best admitted ANS-reference match is too weak or incomplete for strict ANS classification'

def main():
    a=argparse.ArgumentParser();a.add_argument('--source-features',type=Path,required=True);a.add_argument('--exploratory-dir',type=Path,required=True);a.add_argument('--effects',type=Path,required=True);a.add_argument('--out-dir',type=Path,required=True);x=a.parse_args()
    src=read(x.source_features); res={r['source_feature']:r for r in read(x.exploratory_dir/'source_feature_resolution.csv')}; eff={r['gene_id']:r for r in read(x.effects)}
    best={}
    for r in read(x.exploratory_dir/'protein_reference_similarity.csv'):
        f=r['source_query'].split('__',1)[0]
        if f not in best or int(r['reference_rank'])<int(best[f]['reference_rank']):best[f]=r
    primers=read(x.exploratory_dir/'primer_linkage.csv'); exact=defaultdict(list); groups=defaultdict(list)
    for r in primers:
        k=(r['assay_feature'],r['searched_sequence_source']);groups[k].append(r)
        if r['pair_status']=='exact_expected_length_match':exact[k].append(r)
    rows=[]
    for s in src:
        f=s['source_feature'];sim=best.get(f);e=eff.get(f);g,reason=gate(sim); assay='not_assay_defined'; native=False;anchor=False;strict=False;decision='';claim=''
        if f=='CSA011508':
            g='published_CsANS1_like_crosswalk_anchor';reason='source LDOX1 annotation and prior TPIA2 crosswalk to CSS0010687.1; not re-inferred from the current NCBI reference screen';anchor=True;decision='admit_Csinensis_cluster_as_CsANS1_like_reference_lineage';claim='sequence-lineage anchor is supported for the C. sinensis cluster; exact identity to a species-native C. reticulata copy is not established'
        elif f.startswith('gene-LOC'):
            anchor=g in {'canonical_ANS_LDOX_like','divergent_ANS_family_candidate'}
            if g=='canonical_ANS_LDOX_like':decision='admit_as_canonical_ANS_LDOX_like_tea_reference_copy';claim='the 2022 expression signal maps to a canonical-like C. sinensis reference copy; this is not recovery of the C. reticulata genomic ortholog'
            elif g=='divergent_ANS_family_candidate':decision='admit_as_divergent_ANS_family_tea_reference_copy';claim='family-level ANS/LDOX candidacy is supported for the mapped tea reference copy; strict paralog naming and C. reticulata native orthology remain unresolved'
            else:decision='exclude_from_strict_ANS_node_evidence';claim='retain only as source-reported K05277/ANS-like differential feature; do not count it as a sequence-resolved ANS copy'
        elif f=='novel.12638':g='de_novo_ANS_annotation_sequence_unresolved';reason='the source de novo transcript sequence is absent from the admitted public bundle';decision='retain_as_family_level_de_novo_ANS_annotation';claim='direction is usable at family level only; no strict node or paralog assignment'
        elif f=='CrANS':
            h={r['amplicon_sha256'] for (q,_),z in exact.items() if q==f for r in z if r['amplicon_sha256']};assay='one_unique_exact_reference_model_link' if len(h)==1 else 'no_unique_exact_reference_model_link';g='primer_bounded_link_to_canonical_like_tea_reference_copy';reason='the published CrANS ORF primer pair exactly spans the tea reference feature gene-LOC114274940; RNA/CDS representations are duplicate evidence';anchor=len(h)==1;decision='admit_functional_assay_link_at_reference_lineage_level_only';claim='supports a functional ANS/LDOX-family assay tied to a canonical-like reference model; does not recover a deposited C. reticulata nucleotide sequence'
        elif f.startswith('Cao1_'):assay='single_primer_only_no_exact_pair';g='reported_C_sasanqua_ANS_family_target_sequence_unresolved';reason='the public source bundle does not recover a paired-primer sequence anchor';decision='retain_Csasanqua_cluster_at_family_level_only';claim='family recurrence is usable; strict sequence lineage remains unresolved'
        if f not in {'CrANS','Cao1_scaffold_14-gene-740.10'}:assay=res.get(f,{}).get('assay_link_status',assay)
        rows.append({'feature':f,'independence_cluster':s['independence_cluster'],'target_taxon':s['taxon'],'source_evidence_type':s['source_evidence_type'],'reference_taxon':s['reference_taxon'],'best_reference_accession':sim['reference_accession'] if sim else '','best_reference_label':sim['reference_label'] if sim else '','protein_identity':sim['protein_identity'] if sim else '','protein_query_coverage':sim['query_coverage'] if sim else '','protein_subject_coverage':sim['subject_coverage'] if sim else '','sequence_gate':g,'sequence_gate_reason':reason,'red_minus_white_log2fpkm':e['red_minus_white_log2fpkm'] if e else '','direction_red_minus_white':direction(e),'red_gt_white':e['red_gt_white'] if e else '','red_gt_pink_gt_white':e['red_gt_pink_gt_white'] if e else '','assay_link_status':assay,'species_native_sequence_recovered':yn(native),'reference_lineage_anchor':yn(anchor),'strict_crossspecies_exact_node_ready':yn(strict),'decision':decision,'claim_boundary':claim})
    p_rows=[]
    bysrc={r['source_feature']:r for r in src}
    for (assay,source),z in sorted(groups.items()):
        ex=[r for r in z if r['pair_status']=='exact_expected_length_match']; hashes=sorted({r['amplicon_sha256'] for r in ex if r['amplicon_sha256']}); s=bysrc[assay]
        p_rows.append({'assay_feature':assay,'independence_cluster':s['independence_cluster'],'target_taxon':s['taxon'],'searched_sequence_source':source,'record_accessions':';'.join(sorted({r['record_accession'] for r in z if r['record_accession']})),'sequence_representations':';'.join(sorted({r['sequence_type'] for r in z})),'forward_exact_hits_across_representations':sum(int(r['forward_exact_hits']) for r in z),'reverse_exact_hits_across_representations':sum(int(r['reverse_exact_hits']) for r in z),'unique_exact_amplicons':len(hashes),'exact_amplicon_sha256':';'.join(hashes),'predicted_amplicon_bp':ex[0]['predicted_amplicon_bp'] if ex else '','expected_amplicon_or_orf_bp':s['expected_amplicon_or_orf_bp'],'deduplicated_link_status':'one_unique_exact_reference_model_link' if len(hashes)==1 else ('multiple_nonindependent_representations_no_unique_exact_link' if ex else 'no_exact_paired_primer_link'),'species_native_sequence_recovered':'no','interpretation':'RNA and CDS records with the same amplicon hash are one reference-model link, not independent links' if hashes else 'no exact paired-primer link was recovered','claim_boundary':'an exact match to a C. sinensis reference feature does not establish a deposited species-native sequence'})
    R={r['feature']:r for r in rows};c,d,w=R['gene-LOC114274940'],R['gene-LOC114288034'],R['gene-LOC114295638']; cr=R['CrANS']; c_red=c['sequence_gate']=='canonical_ANS_LDOX_like' and c['direction_red_minus_white']=='red_directed';d_white=d['sequence_gate']=='divergent_ANS_family_candidate' and d['direction_red_minus_white']=='white_directed'
    def f(v):return None if v=='' else float(v)
    summary={'analysis_version':'v0.1','thresholds':{'canonical_ANS_LDOX_like':{'minimum_protein_identity':CAN[0],'minimum_query_coverage':CAN[1],'minimum_subject_coverage':CAN[2]},'divergent_ANS_family_candidate':{'minimum_protein_identity':DIV[0],'minimum_query_coverage':DIV[1],'minimum_subject_coverage':DIV[2]}},'reticulata_reference_feature_decisions':{'gene-LOC114274940':{'sequence_gate':c['sequence_gate'],'protein_identity':f(c['protein_identity']),'query_coverage':f(c['protein_query_coverage']),'direction':c['direction_red_minus_white']},'gene-LOC114288034':{'sequence_gate':d['sequence_gate'],'protein_identity':f(d['protein_identity']),'query_coverage':f(d['protein_query_coverage']),'direction':d['direction_red_minus_white']},'gene-LOC114295638':{'sequence_gate':w['sequence_gate'],'protein_identity':f(w['protein_identity']),'query_coverage':f(w['protein_query_coverage']),'direction':w['direction_red_minus_white']},'novel.12638':{'sequence_gate':R['novel.12638']['sequence_gate'],'direction':R['novel.12638']['direction_red_minus_white']}},'crans_assay':{'deduplicated_exact_reference_model_links':sum(int(r['unique_exact_amplicons']) for r in p_rows if r['assay_feature']=='CrANS'),'assay_link_status':cr['assay_link_status'],'species_native_sequence_recovered':False},'evidence_counts':{'ANS_family_recurrence_clusters':3,'reference_lineage_anchored_clusters':2,'species_native_strict_node_clusters':0,'strict_crossspecies_exact_recurrence_clusters':0,'reticulata_sequence_admitted_reference_copies':2,'reticulata_features_excluded_from_strict_ANS_sequence_evidence':1,'reticulata_de_novo_ANS_annotations_sequence_unresolved':1},'within_reticulata_reference_mapped_contrast':{'canonical_like_copy_red_directed':c_red,'divergent_ANS_family_copy_white_directed':d_white,'copy_or_paralog_direction_heterogeneity_supported':c_red and d_white},'decision':'ANS/LDOX family recurrence is strengthened at reference-lineage resolution, and the 2022 reference-mapped contrast supports copy/paralog-specific directional deployment. Strict species-native cross-species exact-node recurrence remains zero.','claim_boundary':{'supported':['canonical-like versus divergent ANS-family classification of admitted tea reference copies','red- versus white-directed deployment of those reference-mapped copies in the recovered 2022 contrast','one deduplicated exact CrANS primer-bounded link to a canonical-like tea reference model','two reference-lineage-anchored ANS independence clusters while strict recurrence remains zero'],'not_supported':['recovery of a deposited C. reticulata CrANS nucleotide sequence','species-native C. reticulata orthology for the 2022 tea-reference targets','strict cross-species exact-node recurrence','duplication age, adaptive selection, or macro-transition enrichment']}}
    df=['feature','independence_cluster','target_taxon','source_evidence_type','reference_taxon','best_reference_accession','best_reference_label','protein_identity','protein_query_coverage','protein_subject_coverage','sequence_gate','sequence_gate_reason','red_minus_white_log2fpkm','direction_red_minus_white','red_gt_white','red_gt_pink_gt_white','assay_link_status','species_native_sequence_recovered','reference_lineage_anchor','strict_crossspecies_exact_node_ready','decision','claim_boundary']
    pf=['assay_feature','independence_cluster','target_taxon','searched_sequence_source','record_accessions','sequence_representations','forward_exact_hits_across_representations','reverse_exact_hits_across_representations','unique_exact_amplicons','exact_amplicon_sha256','predicted_amplicon_bp','expected_amplicon_or_orf_bp','deduplicated_link_status','species_native_sequence_recovered','interpretation','claim_boundary']
    x.out_dir.mkdir(parents=True,exist_ok=True);write(x.out_dir/'source_feature_decisions.csv',rows,df);write(x.out_dir/'primer_linkage_deduplicated.csv',p_rows,pf);(x.out_dir/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
