import io
import itertools
import sys
import unittest
from pathlib import Path
import numpy as np
from Bio import Phylo
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from analyze_hydrangea_mk_v0_2 import BinaryMk, transition

class TestMk(unittest.TestCase):
    def setUp(self):
        self.tree = Phylo.read(io.StringIO('((a:0.1,b:0.2):0.3,c:0.4);'),'newick')
        self.states={'a':0,'b':1,'c':0}
        self.mk=BinaryMk(self.tree,self.states)
    def test_transition_matches_expm(self):
        from scipy.linalg import expm
        for a,b,t in ((.3,.8,.2),(5,1,2),(.01,4,0)):
            np.testing.assert_allclose(transition(a,b,t),expm(np.array([[-a,a],[b,-b]])*t),atol=1e-14)
    def test_pruning_matches_bruteforce(self):
        a,b=1.3,.8
        ans=0
        for root,inner in itertools.product(range(2),repeat=2):
            ans+=.5*transition(a,b,.3/.5)[root,inner]*transition(a,b,.1/.5)[inner,0]*transition(a,b,.2/.5)[inner,1]*transition(a,b,.4/.5)[root,0]
        self.assertAlmostEqual(self.mk.calculate(a,b),np.log(ans),12)
    def test_jump_occupancy_derivative_identity(self):
        a,b=1.3,.8
        _,d=self.mk.calculate(a,b,details=True)
        h=1e-5
        da=(self.mk.calculate(a*np.exp(h),b)-self.mk.calculate(a*np.exp(-h),b))/(2*h)
        db=(self.mk.calculate(a,b*np.exp(h))-self.mk.calculate(a,b*np.exp(-h)))/(2*h)
        self.assertAlmostEqual(da,d['expected_white_to_red']-a*d['expected_white_occupancy_substitutions']/self.mk.scale,8)
        self.assertAlmostEqual(db,d['expected_red_to_white']-b*d['expected_red_occupancy_substitutions']/self.mk.scale,8)
    def test_label_swap(self):
        other=BinaryMk(self.tree,{t:1-s for t,s in self.states.items()})
        self.assertAlmostEqual(self.mk.calculate(1.2,2.3),other.calculate(2.3,1.2),12)
    def test_missing_tip_fails(self):
        with self.assertRaises(ValueError):BinaryMk(self.tree,{'a':0,'b':1})
    def test_unobserved_state_fails(self):
        with self.assertRaises(ValueError):BinaryMk(self.tree,{'a':0,'b':0,'c':0})
    def test_invalid_branches_fail(self):
        tree=Phylo.read(io.StringIO('(a:-1,b:1);'),'newick')
        with self.assertRaises(ValueError):BinaryMk(tree,{'a':0,'b':1})
    def test_ER_same_rates_but_counts_need_not_match(self):
        _,d=self.mk.calculate(.8,.8,details=True)
        self.assertNotAlmostEqual(d['expected_white_to_red'],d['expected_red_to_white'],places=4)
    def test_fit_finite(self):
        r=self.mk.fit('ER')
        self.assertTrue(np.isfinite(r['log_likelihood']))
        self.assertAlmostEqual(r['rate_ratio_return_to_gain'],1)

if __name__=='__main__':unittest.main()
