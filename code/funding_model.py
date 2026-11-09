"""Phase11 scenario-conditioned liquid funding model. USDm, annual dates.
No random sampling, loans, external contributions, final NAV, or default recovery.
Calls occur BEFORE same-date distributions. All source inputs are frozen locally.
"""
import csv,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];H=14;EPS=1e-9
BASE_INV=[17.]*5+[0.]*10
BASE_FEE=[2.]*5+[1.]*5+[0.]*5
BASE_CALL=[a+b for a,b in zip(BASE_INV,BASE_FEE)]
def read_csv(path):
 with path.open() as f:return list(csv.DictReader(f))
def write(name,rows):
 with (R/'calculations'/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def bisect(f,lo,hi,n=90):
 if f(lo)*f(hi)>0:raise ValueError('Not bracketed')
 for _ in range(n):
  mid=(lo+hi)/2
  if f(mid)<0:lo=mid
  else:hi=mid
 return (lo+hi)/2

def fund(inv=None,fee=None,dist_delay=0,haircut=0,gross=None,first_tranche_delay=0):
 inv=BASE_INV[:] if inv is None else inv;fee=BASE_FEE[:] if fee is None else fee
 calls=[a+b for a,b in zip(inv,fee)]
 if gross is None:gross=GROSS
 gd=[0.]*15;gd[9+dist_delay+first_tranche_delay]+=.4*gross*(1-haircut);gd[10+dist_delay]+=.6*gross*(1-haircut)
 paid=received=oldcarry=0.;net=[];flow=[]
 for t in range(15):
  paid+=calls[t];received+=gd[t]
  carry=.2*max(received-paid,0);increment=carry-oldcarry
  if increment<-EPS:raise ValueError('No clawback contract not valid with calls after carry')
  net.append(gd[t]-increment);oldcarry=carry
  flow.append(dict(year=t,investment=inv[t],management_fee=fee[t],capital_call=calls[t],gross_distribution=gd[t],carry=increment,net_distribution=net[-1],net_cashflow=net[-1]-calls[t]))
 return calls,net,flow

def npv(rate,cs,ds):return sum((d-c)/(1+rate)**t for t,(c,d) in enumerate(zip(cs,ds)))
def irr(cs,ds):return bisect(lambda x:-npv(x,cs,ds),-.5,2.)
def solve_gross():
 return bisect(lambda g:npv(.1,*fund(gross=g)[:2]),100,1000)
GROSS=solve_gross()

def call_variant(kind):
 inv=BASE_INV[:];fee=BASE_FEE[:]
 if kind in ['early','late']:
  shift=-1 if kind=='early' else 1
  def move(xs):
   ys=[0.]*15
   for t,x in enumerate(xs):
    if x:ys[max(0,t+shift) if t else 0]+=x
   return ys
  inv,fee=move(inv),move(fee)
 elif kind=='tail':
  inv[7]+=inv[3];inv[3]=0;inv[8]+=inv[4];inv[4]=0
 return inv,fee

def cohorts(delay=0,haircut=0):
 """Two half-size commitments at0,4, total100, common horizon14."""
 c=[0.]*15;d=[0.]*15
 for start in [0,4]:
  cs,ds,_=fund(dist_delay=delay if start==0 else 0,haircut=haircut if start==0 else 0)
  for t in range(11+(delay if start==0 else 0)):
   if start+t<=14:c[start+t]+=.5*cs[t];d[start+t]+=.5*ds[t]
 return c,d

def path(shocks=None,constant=.08):
 p=[1.]+[1+constant]*14
 if shocks:
  normal=((1.08**14)/math.prod(1+r for r in shocks.values()))**(1/(14-len(shocks)))
  p=[1.]+[normal]*14
  for t,r in shocks.items():p[t]=1+r
 return p

def levels(mult):
 a=[1.]
 for m in mult[1:]:a.append(a[-1]*m)
 return a

def forecast_target(t,policy,forecast,remaining):
 years=1 if policy=='rolling1' else 2
 target=sum(forecast[t+1:min(t+years+1,15)])
 if policy=='hybrid':target+=.1*remaining
 return min(remaining,target)

def run_policy(c,d,p,s,policy,forecast=None,budget=100.,initial_reserve=None,slippage=0.):
 """s,p are gross annual multipliers, first dummy1. Forecast never actual shock schedule."""
 forecast=c if forecast is None else forecast;commit=sum(c);last=max(t for t,x in enumerate(c) if x>EPS)
 if policy=='public':cash=0.
 elif policy in ['full0','full3','full_variable']:cash=commit
 elif policy=='oracle':cash=sum(forecast[t]/1.03**t for t in range(15))
 elif policy=='static':cash=initial_reserve
 else:cash=c[0]+forecast_target(0,policy,forecast,commit-c[0])
 cash=min(budget,cash);equity=budget-cash;initial=cash;paid=0;ledger=[];failure=None;max_short=0.;minhead=float('inf');mincash=float('inf');mintarget=0
 cashrate=[1.]*15 if policy=='full0' else s
 for t in range(15):
  if t:cash*=cashrate[t];equity*=p[t]
  pre_cash,pre_equity=cash,equity;need=c[t];available=cash+equity*(1-slippage)
  if need>EPS:minhead=min(minhead,available-need)
  short=max(need-available,0)
  max_short=max(max_short,short)
  row=dict(year=t,reserve_before=pre_cash,public_before=pre_equity,capital_call=need,available_before_call=available,pre_call_headroom=available-need if need>EPS else '',net_distribution=d[t],call_sale_gross=0.,reserve_target=0.,target_shortfall=0.,reserve_after='',public_after='',status='OK')
  if short>EPS:
   failure=t;row.update(status='FUNDING_FAILURE',net_distribution=0.,funding_shortfall=short);ledger.append(row);break
  fromcash=min(cash,need);cash-=fromcash;left=need-fromcash;sale=left/(1-slippage);equity-=sale;paid+=need
  cash=max(cash,0.);equity=max(equity,0.);row['call_sale_gross']=sale
  if need>EPS:mincash=min(mincash,cash)
  # Only now do current receipts exist. They cannot finance current calls.
  equity+=d[t];remaining=max(commit-paid,0.)
  if remaining<EPS:equity+=cash;cash=0.
  elif policy in ['rolling1','rolling2','hybrid']:
   target=forecast_target(t,policy,forecast,remaining);total=cash+equity
   row['reserve_target']=target;row['target_shortfall']=max(target-total,0.);mintarget=max(mintarget,row['target_shortfall'])
   # Rebalance at observed end-of-date prices, no transaction charge except optional call-sale stress.
   cash=min(target,total);equity=total-cash
  row.update(reserve_after=cash,public_after=equity,funding_shortfall=0.);ledger.append(row)
 wealth=None if failure is not None else cash+equity
 return dict(feasible=failure is None,first_failure_year='' if failure is None else failure,max_observed_shortfall=max_short,min_pre_call_headroom=minhead,min_post_call_reserve=mincash,max_reserve_target_gap=mintarget,initial_reserve=initial,terminal_wealth='' if wealth is None else wealth,public_policy_wealth=budget*math.prod(p),wealth_difference='' if wealth is None else wealth-budget*math.prod(p)),ledger

def prefix_boundary(c,d,p):
 """Public-funded W >= max_t discounted calls through t minus receipts STRICTLY before t."""
 B=levels(p);req=0.;rows=[];critical=0;priornet=0.
 for t in range(15):
  due=priornet+c[t]/B[t]
  if due>req:req=due;critical=t
  rows.append(dict(year=t,public_level=B[t],discounted_prefix_requirement=due))
  priornet=due-d[t]/B[t]
 return req,critical,rows

def controls():
 c,d,_=fund();p=path();s=[1.]+[1.03]*14
 a,_=run_policy(c,d,p,s,'full0');b,_=run_policy(c,d,p,s,'full3')
 root=bisect(lambda y:run_policy(c,d,p,[1.]+[1+y]*14,'full_variable')[0]['terminal_wealth']-100*1.08**14,0,.08)
 expected=json.loads((R/'inputs/phase9_reconstruction_summary.json').read_text())
 assert abs(root-float(expected['reserve_break_even_decimal']))<1e-12
 olds=read_csv(R/'inputs/phase9_independent_policy_results.csv')
 for name,r,rate in [('zero',a,'0.000'),('three',b,'0.030')]:
  old=next(x for x in olds if x['case_id']==f'T10-full_commitment_reserve-s{rate}-b0.080');assert abs(r['terminal_wealth']-float(old['terminal_wealth']))<1e-9
 return dict(liquid_wealth=100*1.08**14,full0_wealth=a['terminal_wealth'],full3_wealth=b['terminal_wealth'],reserve_break_even=root,gross_proceeds=GROSS,net_fund_irr=irr(c,d),status='MATCH_PHASE9_CONTROLS_NOT_NEW_FINDINGS')

POLICIES=['full0','full3','oracle','rolling1','rolling2','public','hybrid']

def main():
 c,d,flows=fund();write('baseline_fund_schedule.csv',flows)
 con=controls();(R/'checks/control_verification.json').write_text(json.dumps(con,indent=2))
 paths={'constant8':path(),'early40_t2':path({2:-.4}),'late40_t12':path({12:-.4}),'precall40_t4':path({4:-.4}),'prolonged20':path({1:-.2,2:-.2,3:-.2}),'late_recovery':path({1:-.1,2:-.1,3:-.1,4:-.1}),'moderate20_t2':path({2:-.2}),'joint20_t8':path({8:-.2}),'constant0':path(constant=0),'constant6':path(constant=.06),'constant10':path(constant=.10)}
 # Hybrid historical scenarios are not VC backtests.
 annual=read_csv(R/'inputs/french_annual_2000_2023.csv')
 cashpaths={}
 for start in [2000,2004,2010]:
  rs=[x for x in annual if start<=int(x['year'])<start+14];assert len(rs)==14
  name=f'HYBRID_US_{start}_{start+13}';paths[name]=[1.]+[1+float(x['market_total_return']) for x in rs];cashpaths[name]=[1.]+[1+float(x['bill_proxy_return']) for x in rs]
 write('public_paths.csv',[dict(path=k,year=t,gross_multiplier=x,return_decimal=x-1,public_level=levels(v)[t],evidence_class='observed_public_hypothetical_private_hybrid' if k.startswith('HYBRID') else 'constructed') for k,v in paths.items() for t,x in enumerate(v)])
 res=[];led=[];prefix=[]
 variants={}
 for kind in ['base','early','late','tail']:
  inv,fee=call_variant(kind);variants[kind]=fund(inv,fee)[:2]
 variants['delay2']=fund(dist_delay=2)[:2];variants['first_tranche_delay2']=fund(first_tranche_delay=2)[:2];variants['delay2_haircut25']=fund(dist_delay=2,haircut=.25)[:2]
 variants['two_cohort_base']=cohorts();variants['two_cohort_delay2']=cohorts(delay=2);variants['two_cohort_delay2_haircut25']=cohorts(delay=2,haircut=.25)
 for pn,p in paths.items():
  for vn,(cs,ds) in variants.items():
   forecast=variants['two_cohort_base'][0] if vn.startswith('two_cohort') else c
   req,crit,pr=prefix_boundary(cs,ds,p);prefix.append(dict(path=pn,cashflow_variant=vn,required_initial_public_capital=req,critical_year=crit,max_commitment_fraction_of100=min(1.,100/req)))
   for policy in POLICIES:
    # In historical hybrids3% policies use observed rolling-bill proxy instead, clearly labelled.
    s=cashpaths.get(pn,[1.]+[1.03]*14)
    r,ls=run_policy(cs,ds,p,s,policy,forecast)
    case=f'{pn}/{vn}/{policy}';r=dict(case_id=case,path=pn,cashflow_variant=vn,policy=policy,reserve_input='observed_RF_proxy' if pn in cashpaths and policy!='full0' else 'zero' if policy=='full0' else 'assumed3pct',fund_net_irr=irr(cs,ds),**r)
    # Control puts each call into public assets, preserving funding-wallet path and receipts NEVER fund calls in this comparator.
    B=levels(p);callfv=sum(cs[t]*B[-1]/B[t] for t in range(15));distfv=sum(ds[t]*B[-1]/B[t] for t in range(15))
    r['fund_relative_terminal_benefit']=distfv-callfv
    r['reserve_opportunity_cost']='' if not r['feasible'] else 100*B[-1]-(r['terminal_wealth']-distfv+callfv)
    # Independent exposure-cost identity: foregone public return on actual beginning reserve balances.
    cost=0.
    for t in range(1,len(ls)):
     reserve_before_interval=ls[t-1]['reserve_after']
     cost+=reserve_before_interval*(p[t]-(1. if policy=='full0' else s[t]))*B[-1]/B[t]
    r['reserve_cost_from_exposures']='' if not r['feasible'] else cost
    if r['feasible']:assert abs(cost-r['reserve_opportunity_cost'])<1e-8,(case,cost,r)
    res.append(r);led.extend(dict(case_id=case,**x) for x in ls)
 write('policy_results.csv',res);write('annual_ledgers.csv',led);write('public_prefix_boundaries.csv',prefix)
 write('private_schedules.csv',[dict(variant=v,year=t,capital_call=cs[t],net_distribution=ds[t]) for v,(cs,ds) in variants.items() for t in range(15)])
 # Commitment size is essential:100% of initial wealth is not a representative institutional allocation.
 size=[]
 for pn in ['constant8','early40_t2','prolonged20','joint20_t8']:
  for vn in ['base','two_cohort_base','two_cohort_delay2_haircut25']:
   for frac in [.25,.5,.75,1.]:
    cs,ds=variants[vn];cs=[frac*x for x in cs];ds=[frac*x for x in ds];fc=variants['two_cohort_base'][0] if vn.startswith('two_cohort') else c
    for policy in POLICIES:
     r,_=run_policy(cs,ds,paths[pn],[1.]+[1.03]*14,policy,[frac*x for x in fc]);size.append(dict(path=pn,variant=vn,commitment_fraction=frac,policy=policy,**r))
 write('commitment_size_controls.csv',size)
 reserve=[]
 for rate in [0,.01,.02,.03,.05]:
  r,_=run_policy(c,d,path(),[1.]+[1+rate]*14,'full_variable');reserve.append(dict(rate_pattern=f'constant_{rate}',**r))
 for label,rates in json.loads((R/'inputs/analysis_design.json').read_text())['reserve_rate_stresses'].items():
  r,_=run_policy(c,d,path(),[1.]+[1+x for x in rates],'full_variable');reserve.append(dict(rate_pattern=label,**r))
 write('reserve_rate_sensitivity.csv',reserve)
 # Feasibility boundaries, not confidence bounds or optimisers. Smallest static initial reserve on declared1m grid;0.01m refinement.
 front=[]
 for pn in ['constant8','moderate20_t2','early40_t2','precall40_t4','prolonged20','late_recovery','late40_t12']:
  p=paths[pn]
  for vn in ['base','early','late']:
   cs,ds=variants[vn]
   feasible=[]
   for amount in range(101):
    r,_=run_policy(cs,ds,p,[1.]+[1.03]*14,'static',initial_reserve=amount)
    front.append(dict(path=pn,variant=vn,initial_static_reserve=amount,**r))
 write('static_reserve_frontier_grid.csv',front)
 depth=[]
 for shock in [-.1,-.2,-.3,-.4]:
  pp=path({2:shock});req,crit,_=prefix_boundary(c,d,pp)
  r,_=run_policy(c,d,pp,[1.]+[1.03]*14,'public');depth.append(dict(shock_at_t2=shock,public_CAGR=math.prod(pp)**(1/14)-1,required_initial_capital=req,max_commitment_fraction=min(1,100/req),critical_year=crit,**r))
 write('drawdown_depth_controls.csv',depth)
 # Same public terminal factor and all feasible policies: compare sequence, not endpoints alone.
 print(json.dumps(dict(controls=con,policy_cases=len(res),ledger_rows=len(led),frontier_rows=len(front),size_controls=len(size)),indent=2))
if __name__=='__main__':main()
