import csv,json,hashlib,zipfile
from pathlib import Path
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.units import mm
R=Path(__file__).resolve().parents[1]; O=R/'results'; E=R/'evidence'
def read_csv(name):return list(csv.DictReader(open(O/name,newline='')))
manifest=json.loads((O/'simulation_manifest.json').read_text()); summary=read_csv('sensitivity_summary.csv'); seeds=read_csv('seed_level_welfare.csv'); traces=read_csv('complete_HH_0001_decision_trace.csv')
assert len(seeds)==32 and len(traces)==104
# Detailed text appendix, all rows of trace in attached CSV
md=['# Appendix R - BLIGHT matched-seed deployment-delay sensitivity','', '**Status:** Actually executed Python simulation; development-test fixtures only; not Aceh-calibrated.','', '## R1. Simulation manifest','', 'The original BLIGHT v0.1 source is supplied unchanged. The sensitivity driver overrides only `POLICIES["B"]["install_delay"]` from 3 weeks to 1 week. Policy A retains one week. All other economic, hazard, budget and household parameters remain identical.','', f'- Model source SHA-256: `{manifest["original_source_sha256"]}`',f'- Driver SHA-256: `{manifest["sensitivity_driver_sha256"]}`',f'- Python version: {manifest["python_version"]}; standard library only for the simulation.',f'- Scenarios: {", ".join(manifest["scenario_parameters"])}; seeds: 1-8; 52 weekly steps; 600 actors (360 households); shock week 27.', '- 64 actual reruns: 32 original A control replays and 32 equal-delay B sensitivity runs; 32 historical A and B pairs also read from original 96-run CSV.', '- Randomisation: matching scenario/seed generates common synthetic household traits, weather stream and acceptance random draws for each A/B comparison.', '- Synthetic welfare outcome: mean across households of each household\'s mean weekly welfare index. No empirical welfare measurement.', '- Baseline A replay reproduced the recorded six-decimal welfare for all 32 runs exactly.', '- One complete 52-step trace per A-original and B-equal-delay is in `results/complete_HH_0001_decision_trace.csv` and a JSONL copy.', '- Warning: model generated identical `run_id` labels for baseline B and sensitivity B; provenance is distinguished by the experiment ID and separate folders.','', '### Parameters', '', '| Parameter | A baseline | B baseline | B equal delay |','|---|---:|---:|---:|']
for k in ['shelter_cost','public_share','flood_protection','heat_protection','maintenance_rate','retrofit_cost','retrofit_gain','install_delay']:
 md.append(f'| {k} | {manifest["baseline_policy_A"][k]} | {manifest["baseline_policy_B"][k]} | {manifest["policy_B_equalized"][k]} |')
md.extend(['','## R2. Observed synthetic welfare results','', '| Scenario | N matched | Baseline B-A | Equal-delay B-A | Improvement | B wins equal delay |','|---|---:|---:|---:|---:|---:|'])
for r in summary:
 md.append(f'| {r["scenario_id"]} | {r["n_matched_seeds"]} | {float(r["baseline_B_minus_A_mean"]):+.3f} | {float(r["equal_delay_B_minus_A_mean"]):+.3f} | {float(r["change_in_gap_due_to_equal_delay_mean"]):+.3f} | {r["equal_delay_B_higher_count"]} |')
md.extend(['','### All 32 seed-level welfare outcomes','','| Path | Seed | A original | B original | A equal | B equal | Original B-A | Equal B-A |','|---|---:|---:|---:|---:|---:|---:|---:|'])
for r in seeds:md.append('| '+ ' | '.join([r['scenario_id'],r['seed']]+[f'{float(r[k]):.4f}' for k in ('baseline_A_welfare','baseline_B_welfare','equal_delay_A_welfare','equal_delay_B_welfare','baseline_B_minus_A','equal_delay_B_minus_A')])+' |')
md.extend(['','## R3. Full individual-agent decision trace','', 'Actor HH-0001, scenario S2, seed 1. All 52 weeks for Policy A original and Policy B equal delay. Every record has state transitions, action, budgets, displacement accumulation, shock flags, local welfare, peer influence, version, seed and provenance. Full records are supplied in CSV and JSONL files; this appendix prints selected core columns below.','', '| Policy | Week | Prior | Action | Next | Budget before | Budget after | Welfare |','|---|---:|---|---|---|---:|---:|---:|'])
for r in traces:md.append('| '+' | '.join([r['experiment'],r['time_step'],r['prior_state'],r['action'],r['next_state'],r['budget_before'],r['budget_after'],r['utility_welfare']])+' |')
md.extend(['','## R4. Limitations and interpretation','','The B-A gap improved by 1.603 simulated welfare points overall but remained negative across all 32 paired observations on average. In S4 the mean B-A gap is approximately +0.007 and only 4/8 seeds favour B; there is no robust ranking reversal. The delay is a model parameter that also enters household acceptance utility, so this sensitivity measures the model-defined combination of waiting time and adoption response. It does not isolate construction timing from preferences.','', 'The two scenarios differ in remaining fixed assumptions: initial material cost, government subsidy, protection and maintenance. Thus equal delays do not equalise budget constraints or procurement feasibility. Synthetic welfare is not validated against Aceh survey or disaster data. No inference about actual shelters is warranted. The earlier RRI formula double-counts displacement and is not used here.','', '## R5. Reproduction','','From the extracted package root, run `python src/run_equal_delay.py`. It replays 32 A controls, asserts identical baseline welfare for each and executes 32 B equal-delay runs, producing seed-level results, summary and one compressed complete B trace. All referenced inputs and source files are in this package.',''])
(R/'Appendix_R_Reproducibility.md').write_text('\n'.join(md))
# Professional compact PDF, landscape pages
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='MainTitleX',parent=styles['Title'],fontSize=18,leading=22,textColor=colors.HexColor('#173854'),spaceAfter=12));styles.add(ParagraphStyle(name='SectionX',parent=styles['Heading2'],fontSize=11,leading=14,textColor=colors.HexColor('#173854'),spaceBefore=9,spaceAfter=7));styles.add(ParagraphStyle(name='BodyX',parent=styles['BodyText'],fontSize=8.5,leading=12,spaceAfter=7));styles.add(ParagraphStyle(name='FootX',parent=styles['BodyText'],fontSize=7.3,leading=10,textColor=colors.HexColor('#444444')))
P=lambda s,sty='BodyX':Paragraph(s,styles[sty]); story=[]
def heading(s):story.append(P(s,'SectionX'))
def table(data,widths=None,font=7,pad=5):
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#173854')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f0f4f7')]),('BOTTOMPADDING',(0,0),(-1,-1),pad),('TOPPADDING',(0,0),(-1,-1),pad),('FONTSIZE',(0,0),(-1,-1),font),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,0),0.7,colors.HexColor('#173854'))]));story.append(t)
story.append(P('Appendix R  |  BLIGHT Sensitivity &amp; Reproducibility','MainTitleX'))
story.append(P('<b>Evidence classification:</b> Executed sandbox test with synthetic development fixtures. Not a validated Aceh forecast or a deployment to a public agency.'))
heading('R1. Simulation manifest')
for s in [f'Experiment: {manifest["experiment_id"]}. Python {manifest["python_version"]}, standard library simulator, 600 computational actors (360 households), 52 weekly steps, shock in week 27.', 'Design: 4 pathways x 8 matched seeds x (A control replay and B delay sensitivity) = 64 newly executed runs. Original 96-configuration results supply the historical comparison.', 'Sole modification: B.install_delay reduced from 3 weeks to 1 week, matching A. No other policy coefficients were modified. Same scenario-seed generates matching household traits, random acceptance draws and weather shocks.',f'Source SHA-256: {manifest["original_source_sha256"]}',f'Driver SHA-256: {manifest["sensitivity_driver_sha256"]}']:
 story.append(P(s,'FootX'))
heading('Controlled policy assumptions')
settings=[['Parameter','A baseline','B baseline','B equal delay']]
for k in ['shelter_cost','public_share','flood_protection','heat_protection','maintenance_rate','retrofit_cost','retrofit_gain','install_delay']:
 settings.append([k]+[str(manifest[x][k]) for x in ('baseline_policy_A','baseline_policy_B','policy_B_equalized')])
table(settings,[165,120,120,120],7.6,4)
heading('R2. Welfare ranking change')
summary_rows=[['Path','Pairs','B - A original','B - A equal delay','Gain from change','B wins (equal)']]
for r in summary:summary_rows.append([r['scenario_id'],r['n_matched_seeds'],f'{float(r["baseline_B_minus_A_mean"]):+.3f}',f'{float(r["equal_delay_B_minus_A_mean"]):+.3f}',f'{float(r["change_in_gap_due_to_equal_delay_mean"]):+.3f}',r['equal_delay_B_higher_count']])
table(summary_rows,[75,70,120,140,130,105],8,6)
story.append(Spacer(1,7));story.append(P('A larger welfare index is better. Pooled mean gap improves from -2.033 to -0.430 (+1.603). S4 becomes nearly tied (+0.007; B wins in 4/8 seeds), not a stable ranking reversal.','FootX'))
story.append(Spacer(1,12));heading('R3. Seed-level welfare values: all 32 matched pairs')
seed_table=[['Scenario','Seed','A original','B original','A equal','B equal','B-A original','B-A equal']]
for r in seeds:seed_table.append([r['scenario_id'],r['seed']]+[f'{float(r[k]):.4f}' for k in ('baseline_A_welfare','baseline_B_welfare','equal_delay_A_welfare','equal_delay_B_welfare','baseline_B_minus_A','equal_delay_B_minus_A')])
table(seed_table,[75,45,110,110,110,110,90,90],7,4)
story.append(PageBreak());heading('R4. Individual actor trace: HH-0001 / S2 / seed 1')
story.append(P('The following tables reproduce every observed week for the original A run and equal-delay B run (52 observations each). The attached CSV/JSONL preserve every available event attribute, including peer share, hazard flags, displacement, provenance and model version.','FootX'))
for label in ('A_original','B_equal_delay'):
 heading('Complete 52-step trace: '+label.replace('_',' '))
 parts=[x for x in traces if x['experiment']==label]
 trace_table=[['Week','Prior state','Action','Next state','Budget before','Budget after','Welfare','Cost']]
 for r in parts:
  trace_table.append([r[k] for k in ('time_step','prior_state','action','next_state','budget_before','budget_after','utility_welfare','cost')])
 table(trace_table,[42,95,150,90,95,95,66,65],6.65,3.3)
 story.append(Spacer(1,8))
heading('R5. Audit notes and interpretation')
for s in ['The original A outputs were replayed and matched the six-decimal welfare results of all 32 baseline runs. Complete trace source files are supplied for baseline A / S2 / seed 1 and equal-delay B / S2 / seed 1.','Synthetic conditions and assumed budget constraints are not evidence about actual Aceh housing conditions. Policy B still has higher price and different subsidies, protection and maintenance assumptions, so this is a deployment-delay sensitivity test rather than a fully equal-resource experiment.','The previously reported RRI proxy double-counted displacement. It is excluded. The experiment-specific manifest, original source, sensitivity driver and all seed-level outputs are supplied in the ZIP.']:
 story.append(P(s,'FootX'))
pdf=R/'BLIGHT_Reproducibility_Appendix.pdf';doc=SimpleDocTemplate(str(pdf),pagesize=landscape(A4),leftMargin=42,rightMargin=42,topMargin=38,bottomMargin=36)
def page(c,d):
 c.saveState();w,h=landscape(A4);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#6b7684'));c.drawString(42,21,'BLIGHT | executed synthetic policy-sensitivity experiment');c.drawRightString(w-42,21,str(d.page));c.restoreState()
doc.build(story,onFirstPage=page,onLaterPages=page)
# integrity index for archive
checks=[]
for path in sorted(R.rglob('*')):
 if path.is_file() and path.name!='SHA256SUMS.txt' and '_preview' not in path.parts:checks.append(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+str(path.relative_to(R)))
(R/'SHA256SUMS.txt').write_text('\n'.join(checks)+'\n')
out=Path('/mnt/data/BLIGHT_Equal_Delay_Sensitivity_and_Appendix.zip')
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for path in R.rglob('*'):
  if path.is_file() and '_preview' not in path.parts:z.write(path,'BLIGHT_Equal_Delay/'+str(path.relative_to(R)))
print(pdf,out,'pages and bytes',pdf.stat().st_size,out.stat().st_size)
