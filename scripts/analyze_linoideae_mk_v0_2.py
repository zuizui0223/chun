#!/usr/bin/env python3
"""Source-set aware conditional colour history. No fixed-white root or dated rates."""
from __future__ import annotations
import argparse,copy,csv,io,json,math,hashlib
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
from Bio import Phylo
from scipy.linalg import expm
from scipy.optimize import minimize_scalar,brentq
from scipy.stats import chi2
from analyze_hydrangea_mk_v0_2 import BinaryMk
SEED=20260907
COLORS=('WHITE','YELLOW','BLUE','PURPLE','RED','PINK')

def load_snapshot(path):
    path=Path(path);data=json.loads(path.read_text())
    if 'rows' in data and 'trees' in data:return data
    for name,expected in data['frozen_files_sha256'].items():
        p=path.parent/name
        if not p.resolve().is_relative_to(path.parent.resolve()):raise ValueError('unsafe input path')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=expected:raise ValueError('input checksum mismatch: '+name)
    rows=list(csv.DictReader((path.parent/data['source_rows_path']).open()))
    if len(rows)!=121 or len({r['tip_id'] for r in rows})!=121:raise ValueError('source row identity/count failure')
    for r in rows:
        for key in ('figure2_states','figureS5_states'):
            r[key]=r[key].split('|')
            if not set(r[key])<=set(COLORS):raise ValueError('unknown source colour')
    data['rows']=rows
    data['trees']={tag:(path.parent/name).read_text() for tag,name in data['tree_files'].items()}
    return data

class StateTree:
    def __init__(self,tree,states,k):
        self.tree=tree;self.nodes=list(tree.find_clades(order='postorder'));self.n=len(self.nodes)
        self.index={id(n):i for i,n in enumerate(self.nodes)}
        self.children=[[self.index[id(c)] for c in n.clades] for n in self.nodes]
        tips=tree.get_terminals();names=[n.name for n in tips]
        if len(set(names))!=len(names) or set(names)!=set(states):raise ValueError('tree and source state sets must match one-to-one')
        if any(not v or not set(v)<=set(range(k)) for v in states.values()):raise ValueError('invalid or empty allowed-state set')
        lengths=[n.branch_length for n in self.nodes[:-1]]
        if any(t is None or not np.isfinite(t) or t<0 for t in lengths):raise ValueError('finite nonnegative branches required')
        self.scale=max(tree.depths().values())
        if self.scale<=0:raise ValueError('zero tree depth')
        self.t=np.array([(n.branch_length or 0)/self.scale for n in self.nodes]);self.t[-1]=0
        self.leaves={self.index[id(n)]:tuple(sorted(states[n.name])) for n in tips};self.k=k
        self.emissions=np.ones((self.n,k))
        for i,allowed in self.leaves.items():self.emissions[i]=[float(j in allowed) for j in range(k)]
    def pruning(self,p,pi):
        d=self.emissions.copy();msg=np.ones_like(d);log_scale=0.
        for i in range(self.n):
            if self.children[i]:
                for c in self.children[i]:d[i]*=msg[c]
                z=d[i].sum()
                if z<=0:return -np.inf,None,None,None
                d[i]/=z;log_scale+=np.log(z)
            msg[i]=p[i]@d[i]
        post=pi*d[-1];z=post.sum()
        if z<=0:return -np.inf,None,None,None
        return float(np.log(z)+log_scale),post/z,d,msg

class AmbiguousBinaryMk(StateTree):
    def __init__(self,tree,states):
        super().__init__(tree,states,2)
        if not any(set(s)=={0} for s in states.values()) or not any(set(s)=={1} for s in states.values()):raise ValueError('at least one definite observation of each binary state is required')
    def calculate(self,a,b,prior='equal',details=False):
        if a<=0 or b<=0 or not np.isfinite(a+b) or prior not in ('equal','stationary'):raise ValueError('positive finite rates and supported prior required')
        s=a+b;off=-np.expm1(-s*self.t);p=np.empty((self.n,2,2))
        p[:,0,0]=1-a/s*off;p[:,0,1]=a/s*off;p[:,1,0]=b/s*off;p[:,1,1]=1-b/s*off
        pi=np.array([.5,.5]) if prior=='equal' else np.array([b/s,a/s])
        ll,post,d,msg=self.pruning(p,pi)
        if not details:return ll
        if post is None:return ll,None
        outside=np.zeros_like(d);outside[-1]=pi;q=np.array([[-a,a],[b,-b]]);blocks=[]
        for i,j in ((0,1),(1,0),(0,0),(1,1)):
            v=np.zeros((2,2));v[i,j]=q[i,j] if i!=j else 1.;block=np.zeros((4,4));block[:2,:2]=block[2:,2:]=q;block[:2,2:]=v;blocks.append(block)
        totals=np.zeros(4)
        for i in range(self.n-1,-1,-1):
            for c in self.children[i]:
                u=outside[i].copy()
                for sib in self.children[i]:
                    if sib!=c:u*=msg[sib]
                u/=u.sum();denom=u@p[c]@d[c]
                for k,block in enumerate(blocks):totals[k]+=(u@expm(block*self.t[c])[:2,2:]@d[c])/denom
                outside[c]=u@p[c];outside[c]/=outside[c].sum()
        if not np.isclose(totals[2:].sum(),self.t.sum(),rtol=1e-6,atol=1e-7):raise ArithmeticError('occupancy identity failed')
        # Internal names match the verified binary optimizer; public names are relabelled in fit.
        return ll,dict(root_probability_white=float(post[0]),expected_white_to_red=float(totals[0]),expected_red_to_white=float(totals[1]),expected_white_occupancy_substitutions=float(totals[2]*self.scale),expected_red_occupancy_substitutions=float(totals[3]*self.scale),histories_conditioned_on='fitted_Q_and_this_tree_no_parameter_posterior')
    def fit(self,model='ER',prior='equal',detailed=True):
        r=BinaryMk.fit(self,model,prior,detailed)
        r={k.replace('red','nonwhite'):v for k,v in r.items()}
        r['rate_units']='per_sequence_substitution_per_site_NOT_per_year'
        a=r['q_white_to_nonwhite']*self.scale;b=r['q_nonwhite_to_white']*self.scale
        r['rate_times_1000_delta_logL']=self.calculate(a*1000,b*1000,prior)-r['log_likelihood']
        r['high_rate_plateau']=bool(abs(r['rate_times_1000_delta_logL'])<1e-6)
        r['ambiguous_binary_tips']=sum(len(v)==2 for v in self.leaves.values())
        r['inference_status']='BOUNDARY_OR_RATE_PLATEAU_DIAGNOSTIC_ONLY' if r['optimization_bound_hit'] or r['high_rate_plateau'] else 'NUMERICAL_INTERIOR_CONDITIONAL_FIT'
        return r

def profile(mk,fit):
    if fit['model']!='ARD':raise ValueError('profile requires ARD fit')
    if fit.get('optimization_bound_hit') or fit.get('high_rate_plateau'):raise ValueError('regular profile inference requires an interior, identifiable rate fit')
    prior=fit['root_prior'];best=fit['log_likelihood'];centre=math.log(fit['rate_ratio_return_to_gain']);cut=best-chi2.ppf(.95,1)/2
    cache={}
    def ll_at(r):
        r=float(r)
        if r in cache:return cache[r]
        low=-12+abs(r)/2;high=12-abs(r)/2
        def obj(u):return -mk.calculate(math.exp(u-r/2),math.exp(u+r/2),prior)
        grid=np.linspace(low,high,25);vals=[obj(u) for u in grid];j=int(np.argmin(vals));lo=grid[max(0,j-1)];hi=grid[min(len(grid)-1,j+1)]
        opt=minimize_scalar(obj,bounds=(lo,hi),method='bounded',options={'xatol':1e-7})
        val=-min(float(opt.fun),min(vals))
        if val>best+1e-5:raise ArithmeticError('profile improves on purported maximum; optimizer audit required')
        cache[r]=val;return val
    out={'conditioning':'fixed_tree_source_set_coding_equal_root_prior_asymptotic_profile','LR_p_equal_rates':float(chi2.sf(max(0,2*(best-ll_at(0))),1))}
    for label,end in [('low',-10.),('high',10.)]:
        grid=np.linspace(centre,end,35);bracket=None;prev=centre
        for v in grid[1:]:
            if ll_at(v)<cut:bracket=(prev,float(v));break
            prev=float(v)
        out[label]=math.exp(brentq(lambda x:ll_at(x)-cut,*sorted(bracket),xtol=1e-6)) if bracket else None
        out[label+'_search_ratio_limit']=math.exp(end)
    out['profile_points']=[{'log_ratio':r,'logL':v} for r,v in sorted(cache.items())]
    return out

def fit_six_er(tree,states):
    obj=StateTree(tree,states,6)
    def calc(x,details=False):
        rate=math.exp(float(x));e=np.exp(-6*rate*obj.t);p=np.broadcast_to(((1-e)/6)[:,None,None],(obj.n,6,6)).copy()
        for j in range(6):p[:,j,j]+=e
        ll,post,_,_=obj.pruning(p,np.ones(6)/6)
        return (ll,post) if details else -ll
    grid=np.linspace(-12,12,49);vals=[calc(x) for x in grid];j=int(np.argmin(vals))
    opt=minimize_scalar(calc,bounds=(grid[max(0,j-1)],grid[min(48,j+1)]]),method='bounded',options={'xatol':1e-8})
    ll,post=calc(opt.x,True)
    return {'model':'SIX_STATE_ER','log_likelihood':ll,'AIC':2-2*ll,'rate_per_substitution':math.exp(float(opt.x))/obj.scale,'root_probabilities':dict(zip(COLORS,map(float,post))),'root_prior':'equal_six_states','optimization_bound_hit':bool(abs(opt.x)>11.99),'ambiguous_tips':sum(len(s)>1 for s in states.values()),'claim_boundary':'ER-only observation-space sensitivity; not a full identifiable 30-rate ARD model'}

def permutation_indices(rng,nt,groups=None):
    if groups is None:return rng.permutation(nt)
    result=np.arange(nt)
    for members in groups:result[members]=rng.permutation(members)
    return result

def parsimony_scores(tree,tip_sets,k,permutations=9999,seed=SEED,conditional_white=False):
    obj=StateTree(tree,tip_sets,k);leafids=list(obj.leaves);nt=len(leafids)
    patterns=np.array([[0 if j in obj.leaves[i] else 10000 for j in range(k)] for i in leafids],dtype=np.int16)
    rng=np.random.default_rng(seed);scores=[];groups=None
    if conditional_white:
        if k!=6:raise ValueError('conditional hue test requires the six-colour alphabet')
        by_class=defaultdict(list)
        for pos,i in enumerate(leafids):
            a=set(obj.leaves[i]);by_class[(0 in a,bool(a-{0}))].append(pos)
        groups=[np.asarray(v,dtype=int) for v in by_class.values()]
    for start in range(0,permutations+1,500):
        n=min(500,permutations+1-start);indices=np.array([np.arange(nt) if start+j==0 else permutation_indices(rng,nt,groups) for j in range(n)])
        d=np.zeros((obj.n,n,k),dtype=np.int16)
        for pos,i in enumerate(leafids):d[i]=patterns[indices[:,pos]]
        for i in range(obj.n):
            for c in obj.children[i]:d[i]+=np.minimum(d[c],d[c].min(axis=1)[:,None]+1)
        scores.extend(d[-1].min(axis=1).tolist())
    observed=scores[0];null=np.asarray(scores[1:]);p=(1+int((null<=observed).sum()))/(len(null)+1)
    return {'observed_minimum_changes':observed,'null_mean':float(null.mean()),'null_quantiles':np.quantile(null,[0,.025,.5,.975,1]).tolist(),'observed_over_null_mean':observed/float(null.mean()) if null.mean() else None,'lower_tail_p':p,'permutations':len(null),'seed':seed,'n_tips':nt,'null':('allowed-state vectors exchanged only within fixed WHITE/NONWHITE/ambiguous classes; every tip retains its binary white-status' if conditional_white else 'whole allowed-state vectors exchanged among one-source-binomial tips; uncertainty counts and colour frequencies preserved'),'conditional_on_white_status':conditional_white,'not_independent_origins':True}

def subset(tree,allowed):
    t=copy.deepcopy(tree)
    # Keep root through unknown tips for modelling; this helper is for balanced sampling only.
    for n in list(t.get_terminals()):
        if n.name not in allowed:t.prune(n)
    t.root.branch_length=0.;return t

def rooted_ingroup(text):
    t=Phylo.read(io.StringIO(text),'newick');names=[n.name for n in t.get_terminals()]
    if names.count('LINO001')!=1:raise ValueError('explicit source outgroup missing or duplicated')
    t.root_with_outgroup('LINO001');allowed=set(names)-{'LINO001'};m=t.common_ancestor(sorted(allowed))
    if set(n.name for n in m.get_terminals())!=allowed:raise ValueError('ingroup rooting failed')
    t.prune('LINO001');t.root.branch_length=0.;return t

def run(snapshot,out,balanced=10,permutations=9999):
    data=load_snapshot(snapshot);rows=data['rows'];out=Path(out);out.mkdir(parents=True,exist_ok=True)
    lookup={r['tip_id']:r for r in rows};fits=[];six=[];profiles=[];signals=[];balancedfits=[]
    state_sets={policy:{r['tip_id']:set((r['figure2_states'] if policy=='FIGURE2' else r['figureS5_states']) if policy!='UNION' else r['figure2_states']+r['figureS5_states']) for r in rows} for policy in ('FIGURE2','FIGURES5','UNION')}
    for tag,text in data['trees'].items():
        t=rooted_ingroup(text);tipnames={n.name for n in t.get_terminals()}
        if not tipnames<=set(lookup):raise ValueError('unmapped tree observations')
        groups=defaultdict(list)
        for n in sorted(tipnames):groups[' '.join(lookup[n]['source_taxon'].split()[:2])].append(n)
        rng=np.random.default_rng(SEED);draws=[sorted(str(rng.choice(groups[g])) for g in sorted(groups)) for _ in range(balanced)]
        for policy,sets in state_sets.items():
            binary={n:{0 if c=='WHITE' else 1 for c in sets[n]} for n in tipnames}
            mult={n:{COLORS.index(c) for c in sets[n]} for n in tipnames}
            mk=AmbiguousBinaryMk(t,binary)
            for prior in ('equal','stationary'):
                for model in ('ER','ARD'):
                    r=mk.fit(model,prior);r.update(alignment=tag,coding=policy);fits.append(r)
                    print(json.dumps({k:v for k,v in r.items() if k not in ('histories_conditioned_on',)}),flush=True)
                    if model=='ARD' and prior=='equal' and not r['high_rate_plateau'] and not r['optimization_bound_hit']:
                        pr=profile(mk,r);pr.update(alignment=tag,coding=policy);profiles.append(pr)
            er6=fit_six_er(t,mult);er6.update(alignment=tag,coding=policy);six.append(er6)
            for draw,chosen in enumerate(draws):
                sub=subset(t,set(chosen));sub_binary={n:binary[n] for n in chosen};bmk=AmbiguousBinaryMk(sub,sub_binary)
                for model in ('ER','ARD'):
                    r=bmk.fit(model,'equal',False);r.update(alignment=tag,coding=policy,draw=draw,chosen=chosen);balancedfits.append(r)
                # First three deterministic taxon-balanced draws assess repeatability of signal.
                if draw<3:
                    for mode,k,states in [('WHITE_NONWHITE',2,sub_binary),('SIX_COLOURS',6,{n:mult[n] for n in chosen})]:
                        sig=parsimony_scores(sub,states,k,permutations,SEED);sig.update(alignment=tag,coding=policy,draw=draw,state_space=mode);signals.append(sig)
    results={'primary_fits':fits,'conditional_profiles':profiles,'six_state_ER':six,'taxon_balanced_fits':balancedfits,'phylogenetic_signal':signals,'balanced_draws_per_coding':balanced,'seed':SEED,'status':'EXECUTED_CONDITIONAL_SOURCE_SET_REANALYSIS','claim_boundary':'Two alignment treatments and three source codings are ONE radiation. Rates per sequence substitution, not years. White ancestor never imposed. Source multi-colour sets are uncertainty, not proven natural polymorphism.','paper1_science_changed':False}
    (out/'analysis_results.json').write_text(json.dumps(results,indent=2)+'\n')
    return results
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--balanced',type=int,default=10);ap.add_argument('--permutations',type=int,default=9999);a=ap.parse_args();run(a.snapshot,a.out,a.balanced,a.permutations)
