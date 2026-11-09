"""Reproduce only the approved carousel cases; no new model or scenarios."""
from pathlib import Path
import csv,json,math
import funding_model as model
R=Path(__file__).resolve().parents[1]
def rows(p):
 with (R/p).open() as f:return list(csv.DictReader(f))
def save(name,data):
 with (R/'results'/name).open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
def main():
 (R/'results').mkdir(exist_ok=True)
 paths={}
 for r in rows('data/constructed_public_paths.csv'):paths.setdefault(r['path'],[]).append((int(r['year']),float(r['gross_multiplier'])))
 paths={k:[x for t,x in sorted(v)] for k,v in paths.items()}
 c,d,schedule=model.fund();frozen=rows('data/baseline_fund_schedule.csv')
 for x,y in zip(schedule,frozen):
  for col in ['investment','management_fee','capital_call','gross_distribution','carry','net_distribution']:assert abs(x[col]-float(y[col]))<1e-10
 assert abs(model.npv(.1,c,d))<1e-10
 out=[];ledgers=[]
 for x in rows('expected/policy_results.csv'):
  p=paths[x['path']];result,ls=model.run_policy(c,d,p,[1]+[1.03]*14,x['policy'],c)
  assert result['feasible']==(x['feasible']=='True')
  if result['feasible']:assert abs(result['terminal_wealth']-float(x['terminal_wealth']))<1e-9
  else:assert result['terminal_wealth']=='' and result['first_failure_year']==int(x['first_failure_year'])
  assert abs(result['max_observed_shortfall']-float(x['max_observed_shortfall']))<1e-10
  out.append(dict(case_id=x['case_id'],**result));ledgers.extend(dict(case_id=x['case_id'],**l) for l in ls)
 half,_=model.run_policy([v*.5 for v in c],[v*.5 for v in d],paths['early40_t2'],[1]+[1.03]*14,'public',[v*.5 for v in c])
 expected=rows('expected/half_commitment.csv')[0];assert half['feasible'] and abs(half['terminal_wealth']-float(expected['terminal_wealth']))<1e-9
 # Independent discounted-prefix calculation; future and same-date receipts excluded.
 B=[1.]
 for f in paths['early40_t2'][1:]:B.append(B[-1]*f)
 requirement=max(sum(c[u]/B[u] for u in range(t+1))-sum(d[u]/B[u] for u in range(t)) for t in range(15))
 original=rows('expected/prefix_boundary.csv')[0];assert abs(requirement-float(original['required_initial_public_capital']))<1e-10
 assert sorted(paths['early40_t2'])==sorted(paths['late40_t12'])
 assert abs(math.prod(paths['early40_t2'])**(1/14)-1-.08)<1e-12
 save('policy_results.csv',out);save('annual_ledgers.csv',ledgers)
 summary=dict(status='PASS',scope='Original approved cases only; no new scenarios',gross_proceeds=model.GROSS,fund_net_irr=model.irr(c,d),total_calls=sum(c),minimum_starting_budget=requirement,half_commitment_survives=half['feasible'],same_return_observations_reordered=True,publication_evidence='Hypothetical original LVCS calculations; not institutional default frequencies')
 (R/'results/verification.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
