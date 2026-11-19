#!/usr/bin/env python3
"""Matched seed sensitivity: equalize only B install_delay to A=1 week.
Uses original BLIGHT simulator unmodified, applying a single in-memory policy override.
"""
import sys,csv,json,hashlib,statistics,math,platform
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=Path(__file__).resolve().parent
sys.path.insert(0,str(SRC))
import blight

def main():
    root=ROOT
    rows=list(csv.DictReader(open(root/'results'/'baseline_all_96_runs.csv',newline='')))
    base={(r['scenario_id'],r['policy_id'],int(r['seed'])):r for r in rows}
    original=dict(blight.POLICIES['B'])
    assert blight.POLICIES['A']['install_delay']==1 and original['install_delay']==3
    blight.POLICIES['B']={**original,'install_delay':blight.POLICIES['A']['install_delay']}
    out=[];control=[]
    for scenario in blight.PATHWAYS:
        for seed in range(1,9):
            a=blight.simulate(scenario,'A',seed,root,save_trace=False)
            old=base[(scenario,'A',seed)]
            assert abs(a['mean_weekly_welfare']-float(old['mean_weekly_welfare']))<0.0000001,(scenario,seed,a['mean_weekly_welfare'],old['mean_weekly_welfare'])
            b=blight.simulate(scenario,'B',seed,root,save_trace=(scenario=='S2' and seed==1))
            orig_b=base[(scenario,'B',seed)]
            x={'scenario_id':scenario,'seed':seed,'baseline_A_delay_weeks':1,'baseline_B_delay_weeks':3,'equalized_A_delay_weeks':1,'equalized_B_delay_weeks':1,
               'baseline_A_welfare':float(old['mean_weekly_welfare']),'baseline_B_welfare':float(orig_b['mean_weekly_welfare']),
               'equal_delay_A_welfare':a['mean_weekly_welfare'],'equal_delay_B_welfare':b['mean_weekly_welfare'],
               'baseline_B_minus_A':round(float(orig_b['mean_weekly_welfare'])-float(old['mean_weekly_welfare']),6),
               'equal_delay_B_minus_A':round(b['mean_weekly_welfare']-a['mean_weekly_welfare'],6),
               'change_in_gap_due_to_equal_delay':round((b['mean_weekly_welfare']-a['mean_weekly_welfare'])-(float(orig_b['mean_weekly_welfare'])-float(old['mean_weekly_welfare'])),6),
               'equal_delay_B_acceptance_rate':b['acceptance_rate'],'baseline_B_acceptance_rate':float(orig_b['acceptance_rate']),
               'baseline_B_displacement_weeks':float(orig_b['mean_displacement_weeks']),'equal_delay_B_displacement_weeks':b['mean_displacement_weeks'],
               'equal_delay_B_lifecycle_spend':b['lifecycle_spend']}
            out.append(x)
            print(f"{scenario} seed={seed} original gap={x['baseline_B_minus_A']:+.5f} equal-delay gap={x['equal_delay_B_minus_A']:+.5f}",flush=True)
    dest=root/'results'/'seed_level_welfare.csv'
    with dest.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
    sums=[]
    for sc in list(blight.PATHWAYS)+['ALL']:
        subset=[x for x in out if sc=='ALL' or x['scenario_id']==sc]
        n=len(subset)
        stats={'scenario_id':sc,'n_matched_seeds':n}
        for k in ('baseline_A_welfare','baseline_B_welfare','equal_delay_A_welfare','equal_delay_B_welfare','baseline_B_minus_A','equal_delay_B_minus_A','change_in_gap_due_to_equal_delay'):
            values=[x[k] for x in subset]
            stats[k+'_mean']=round(statistics.mean(values),6)
            stats[k+'_sd']=round(statistics.stdev(values),6)
            stats[k+'_ci95_halfwidth']=round((2.365 if n==8 else 2.04)*statistics.stdev(values)/math.sqrt(n),6)
        stats['baseline_A_higher_count']=sum(x['baseline_B_minus_A']<0 for x in subset)
        stats['equal_delay_B_higher_count']=sum(x['equal_delay_B_minus_A']>0 for x in subset)
        sums.append(stats)
    with (root/'results'/'sensitivity_summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(sums[0]));w.writeheader();w.writerows(sums)
    def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    manifest={'experiment_id':'BLIGHT-SENS-EQUAL-DELAY-20261119','execution_type':'actual Python execution, synthetic development fixtures',
        'analysis':'Matched-seed sensitivity of A vs B, equal deployment delays',
        'original_source_file':'src/blight.py in original BLIGHT_Executed_Sandbox_Complete.zip',
        'original_source_sha256':sha(SRC/'blight.py'),'sensitivity_driver_sha256':sha(__file__),
        'python_version':platform.python_version(),'standard_library_only':True,
        'scenario_parameters':blight.PATHWAYS,'baseline_policy_A':blight.POLICIES['A'],'baseline_policy_B':original,
        'intervention':'Set ONLY B.install_delay=1 (baseline 3), matching A.install_delay=1. All costs, subsidies, material protection, maintenance, retrofit assumptions unchanged.',
        'policy_B_equalized':blight.POLICIES['B'],'seeds':list(range(1,9)),'weeks':blight.WEEKS,'shock_week':blight.SHOCK_WEEK,
        'actors_per_run':600,'households_per_run':360,'runs_executed':64,'baseline_A_controls_replayed':32,'equal_delay_B_runs':32,
        'matched_randomness':'household traits, acceptance random draws, initial institution states and hazards use matching scenario-seed PRNG functions',
        'outcome':'mean_weekly_welfare (synthetic welfare index; average over 360 households and 52 weeks)',
        'interpretation':'Conditional synthetic model comparison; no calibrated Aceh claims or operational recommendations',
        'run_id_collision_note':'Sensitivity reuses simulator-generated B run_id labels; distinguish by experiment_id and output folder, never merge with baseline raw traces without design label.',
        'rri_not_used':'Earlier RRI prototype double-counts displacement; excluded from this sensitivity experiment.',
        'files':{'baseline_csv_sha256':sha(root/'results'/'baseline_all_96_runs.csv'),'seed_level_welfare_sha256':sha(dest)}}
    (root/'results'/'simulation_manifest.json').write_text(json.dumps(manifest,indent=2))
    print('ALL RUNS COMPLETE',json.dumps([{k:v for k,v in r.items() if k in ('scenario_id','baseline_B_minus_A_mean','equal_delay_B_minus_A_mean','change_in_gap_due_to_equal_delay_mean','equal_delay_B_higher_count')} for r in sums],indent=2),flush=True)
if __name__=='__main__':main()
