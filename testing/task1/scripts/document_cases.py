"""Build Task 1 records from completed desktop-run evidence, not invented results."""
from pathlib import Path
import json,csv,shutil,hashlib
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage

root=Path(__file__).resolve().parents[1]
planning=root.parents[1]/'planning'
records=json.loads((root/'results/TC03_TC17_review.json').read_text())
assert len(records)==15 and all(r['status']=='execution_completed' for r in records)
commit='d74f56dd7f22925fb8148cabf5740ed8d1e39ff3'
titles={3:'Span 45 m',4:'Carriageway width 4.25 m',5:'Carriageway width 23.6 m',6:'Skew -15 degrees',7:'Skew +15 degrees',8:'Median and footpaths on both sides',9:'Deck thickness 275 mm',10:'Custom G1M1 stiffener spacing 1800 mm',11:'Seismic damping 5%',12:'Deck top cover 60 mm',13:'Fatigue strength factor 1.25',14:'Custom girder steel',15:'Custom bracing and diaphragm steel',16:'Custom G1M1 stiffener thicknesses',17:'Custom concrete deck'}
labels={
'geometry.span':'Span (m)','geometry.carriageway_width':'Carriageway width (m)','geometry.skew_angle':'Skew (deg)','geometry.include_median':'Include median','geometry.footpath':'Footpath','geometry.design_mode':'Design mode',
'typical_section.deck_thickness':'Deck thickness (mm)',
'member_properties.stiffener_details.intermediate_stiffener_spacing':'G1M1 intermediate stiffener spacing (mm)',
'member_properties.stiffener_details.intermediate_stiffener_thickness':'G1M1 intermediate stiffener thickness (mm)',
'member_properties.stiffener_details.bearing_stiffener_plate_thickness':'G1M1 bearing stiffener thickness (mm)',
'loading.seismic_load.damping':'Seismic damping (%)','design_options.deck.top_clear_cover':'Deck top cover (mm)',
'design_options_cont.partial_factor.fatigue_strength.gamma_mf':'Fatigue strength factor gamma_mf',
}
for component,name in [('girder','Girder'),('cross_bracing','Cross bracing'),('end_diaphragm','End diaphragm')]:
 for prop,unit in [('fy','MPa'),('fu','MPa'),('e','GPa')]:labels[f'material.{component}.{prop}']=f'{name} {prop} ({unit})'
for prop,unit in [('fck','MPa'),('fctm','MPa'),('ecm','GPa'),('density','kN/m3')]:labels[f'material.deck.{prop}']=f'Deck {prop} ({unit})'
findings={
9:'F01: Deck thickness changed from the accepted 275 mm to 250 mm during Save Input and stayed 250 mm in the design output.',
11:'F01: Damping changed from the accepted 5% to 2% during Save Input and stayed 2% in the design output.',
12:'F01: Top cover changed from the accepted 60 mm to 50 mm during Save Input and stayed 50 mm in the design output.',
13:'F01: Fatigue factor changed from the accepted 1.25 to 1.35 during Save Input and stayed 1.35 in the design output.',
14:'F02: Custom girder properties were retained, but the steel export also repeated them for E 350A bracing and diaphragm rows (fy 360 / fu 510 MPa). Those components retained fy 350 / fu 490 MPa in the dictionaries.',
15:'F02: Bracing fy/fu 300/450 and diaphragm 320/470 MPa were retained in the dictionaries. The exported steel table instead showed 350/490 MPa for both, while displaying their custom grade names.',
17:'F03: Custom deck properties were retained in the dictionaries. The concrete export showed density 25 instead of 24 kN/m3, Ecm 35 under an MPa header although the input is 35 GPa, and modular ratio 5714.29 instead of the same-unit ratio 200/35 = 5.71429.'}
method='Each case starts in a fresh Qt desktop process from TC01_baseline.osi. The driver edits real widgets, emits their normal edit signals, invokes the application Save and Design handlers, and exports Select All results through the native exporter. Message boxes are recorded and acknowledged automatically. No solver or exporter results are substituted. CAD images are dumped from the live OpenCascade viewer because ordinary Qt window captures omit the native graphics surface.'
limits='These are Task 1 software-testing records. A completed run does not mean every structural check passed. Saved dictionaries establish retention, not independent verification that every calculation consumes every custom value. Full application design-report PDFs, structural-plot accuracy, same-session consecutive runs, screen recording, issue publication and final assignment submission remain separate work.'
findings_detail=[
('F01 - Additional inputs reset during saving',
 'Reproduced in TC-09, TC-11, TC-12 and TC-13. Each edit was accepted and present in input_before_save.json. input.osi, input_after_save.json and output_dictionary.json contain defaults. The UI reported successful saving without warning about these replacements.',
 'Source: desktop/ui/template_page.py:793 saveOSI_inputs calls solve_extend_basic_input_dict unconditionally. core/bridge_types/plate_girder/defaults.py:870 calls the tab-default functions; their _update helpers overwrite present values (e.g. lines 181-185, 263, 340, 362). A second isolated call using already-initialized inputs reproduced all four resets; see results/default_reset_reproduction.json.',
 'Suggested fix: initialize only missing user-controlled values. Separate derived geometry recomputation from default assignment. Add save/reload and design regression checks for these four fields. Do not silently overwrite accepted values.'),
('F02 - Steel export repeats girder properties for other components',
 'TC-14 exports custom girder fy/fu 360/510 MPa for bracing and diaphragm that retain 350/490. TC-15 exports 350/490 for custom bracing 300/450 and diaphragm 320/470. Grade names are component-specific but numeric values are not.',
 'Source: desktop/ui/dialogs/generate_results_values_builder.py:155 resolve_material_properties_steel obtains one steel_prop from bridge._build_material_props(). Its _row function reuses those numeric properties for all three rows.',
 'Suggested fix: resolve each row from the corresponding material prefix and grade, with explicit unit conversion. Test three different material definitions in one export. The finding proves an export mismatch; its effect on all internal design calculations remains unverified.'),
('F03 - Concrete export ignores custom density and mixes modulus units',
 'TC-17 input and output dictionaries retain density 24 kN/m3 and Ecm 35 GPa. Material Properties - Concrete exports density 25 and Ecm 35 labeled MPa. It computes 200000/35 = 5714.29 as the modular ratio; consistent MPa units give 200000/35000 = 5.71429.',
 'Source: desktop/ui/dialogs/generate_results_values_builder.py:204 resolve_material_properties_concrete reads cp.Ecm without GPa-to-MPa conversion and uses it as the denominator of steel_e_mpa/ecm. It hardcodes density = 25.0.',
 'Suggested fix: convert both moduli to the same unit for the ratio and display, and export density from the selected deck material. Add a custom-density and modulus-unit regression test. This is an export finding, not an independently verified solver error.')]

def number(r):return int(r['case'][-2:])
def status(r):return 'Completed - finding recorded' if number(r) in findings else 'Completed - input retention passed'
def summary(r):
 rows=r['tables']['Design Results Summary'][1:]
 failed=sum(x[-1]=='FAIL' for x in rows)
 checks=', '.join(dict.fromkeys(str(x[2]) for x in rows if x[-1]=='FAIL')) or 'none'
 return f'Native Design Results Summary: {failed}/{len(rows)} exported member rows FAIL. Controlling checks: {checks}.'

# Existing CSV is a machine-readable test log, not a redesigned workbook.
logpath=planning/'test_log.csv'
if not (planning/'test_log_before_TC03_TC17.csv').exists():shutil.copy2(logpath,planning/'test_log_before_TC03_TC17.csv')
with logpath.open(newline='') as f:reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
for r in records:
 n=number(r);p=Path(r['attempt']);m=json.loads((p/'run.json').read_text())
 params='; '.join(f"{labels.get(x['key'],x['key'])}={x['requested']}" for x in r['retention'])
 actual=f"Execution completed; 36-sheet workbook and CAD saved. Requested values retained: {r['all_requested_values_retained']}. "+summary(r)
 if n in findings:actual+=' '+findings[n]
 row=next(x for x in rows if x['test_id']==r['case'])
 row.update(session_id=f'TC{n:02}-fresh-process',run_number='1',tested_at=r['started_at'],commit=commit,parameters=params,parameters_file=str(p/'run.json'),expected_result='Accept the requested inputs, retain them through Save and Design, generate CAD and results, and export material values consistent with the saved inputs.',actual_result=actual,status=status(r),osi_file=str(p/'input.osi'),ui_screenshot=str(p/'inputs.png'),input_dictionary=str(p/'input_before_save.json'),output_dictionary=str(p/'output_dictionary.json'),cad_or_plot_evidence=str(p/'cad.png'),log_file=str(root/f'logs/TC{n:02}_attempt1.log'),notes=f"See Task1/notes/TC{n:02}.md. Native workbook: {p/'results.xlsx'}. Fresh session; not consecutive-run evidence.")
 text=f"# {r['case']}: {titles[n]}\n\nStatus: {status(r)}\n\nRun: {r['started_at']} to {r['finished_at']} (Asia/Kolkata). Source commit: `{commit}`.\n\n## Procedure and expected result\n\n{method}\n\nBaseline: TC01_baseline.osi (25 m span, 7.5 m carriageway, skew 0, no median/footpath, Bhagalpur Bihar). Only the following requested changes were entered; any computed changes are in the complete dictionaries. Expected: accepted changes survive saving and design, and the result export agrees.\n\n## Input comparison\n\n| Parameter | Requested | Before Save | After Save | After Design | Output |\n|---|---|---|---|---|---|\n"
 for x in r['retention']:text+='| '+' | '.join(str(y) for y in [labels.get(x['key'],x['key']),x['requested'],x['before_save'],x['saved'],x['after_design'],x['output']])+' |\n'
 if n in (10,16):text+='\nCustom mode is required by the UI. Stiffener edits apply to G1M1; the Apply changes to all custom button was not used. Other members retain their baseline stiffener values.\n'
 text+='\n## Actual result\n\n'+actual+'\n\nFailed-check sheets: '+', '.join(r['failed_check_rows'])+'.\n\n'
 for title in ['Bridge Configuration Summary','Design Results Summary','Deflection - Total Load','Material Properties - Steel','Material Properties - Concrete']:
  table=r['tables'].get(title,[])
  text+='### '+title+'\n\n'
  if table:
   text+='| '+' | '.join(map(str,table[0]))+' |\n|'+'|'.join(['---']*len(table[0]))+'|\n'
   for cells in table[1:]:text+='| '+' | '.join(str(c).replace('|','/') for c in cells)+' |\n'
  text+='\n'
 text+='## Evidence\n\n'
 for f in sorted(p.iterdir()):
  if f.is_file():text+=f'- [{f.name}](../runs/TC{n:02}/attempt1/{f.name})\n'
 text+=f'- [Runtime log](../logs/TC{n:02}_attempt1.log)\n\n## Limits\n\n{limits}\n'
 (root/f'notes/TC{n:02}.md').write_text(text)
with logpath.open('w',newline='') as f:writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
shutil.copy2(logpath,root/'results/test_log.csv')

index='# Task 1: TC-03 through TC-17\n\nAll 15 cases executed on 21 November 2026 (IST). Documentation reviewed on 22 November 2026. All runs produced OSI files, before/after input snapshots, output dictionaries, native 36-sheet results workbooks, screenshots, CAD images and runtime logs.\n\n11/15 cases retained every requested value in the saved input and output dictionary. Four additional-input cases failed retention. Three material cases had export discrepancies despite retaining their inputs. Every run has at least one failed member in the native overall Design Results Summary.\n\n'
index+='| Case | Scenario | Input retention | Finding | Record |\n|---|---|---|---|---|\n'
for r in records:
 n=number(r);index+=f"| {r['case']} | {titles[n]} | {'PASS' if r['all_requested_values_retained'] else 'FAIL'} | {findings.get(n,'None recorded').split(':')[0]} | [Case record](TC{n:02}.md) |\n"
index+='\n## Method and limits\n\n'+method+'\n\n'+limits+'\n\n## Evidence locations\n\n- `../runs/TC03/attempt1/` through `../runs/TC17/attempt1/`: authoritative completed runs.\n- `../results/test_log.csv`: full TC-01 through TC-17 index.\n- `../results/TC03_TC17_review.json`: extracted comparisons and native table values.\n- `../reports/Task1_TC03_TC17_Test_Report.pdf`: readable testing report, not the application-generated structural design report.\n- `findings_TC03_TC17.md`: observed defects, source locations and proposed fixes.\n\nEarlier partial geometry-run artifacts outside `runs/` are preserved but are not the evidence used for these results. No GitHub issues were posted and no application source was edited.\n'
(root/'notes/TC03_TC17_index.md').write_text(index)
fd='# Task 1 findings: TC-03 through TC-17\n\nObserved at commit `'+commit+'`. These are local findings, not published GitHub issues. Duplicate checking and issue URLs remain open.\n\n'
for title,obs,cause,fix in findings_detail:fd+=f'## {title}\n\n{obs}\n\n{cause}\n\n{fix}\n\n'
(root/'notes/findings_TC03_TC17.md').write_text(fd)

# PDF: one overview, two findings/method pages, one page per case.
(root/'reports').mkdir(exist_ok=True)
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='SmallBody',fontName='Helvetica',fontSize=8,leading=11,spaceAfter=5));styles.add(ParagraphStyle(name='CellSmall',fontName='Helvetica',fontSize=8,leading=10));styles['Title'].textColor=colors.HexColor('#25404c');styles['Heading2'].textColor=colors.HexColor('#25404c')
def para(s,style='SmallBody'):return Paragraph(escape(str(s)).replace('\n','<br/>'),styles[style])
def tab(data,widths):
 t=Table([[para(v,'CellSmall') for v in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT');t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eef1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#78919b')),('BOTTOMPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6)]));return t
story=[para('OsdagBridge | Task 1','Title'),para('TC-03 through TC-17','Heading1'),para('Input and customization testing - evidence report'),para('Runs: 21 November 2026 (IST). Report prepared: 22 November 2026.'),Spacer(1,10),para('15 runs completed; four input-retention failures','Heading2'),para('All 15 cases produced saved inputs, native result workbooks, dictionaries, logs and CAD captures. Eleven retained all requested values through execution. Three custom-material cases also revealed export discrepancies. Each native overall design summary contains at least one FAIL; application completion is not a structural pass.'),Spacer(1,8)]
overview=[['Case','Variation','Input retention','Finding']]
for r in records:
 n=number(r);overview.append([r['case'],titles[n],'PASS' if r['all_requested_values_retained'] else 'FAIL',findings.get(n,'-').split(':')[0]])
story +=[tab(overview,[45,267,90,90]),Spacer(1,12),para('Evidence root: Documents/OsdagBridge_FOSSEE/Task1. The notes folder contains linked case records; results/test_log.csv indexes TC-01 through TC-17.'),PageBreak(),para('Method, baseline and coverage','Heading1'),para(method),para('Baseline','Heading2'),para('TC01_baseline.osi: Highway Bridge, Bhagalpur Bihar, span 25 m, carriageway 7.5 m, no median, no footpath, skew 0 degrees, Optimized design; E 350A steel and M40 concrete. The complete 576-key baseline remains in osi/TC01_baseline.osi.'),para('Environment','Heading2'),para('macOS 15.5 (24F74); Python 3.12.16; PySide6 6.9.3; conda osdagbridge-env. Branch dev. Source commit: '+commit),para('Interpretation','Heading2'),para(limits),para('Coverage','Heading2'),para('TC-03 to TC-08 cover geometry boundaries/options. TC-09 to TC-13 cover all five Additional Inputs tabs. TC-14 to TC-17 cover custom girder, bracing, diaphragm, stiffener and deck properties. TC-10 and TC-16 use Custom mode and edit G1M1 only. This finite case set is not exhaustive input-combination coverage.'),para('Audit trail','Heading2'),para('For each run, run.json records requested edits and messages. input_before_save.json, input_after_save.json and input_after_design.json bracket the workflow; input.osi is the application-saved file. output_dictionary.json is the backend output snapshot. results.xlsx is the native Select All export. review.json contains the independently extracted table values and retention checks.'),para('Execution notes','Heading2'),para('The driver terminates its own process after successful export. Logs include shutdown semaphore-cleanup warnings. Earlier interrupted exploratory runs are retained separately and excluded from the authoritative result set. Native full design-report PDF generation and video recording are not claimed.'),PageBreak()]
for title,obs,cause,fix in findings_detail:
 story +=[para(title,'Heading2'),para(obs),para(cause),para(fix),Spacer(1,10)]
story +=[para('Finding evidence: notes/findings_TC03_TC17.md, per-case dictionaries and results.xlsx. No source changes or online issue publication were made.'),PageBreak()]
for idx,r in enumerate(records):
 n=number(r);p=Path(r['attempt'])
 story +=[para(r['case']+' | '+titles[n],'Heading1'),para(status(r)),para('Run: '+r['started_at']+' to '+r['finished_at']),para('Input comparison','Heading2')]
 data=[['Parameter','Requested','Before Save','After Save','Output']]
 for x in r['retention']:data.append([labels.get(x['key'],x['key']),x['requested'],x['before_save'],x['saved'],x['output']])
 story +=[tab(data,[222,65,70,65,70]),Spacer(1,8),para('Observed result','Heading2'),para(summary(r)),para('Failed-check sheets: '+', '.join(r['failed_check_rows'])+'.')]
 if n in findings:story.append(para(findings[n]))
 if n in (10,16):story.append(para('Custom stiffener changes apply to G1M1 only; other members retain their baseline values.'))
 imagepath=p/'cad.png'
 if n==14:imagepath=p/'material_girder_custom.png'
 if n==15:imagepath=p/'material_cross_bracing_custom.png'
 if n==17:imagepath=p/'material_deck_custom.png'
 with PILImage.open(imagepath) as im:iw,ih=im.size
 scale=min(460/iw,215/ih)
 story +=[Spacer(1,6),Image(str(imagepath),width=iw*scale,height=ih*scale),para('Captured '+('custom material dialog' if n in (14,15,17) else 'live CAD viewer')+'. Full-resolution images are in the case evidence folder.'),para(f'Evidence: runs/TC{n:02}/attempt1/ (input.osi, results.xlsx, dictionary snapshots, screenshots, review.json); logs/TC{n:02}_attempt1.log; notes/TC{n:02}.md. All requested values were also checked after Design; see the case note for the complete comparison.')]
 if idx<len(records)-1:story.append(PageBreak())
def footer(c,d):
 c.setStrokeColor(colors.HexColor('#b9c8cc'));c.line(42,35,553,35);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#50616a'));c.drawString(42,23,'OsdagBridge - Task 1 testing record');c.drawRightString(553,23,str(d.page))
SimpleDocTemplate(str(root/'reports/Task1_TC03_TC17_Test_Report.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=45,title='OsdagBridge Task 1 - TC-03 to TC-17',author='OsdagBridge testing record').build(story,onFirstPage=footer,onLaterPages=footer)
print('Documented',len(records),'cases; CSV, case notes, findings, index and PDF saved.')
