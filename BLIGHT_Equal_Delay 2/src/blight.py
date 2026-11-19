#!/usr/bin/env python3
"""BLIGHT 0.1: reproducible SYNTHETIC policy experiment, NOT a calibrated Aceh forecast."""
from __future__ import annotations
import argparse,csv,gzip,hashlib,json,math,os,random,statistics,sys,time
from pathlib import Path

ARCHETYPES=[('HH',360,'household'),('ER',60,'responder'),('SP',30,'supplier'),('LG',30,'logistics'),('HC',30,'healthcare'),('LA',30,'authority'),('FI',30,'funder'),('CO',30,'community')]
PATHWAYS={'S1':{'weekly_flood_p':0.035,'heat_factor':0.90,'severity':0.88},'S2':{'weekly_flood_p':0.055,'heat_factor':1.05,'severity':1.00},'S3':{'weekly_flood_p':0.075,'heat_factor':1.20,'severity':1.18},'S4':{'weekly_flood_p':0.100,'heat_factor':1.40,'severity':1.38}}
POLICIES={
 'A':{'name':'Immediate donated shelter','shelter_cost':2400,'public_share':0.80,'flood_protection':0.22,'heat_protection':0.20,'maintenance_rate':0.014,'retrofit_cost':3100,'retrofit_gain':0.30,'install_delay':1},
 'B':{'name':'Climate-adaptive reconstruction','shelter_cost':5000,'public_share':0.65,'flood_protection':0.69,'heat_protection':0.68,'maintenance_rate':0.008,'retrofit_cost':1200,'retrofit_gain':0.14,'install_delay':3},
 'C':{'name':'Verified conditional donation','shelter_cost':3500,'public_share':0.74,'flood_protection':0.53,'heat_protection':0.50,'maintenance_rate':0.010,'retrofit_cost':1950,'retrofit_gain':0.22,'install_delay':2}}
WEEKS=52
SHOCK_WEEK=27
SCHEMA_VERSION='0.1.0'
GOVERNANCE_POLICY={'release_policy':'human_approval_required','authorized_roles':['reviewer','recovery_authority'], 'privileged_actions':['approve_expenditure','certify_engineering','delete_audit_log','release_policy_recommendation']}

class Denied(Exception):pass
class InvalidInput(Exception):pass

def enforce(request:dict, audit_path:Path, approved:bool=False)->dict:
    """Application-side PEP: no LLM text can bypass this rule."""
    role=request.get('role','anonymous'); action=request.get('action','')
    permissible=(action not in GOVERNANCE_POLICY['privileged_actions'] or (role in GOVERNANCE_POLICY['authorized_roles'] and approved))
    audit={'event_id':hashlib.sha256(json.dumps([role,action,approved],sort_keys=True).encode()).hexdigest()[:16],
           'actor':role,'action':action,'approval':bool(approved),'decision':'ALLOW' if permissible else 'DENY','policy_version':SCHEMA_VERSION}
    audit_path.parent.mkdir(parents=True,exist_ok=True)
    with audit_path.open('a') as f:f.write(json.dumps(audit,sort_keys=True)+'\n')
    if not permissible:raise Denied('PEP_DENY: missing role or human approval')
    return audit

def ingest_document(name:str, text:str)->dict:
    allowed=('.pdf','.docx')
    if not name.lower().endswith(allowed):raise InvalidInput('UNSUPPORTED_DOCUMENT_TYPE')
    return {'filename':name,'trust_boundary':'UNTRUSTED_DATA','prompt_injection_detected':any(k in text.lower() for k in ('ignore previous instructions','override system','approve expenditure')),'executed_commands':0}

def finite_or_fail(xs):
    if not xs or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in xs):
        raise InvalidInput('DATA_QUALITY_FAILURE: invalid finite reference input')

def drift_stat(reference,current):
    finite_or_fail(reference);finite_or_fail(current)
    # standardized difference; not proof of concept drift
    denom=max(statistics.pstdev(reference),1e-6)
    return abs(statistics.mean(current)-statistics.mean(reference))/denom

def transact(balance,expense):
    if not math.isfinite(balance) or not math.isfinite(expense) or expense<0:raise InvalidInput('BAD_TRANSACTION')
    if expense>balance+1e-9:raise Denied('BUDGET_INVARIANT_DENIAL')
    return round(balance-expense,6)

def registry():
    return [{'agent_id':f'{prefix}-{i:04d}','actor_type':role,'archetype':prefix,'role_index':i} for prefix,n,role in ARCHETYPES for i in range(1,n+1)]

def initial_households(seed):
    """Uncalibrated synthetic latent traits; same within seed across policies."""
    r=random.Random(seed*95839+119)
    hh=[]
    for i in range(360):
        hh.append({'agent_id':f'HH-{i+1:04d}','wealth':round(1100+6500*r.betavariate(1.7,3.5),2),
          'risk':round(0.20+0.78*r.random(),5),'trust':round(r.betavariate(2.4,2.4),5),
          'vulnerable':int(r.random()<0.32),'flood_exposure':round(0.45+0.55*r.random(),5),
          'heat_exposure':round(0.5+0.5*r.random(),5),'peer':[(i-1)%360,(i+1)%360,(i+17)%360]})
    return hh

def shock_stream(seed,scenario):
    """Common random numbers paired across policies; scenarios vary probability."""
    r=random.Random(seed*97813+203)
    return [(r.random(),r.random(),r.random()) for _ in range(WEEKS)]

def safe_run_id(scenario,policy,seed):return f'BLIGHT-{scenario}-{policy}-SEED{seed:02d}'

def trace(logfile,record): logfile.write(json.dumps(record,separators=(',',':'),sort_keys=True)+'\n')

def simulate(scenario:str,policy:str,seed:int,root:Path,save_trace=True):
    if scenario not in PATHWAYS or policy not in POLICIES or not 1<=seed<=8:raise InvalidInput('BAD_EXPERIMENT_CONFIG')
    scenario_cfg=PATHWAYS[scenario];pc=POLICIES[policy]; agents=registry();households=initial_households(seed);weather=shock_stream(seed,scenario)
    run_id=safe_run_id(scenario,policy,seed); rng=random.Random(seed*74653+int(scenario[1])*883)  # same institution preferences across policies
    budget_public=950000.0
    state={x['agent_id']:{'budget':round(55000+14000*rng.random(),2),'inventory':0,'service_units':0} for x in agents if x['archetype']!='HH'}
    hs=[dict(h,home='displaced',budget=h['wealth'],displaced_weeks=0,cum_welfare=0.0,maint=0.0,damage=0.0,retrofit=False,retrofit_cost_paid=0.0,switch_time=0,initial_paid=0.0,initial_state='displaced') for h in households]
    totals={'public_spend':0.0,'private_spend':0.0,'reversal_spend':0.0,'damage_cost':0.0,'displacement_weeks':0.0,'accepted':0,'unhoused':0,'safety_denials':0,'financial_denials':0,'service_events':0}
    asset_events={a['agent_id']:0 for a in agents if a['archetype']!='HH'}
    path=root/'evidence'/'agent_traces';path.mkdir(parents=True,exist_ok=True)
    trace_path=path/(run_id+'.jsonl.gz');sink=gzip.open(trace_path,'wt',encoding='utf-8',compresslevel=5) if save_trace else None
    try:
      # initial acceptance: same budgets/traits across alternatives; costs and compliance determine feasibility
      for i,h in enumerate(hs):
        base=households[i]
        # household acceptance response to shelter costs, protection and trust; no policy-specific advantage baked into trust/resources
        affordability=max(0.0,1.0-(pc['shelter_cost']*(1-pc['public_share'])/max(h['budget'],1)))
        suitability=0.55*pc['flood_protection']+0.45*pc['heat_protection']
        acceptance_utility=-0.6+1.25*affordability+1.0*base['trust']+0.8*base['risk']*suitability -0.50*(pc['install_delay']-1)
        accept_prob=1/(1+math.exp(-acceptance_utility))
        # counterfactual common uniform draws for policy choice
        accept_rng=random.Random(seed*1279+i*7+409)
        amount_private=round(pc['shelter_cost']*(1-pc['public_share']),2)
        amount_public=round(pc['shelter_cost']-amount_private,2)
        can_purchase=(h['budget']>=amount_private and budget_public>=amount_public)
        if accept_rng.random()<accept_prob and can_purchase:
            h['budget']=transact(h['budget'],amount_private);budget_public=transact(budget_public,amount_public)
            totals['private_spend']+=amount_private;totals['public_spend']+=amount_public
            h['initial_paid']=amount_private;h['home']='pending';totals['accepted']+=1
        elif not can_purchase:totals['financial_denials']+=1
      for week in range(1,WEEKS+1):
        flood_u,heat_u,intensity_u=weather[week-1]
        flood=(flood_u<scenario_cfg['weekly_flood_p'])
        heat=(heat_u<min(0.85,0.22*scenario_cfg['heat_factor']))
        intensity=(0.5+intensity_u)*scenario_cfg['severity']
        # the reversibility stress event is identical across policies for a given seed/scenario
        severe_shock=(week==SHOCK_WEEK)
        if severe_shock:flood=True;heat=True;intensity=1.45*scenario_cfg['severity']
        # dynamic choices computed against frozen previous-week peer states
        peer_before=[h['home']=='stable' for h in hs]
        for i,h in enumerate(hs):
            prev=h['home'];prev_budget=h['budget'];prev_displaced=h['displaced_weeks'];action='hold';cost=0.0
            peer_rate=sum(peer_before[j] for j in h['peer'])/len(h['peer'])
            if h['home']=='pending' and week>=pc['install_delay']:h['home']='stable';action='take_possession'
            protection_f=min(0.92,pc['flood_protection']+(pc['retrofit_gain'] if h['retrofit'] else 0))
            protection_h=min(0.92,pc['heat_protection']+(pc['retrofit_gain']*0.65 if h['retrofit'] else 0))
            hazard_flood= (flood and h['flood_exposure']*intensity*(1-protection_f)>0.52)
            effective_heat=h['heat_exposure']*scenario_cfg['heat_factor']*(1-protection_h)
            hazard_heat=heat and effective_heat>0.57
            damage=0.0
            if h['home']=='stable' and hazard_flood:
                damage=round(320*intensity*h['flood_exposure']*(1-protection_f)+90,2)
                h['damage']+=damage;totals['damage_cost']+=damage
                if damage>190:h['home']='damaged';action='flood_damage'
            if severe_shock and h['home'] in ('damaged','stable'):
                # option to reverse/retrofit; explicit resource constraint, fiscal effort, network externality
                base_cost=pc['retrofit_cost']*(1.0+0.10*h['vulnerable'])
                discounted_cost=round(base_cost*1.015**(week/52),2)
                if hazard_flood or hazard_heat or h['home']=='damaged':
                    propensity=0.15+0.32*h['risk']+0.22*peer_rate+0.12*h['trust']
                    coin=random.Random(seed*3389+i*37+2026).random()
                    if coin<propensity and h['budget']>=discounted_cost:
                        h['budget']=transact(h['budget'],discounted_cost);h['retrofit']=True;h['retrofit_cost_paid']+=discounted_cost
                        totals['private_spend']+=discounted_cost;totals['reversal_spend']+=discounted_cost
                        h['switch_time']=int(math.ceil(pc['retrofit_cost']/900))
                        h['home']='repairing';action='reverse_and_retrofit';cost+=discounted_cost
                    elif coin<propensity and h['budget']<discounted_cost:
                        totals['financial_denials']+=1;action='retrofit_blocked_budget'
            if h['home']=='repairing':
                h['switch_time']-=1
                if h['switch_time']<=0:h['home']='stable';action='retrofit_complete' if action=='hold' else action
            elif h['home']=='damaged':
                repair=round(damage*.7+150,2) if damage else 170.0
                if h['budget']>=repair:
                    h['budget']=transact(h['budget'],repair);totals['private_spend']+=repair;cost+=repair;h['home']='stable';action='repair_damage'
                else:totals['financial_denials']+=1
            if h['home']=='stable':
                maintenance=round(pc['shelter_cost']*pc['maintenance_rate']/52,2)
                if maintenance<=h['budget']:
                    h['budget']=transact(h['budget'],maintenance);h['maint']+=maintenance;totals['private_spend']+=maintenance;cost+=maintenance
                else:totals['financial_denials']+=1
            if h['home']!='stable':h['displaced_weeks']+=1;totals['displacement_weeks']+=1
            # welfare units are hypothetical indices, not currency or survey observations
            effective_heat=h['heat_exposure']*scenario_cfg['heat_factor']*(1-protection_h)
            welfare= 10+(2.5 if h['home']=='stable' else -4.5) - (2.5*effective_heat if heat else 0) - min(cost/1400,5) +0.3*peer_rate
            if h['vulnerable']:welfare-=0.7+0.4*effective_heat
            h['cum_welfare']+=welfare
            if sink:
                trace(sink,{'run_id':run_id,'agent_id':h['agent_id'],'actor_type':'household','time_step':week,'scenario_id':scenario,'policy_id':policy,'policy_version':SCHEMA_VERSION,'random_seed':seed,'prior_state':prev,'action':action,'next_state':h['home'],'budget_before':round(prev_budget,2),'budget_after':round(h['budget'],2),'displacement_before':prev_displaced,'displacement_after':h['displaced_weeks'],'peer_stable_share':round(peer_rate,3),'flood':flood,'heat':heat,'severe_reversal_shock':severe_shock,'utility_welfare':round(welfare,3),'vulnerable':h['vulnerable'],'cost':round(cost,2),'provenance':'DEVELOPMENT_TEST_FIXTURE'})
        # other 240 actors: explicit deterministic, capacity constrained agent role actions and state transitions
        for a in agents[360:]:
            st=state[a['agent_id']];before=st['budget'];index=a['role_index'];role=a['archetype'];action='monitor';spend=0.0
            if role=='ER' and flood:action='dispatch';spend=25+index%9
            elif role=='SP' and week%4==0:action='quote_compliant_material';spend=10+index%5
            elif role=='LG' and (flood or week%3==0):action='deliver';spend=20+index%9
            elif role=='HC' and heat:action='heat_outreach';spend=22+index%8
            elif role=='LA' and week%8==0:action='audit_permits';spend=12+index%4
            elif role=='FI' and week%10==0:action='verify_pledge';spend=7+index%5
            elif role=='CO' and week%2==0:action='community_consultation';spend=10+index%4
            if spend:
                st['budget']=transact(st['budget'],float(spend));st['service_units']+=1;asset_events[a['agent_id']]+=1;totals['service_events']+=1
            if sink:trace(sink,{'run_id':run_id,'agent_id':a['agent_id'],'actor_type':a['actor_type'],'time_step':week,'scenario_id':scenario,'policy_id':policy,'policy_version':SCHEMA_VERSION,'random_seed':seed,'prior_state':'active','action':action,'next_state':'active','budget_before':round(before,2),'budget_after':round(st['budget'],2),'cost':spend,'service_units':st['service_units'],'flood':flood,'heat':heat,'severe_reversal_shock':severe_shock,'provenance':'DEVELOPMENT_TEST_FIXTURE'})
      assert all(h['budget']>=-1e-9 for h in hs)
      assert all(st['budget']>=-1e-9 for st in state.values())
      means=statistics.mean(h['cum_welfare']/WEEKS for h in hs)
      vmean=statistics.mean(h['cum_welfare']/WEEKS for h in hs if h['vulnerable'])
      nonvmean=statistics.mean(h['cum_welfare']/WEEKS for h in hs if not h['vulnerable'])
      # RRI components in real units; synthetic benchmark normalization disclosed below
      reversal=totals['reversal_spend'];restoration=sum(h['displaced_weeks'] for h in hs)/360; displacement=totals['displacement_weeks']
      # RRI: base denominators are explicit research-design anchors, not learned weights.
      rri=round((reversal/360/2500 + restoration/15 + displacement/360/15)/3,6)
      return {'run_id':run_id,'scenario_id':scenario,'policy_id':policy,'seed':seed,'agents':600,'weeks':WEEKS,
         'trace_events':WEEKS*600 if save_trace else 0,'households':360,'acceptance_rate':round(totals['accepted']/360,6),
         'mean_weekly_welfare':round(means,6),'vulnerable_weekly_welfare':round(vmean,6),
         'nonvulnerable_weekly_welfare':round(nonvmean,6),'vulnerability_gap':round(nonvmean-vmean,6),
         'public_spend':round(totals['public_spend'],2),'private_spend':round(totals['private_spend'],2),
         'lifecycle_spend':round(totals['public_spend']+totals['private_spend'],2),'damage_cost':round(totals['damage_cost'],2),
         'reversal_spend':round(reversal,2),'displacement_weeks':round(displacement,2),
         'mean_displacement_weeks':round(restoration,6),'rri_proxy':rri,
         'service_events':totals['service_events'],'financial_denials':totals['financial_denials'],
         'policy_release_status':'EXPLORATORY_NOT_AUTHORIZED','evidence_class':'DEVELOPMENT_TEST_FIXTURE'}
    finally:
      if sink:sink.close()

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)

def launch(root:Path):
    root.mkdir(parents=True,exist_ok=True);(root/'results').mkdir(exist_ok=True);(root/'evidence').mkdir(exist_ok=True)
    runs=[];started=time.time()
    for scenario in PATHWAYS:
      for policy in POLICIES:
        for seed in range(1,9):
          r=simulate(scenario,policy,seed,root)
          runs.append(r)
          print(f"EXECUTED {r['run_id']} welfare={r['mean_weekly_welfare']:.3f} displacement={r['displacement_weeks']:.0f} rri={r['rri_proxy']:.4f}",flush=True)
    write_csv(root/'results'/'all_96_runs.csv',runs)
    metrics=['mean_weekly_welfare','vulnerable_weekly_welfare','vulnerability_gap','lifecycle_spend','public_spend','private_spend','damage_cost','reversal_spend','mean_displacement_weeks','rri_proxy','acceptance_rate']
    aggregated=[]
    for scenario in PATHWAYS:
      for policy in POLICIES:
        subset=[x for x in runs if x['scenario_id']==scenario and x['policy_id']==policy]
        row={'scenario_id':scenario,'policy_id':policy,'n_seeds':8}
        for metric in metrics:
            values=[float(x[metric]) for x in subset]
            row[f'{metric}_mean']=round(statistics.mean(values),6)
            row[f'{metric}_sd']=round(statistics.stdev(values),6)
            row[f'{metric}_ci95_halfwidth']=round(2.365*statistics.stdev(values)/math.sqrt(8),6)
        aggregated.append(row)
    write_csv(root/'results'/'scenario_policy_summary.csv',aggregated)
    # Paired B-A, C-A differences by matched scenario and seed; comparison still synthetic
    differences=[]
    index={(r['scenario_id'],r['policy_id'],r['seed']):r for r in runs}
    for scenario in PATHWAYS:
      for challenger in ['B','C']:
        for metric in ['mean_weekly_welfare','lifecycle_spend','mean_displacement_weeks','rri_proxy']:
          values=[index[(scenario,challenger,s)][metric]-index[(scenario,'A',s)][metric] for s in range(1,9)]
          differences.append({'scenario':scenario,'comparator':challenger+' minus A','metric':metric,'paired_mean':round(statistics.mean(values),6),'paired_sd':round(statistics.stdev(values),6),'paired_ci95_halfwidth':round(2.365*statistics.stdev(values)/math.sqrt(8),6),'n_pairs':8})
    write_csv(root/'results'/'paired_policy_differences.csv',differences)
    actor_ids=registry();write_csv(root/'results'/'actor_registry.csv',actor_ids)
    spec={'model':'BLIGHT','version':SCHEMA_VERSION,'type':'synthetic agent-based policy experiment','local_empirical_validity':'NOT_ESTABLISHED',
          'agents':len(actor_ids),'households':360,'other_actor_roles':240,'period_weeks':52,'scenarios':PATHWAYS,'policies':POLICIES,
          'seeds':list(range(1,9)),'shock_week':SHOCK_WEEK,'model_design_note':'Within a scenario and seed, both initial household attributes and external shocks are identical across policies. Differences are consequences of declared policy attributes and rule-based choices. Local parameters are not calibrated.',
          'RRI_proxy_formula':'mean of [reversal_spend/360/2500, mean_displacement_weeks/15, total_displacement_weeks/360/15]. These declared design anchors and equal weights are illustrative, not community endorsed.',
          'reality_boundary':'Code actually executed in current sandbox; synthetic agent outcomes, not real Aceh deployment or externally validated evidence.',
          'runtime_seconds':round(time.time()-started,3)}
    (root/'results'/'experiment_manifest.json').write_text(json.dumps(spec,indent=2))
    files=[p for p in root.rglob('*') if p.is_file() and p.name!='checksums.sha256']
    with (root/'results'/'checksums.sha256').open('w') as f:
      for p in sorted(files): f.write(sha256(p)+'  '+str(p.relative_to(root))+'\n')
    print('COMPLETE: ',len(runs),'configurations,',sum(r['trace_events'] for r in runs),'agent-week events',round(time.time()-started,2),'seconds')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',default='.')
    args=ap.parse_args();launch(Path(args.output))
