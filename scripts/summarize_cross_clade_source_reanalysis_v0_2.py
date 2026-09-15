#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,json
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--registry',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
 with a.registry.open(newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
 ids={r['system_id'] for r in rows}
 expected={'HYDRANGEA_CORNIDIA','LINOIDEAE','ANGRAECINAE','EPIMEDIUM_DIPHYLLON','MIMULUS_CHILEAN'}
 if ids!=expected:raise SystemExit(f'registry systems drift: {ids}')
 executed=[r for r in rows if r['analysis_status']=='SOURCE_TO_TREE_EXECUTED' and r['common_binary_estimator']=='YES']
 if {r['system_id'] for r in executed}!={'HYDRANGEA_CORNIDIA','LINOIDEAE'}:raise SystemExit('current two-radiation common-estimator closure drift')
 if any(r['directional_asymmetry_supported']!='NO' for r in executed):raise SystemExit('no current reanalysed radiation passes the frozen supported-direction gate')
 h=next(r for r in rows if r['system_id']=='HYDRANGEA_CORNIDIA');l=next(r for r in rows if r['system_id']=='LINOIDEAE');ang=next(r for r in rows if r['system_id']=='ANGRAECINAE')
 if h['point_direction']==l['point_direction']:raise SystemExit('point-direction contrast unexpectedly disappeared')
 if ang['analysis_status']!='SOURCE_TRAITS_EXECUTED_TREE_MK_PENDING':raise SystemExit('Angraecinae gate changed; update v0.2 instead of silently advancing')
 out={
  'version':'v0.2',
  'common_estimator_source_to_tree_radiations':len(executed),
  'common_estimator_systems':[r['system_id'] for r in executed],
  'supported_directional_asymmetry_systems':sum(r['directional_asymmetry_supported']=='YES' for r in executed),
  'hydrangea_linoideae_point_directions_opposite':True,
  'universal_white_direction_current_status':'NOT_SUPPORTED',
  'pooled_common_rate_model_ready':False,
  'pooled_gate_required_radiations':3,
  'third_radiation_gate':'ANGRAECINAE_TREE_TO_ORGAN_MK_PENDING',
  'finer_state_positive_results':{
   'LINOIDEAE':'HUE_ORGANIZATION_CONDITIONAL_ON_WHITE_STATUS',
   'EPIMEDIUM_DIPHYLLON':'JOINT_ORGAN_STATE_NONREDUNDANCY',
   'ANGRAECINAE':'SOURCE_LEVEL_ORGAN_DISCORDANCE_46_OF_170_FULLY_BINARY_ROWS'
  },
  'display_scalarization_failure_replicated_systems':['EPIMEDIUM_DIPHYLLON','ANGRAECINAE'],
  'retained_candidate_rule':'ANCESTRAL_OR_DISPLAY_STATE_CONSTRAINS_ACCESSIBLE_TRANSITION_ARCHITECTURE_WITHOUT_FIXING_ONE_UNIVERSAL_DIRECTION; INFORMATIVE_STRUCTURE_CAN_RESIDE_AT FINER HUE, ORGAN, OR FUNCTIONAL-MODULE LEVELS',
  'claim_boundary':'Two radiations currently have common source-to-tree binary reanalysis. Angraecinae has source-level organ evidence but is not counted as the third Mk radiation until its tree/model gate closes. No pooled white-ancestry effect is estimated.'
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
