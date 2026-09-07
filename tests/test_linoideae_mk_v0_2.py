import copy,io,itertools,sys,unittest,tempfile,shutil
from pathlib import Path
import numpy as np
from Bio import Phylo
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_hydrangea_mk_v0_2 import BinaryMk
from analyze_linoideae_mk_v0_2 import AmbiguousBinaryMk,StateTree,parsimony_scores,fit_six_er,permutation_indices,profile,load_snapshot

def tree():return Phylo.read(io.StringIO('((A:0.1,B:0.2):0.2,(C:0.3,D:0.4):0.2);'),'newick')
class Tests(unittest.TestCase):
 def test_matches_verified_engine(self):
  t=tree();raw={'A':0,'B':0,'C':1,'D':1};x=BinaryMk(t,raw);y=AmbiguousBinaryMk(t,{k:{v} for k,v in raw.items()})
  for prior in ('equal','stationary'):
   for a,b in ((.03,3),(3,.03),(1,1)):
    xl,xs=x.calculate(a,b,prior,True);yl,ys=y.calculate(a,b,prior,True)
    self.assertAlmostEqual(xl,yl,12)
    for key,v in xs.items():
     if isinstance(v,float):self.assertAlmostEqual(v,ys[key],10)
 def test_ambiguity_is_sum_not_imputation(self):
  raw={'A':{0},'B':{0,1},'C':{1},'D':{0,1}};m=AmbiguousBinaryMk(tree(),raw)
  for prior in ('equal','stationary'):
   total=sum(np.exp(BinaryMk(tree(),{'A':0,'B':b,'C':1,'D':d}).calculate(.2,.7,prior)) for b,d in itertools.product((0,1),repeat=2))
   self.assertAlmostEqual(m.calculate(.2,.7,prior),np.log(total),11)
 def test_ambiguity_occupancy(self):
  m=AmbiguousBinaryMk(tree(),{'A':{0},'B':{0,1},'C':{1},'D':{1}});ll,s=m.calculate(.8,.3,details=True)
  self.assertAlmostEqual(s['expected_white_occupancy_substitutions']+s['expected_red_occupancy_substitutions'],1.4,10)
 def test_symmetry(self):
  a={'A':{0},'B':{0,1},'C':{1},'D':{1}};b={t:{1-c for c in v} for t,v in a.items()}
  self.assertAlmostEqual(AmbiguousBinaryMk(tree(),a).calculate(.4,2),AmbiguousBinaryMk(tree(),b).calculate(2,.4),12)
 def test_missing_tip_rejected(self):
  with self.assertRaises(ValueError):AmbiguousBinaryMk(tree(),{'A':{0},'C':{1},'D':{1}})
 def test_single_definite_state_rejected(self):
  with self.assertRaises(ValueError):AmbiguousBinaryMk(tree(),{'A':{0,1},'B':{0,1},'C':{1},'D':{1}})
 def test_negative_branch_rejected(self):
  t=tree();t.get_terminals()[0].branch_length=-1
  with self.assertRaises(ValueError):AmbiguousBinaryMk(t,{'A':{0},'B':{0},'C':{1},'D':{1}})
 def test_empty_state_set_rejected(self):
  with self.assertRaises(ValueError):StateTree(tree(),{'A':set(),'B':{0},'C':{1},'D':{1}},2)
 def test_parsimony_known_topology(self):
  r=parsimony_scores(tree(),{'A':{0},'B':{0},'C':{1},'D':{1}},2,99)
  self.assertEqual(r['observed_minimum_changes'],1);self.assertGreaterEqual(r['lower_tail_p'],.01)
 def test_permutation_reproducible(self):
  states={'A':{0},'B':{0,1},'C':{1},'D':{1}}
  self.assertEqual(parsimony_scores(tree(),states,2,29,12),parsimony_scores(tree(),states,2,29,12))
 def test_six_state_probabilities(self):
  r=fit_six_er(tree(),{'A':{0},'B':{1,2},'C':{3},'D':{4,5}})
  self.assertAlmostEqual(sum(r['root_probabilities'].values()),1,12)
class ConditionalTests(unittest.TestCase):
 def test_conditional_permutation_preserves_all_white_masks(self):
  rng=np.random.default_rng(6);groups=[np.array([0,3]),np.array([1]),np.array([2,4,5])]
  masks=np.array([0,1,2,0,2,2])
  for i in range(100):
   perm=permutation_indices(rng,6,groups)
   self.assertEqual(sorted(perm.tolist()),list(range(6)))
   np.testing.assert_array_equal(masks,masks[perm])
 def test_binary_all_same_within_class_yields_conditional_p_one(self):
  r=parsimony_scores(tree(),{'A':{0},'B':{0},'C':{1},'D':{1}},6,99,12,True)
  self.assertEqual(r['lower_tail_p'],1)
 def test_boundary_profile_forbidden(self):
  with self.assertRaises(ValueError):profile(None,{'model':'ARD','optimization_bound_hit':True})
 def test_plateau_profile_forbidden(self):
  with self.assertRaises(ValueError):profile(None,{'model':'ARD','high_rate_plateau':True})
class FrozenInputTests(unittest.TestCase):
 def source(self):return Path(__file__).resolve().parents[1]/'data/linoideae_source_reanalysis_v0_2/source_manifest.json'
 def test_frozen_input_counts_and_hashes(self):
  d=load_snapshot(self.source());self.assertEqual(len(d['rows']),121);self.assertEqual(len(d['trees']),3)
 def test_mutated_input_fails(self):
  with tempfile.TemporaryDirectory() as tmp:
   dst=Path(tmp)/'data';shutil.copytree(self.source().parent,dst)
   with (dst/'terminal_sources.csv').open('a') as f:f.write('CORRUPTED\n')
   with self.assertRaises(ValueError):load_snapshot(dst/'source_manifest.json')
 def test_missing_input_fails(self):
  with self.assertRaises(FileNotFoundError):load_snapshot(self.source().parent/'missing.json')
if __name__=='__main__':unittest.main()
