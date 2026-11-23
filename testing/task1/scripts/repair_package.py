from pathlib import Path
import json,csv,shutil,hashlib,zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape
import openpyxl
from pypdf import PdfReader,PdfWriter
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PIL import Image as PI

root=Path(__file__).resolve().parents[1]
stamp=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat()
replay=root/'runs/TC01/replay1'
meta=json.loads((replay/'run.json').read_text())
assert meta['status']=='execution_completed' and meta['cad_saved'] and meta['workbook_saved']
selected={}
def include(p):
 p=Path(p);assert p.is_file(),p
 selected[str(p.relative_to(root))]=p
def copy(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if src!=dst:
  if dst.exists():assert src.read_bytes()==dst.read_bytes(),f'Conflicting existing evidence: {dst}'
  else:shutil.copy2(src,dst)
 include(dst)
def write(path,content):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content);include(path)

for n in (1,2):
 case=f'TC{n:02}';p=root/f'runs/{case}/original';p.mkdir(parents=True,exist_ok=True)
 source=root/('osi/TC01_baseline.osi' if n==1 else 'osi/TC02_span20.osi')
 copy(source,p/'input.osi');copy(root/f'results/{case}_results.xlsx',p/'results.xlsx')
 for f in (root/'screenshots').glob(case+'_*.png'):
  if '_replay1_' not in f.name:copy(f,p/'screenshots'/f.name);include(f)
 if n==2:
  copy(root/'logs/TC02_final.log',p/'runtime.log');copy(root/'results/TC02_output_dictionary.json',p/'output_dictionary.json')
  note='Original TC-02 Qt desktop run. runtime.log is an exact copy of logs/TC02_final.log. Before/after input snapshots were not captured by that earlier driver. No files in this original folder are a replay.'
 else:
  note='Original user-operated TC-01 run, 21 November 2026. The original full runtime log and output dictionary were not captured. Original screenshots include analysis completion. See ../replay1 for a separately dated fresh execution with its own real runtime log and dictionaries. Replay evidence must not be attributed to the original run.'
 write(p/'PROVENANCE.txt',note+'\n');include(source)
copy(root/'logs/TC01_replay1.log',replay/'runtime.log')
write(replay/'PROVENANCE.txt','TC-01 evidence-completion replay. Started '+meta['started_at']+'; finished '+meta['finished_at']+'. Source commit d74f56dd7f22925fb8148cabf5740ed8d1e39ff3. This log was captured live during this replay, not the original manual test.\n')
for f in replay.glob('*.png'):copy(f,root/'screenshots'/('TC01_replay1_'+f.name))

styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
def p(s,style='BodyText'):return Paragraph(escape(str(s)),styles[style])
def table(rows,widths):
 t=Table([[p(v) for v in row] for row in rows],colWidths=widths,repeatRows=1)
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eef2')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7)]));return t
def extract(path):
 wb=openpyxl.load_workbook(path,read_only=True,data_only=True)
 data={name:list(wb[name].values) for name in ['Bridge Configuration Summary','Design Results Summary','Fatigue Assessment - Girder','Deflection - Total Load']};wb.close();return data
def image(path):
 with PI.open(path) as im:w,h=im.size
 s=min(480/w,215/h);return Image(str(path),width=w*s,height=h*s)
def report_section(title,source,provenance,img,evidence):
 data=extract(source);summary=data['Design Results Summary'][1:]
 story=[p(title,'Title'),Spacer(1,8),p(provenance),Spacer(1,10),p('Recorded configuration','Heading2')]
 conf=data['Bridge Configuration Summary'];story.append(table([['Parameter','Exported value']]+[[k,v] for k,v in zip(conf[0],conf[1])],[330,165]))
 story.extend([p('Observed design outcome','Heading2'),p(f'{sum(row[-1]=="FAIL" for row in summary)}/{len(summary)} exported member rows FAIL in the native Design Results Summary. Failed design checks do not establish a software bug by themselves.'),table([['Member','Controlling check','Utilization','Status']]+[[r[0],r[2],r[-2],r[-1]] for r in summary],[65,280,80,70]),Spacer(1,8),image(img),p('Evidence: '+evidence),p('This is a test evidence report. An application-generated full structural design-report PDF is not included.')])
 return story,data

for n in (1,2):
 case=f'TC{n:02}';original=root/f'runs/{case}/original';title=f'{case}: '+('25 m baseline' if n==1 else '20 m span')
 prov=(original/'PROVENANCE.txt').read_text()
 img=root/('screenshots/TC01_3d_cad.png' if n==1 else 'screenshots/TC02_cad.png')
 story,data=report_section(title,original/'results.xlsx',prov,img,f'runs/{case}/original; osi/{"TC01_baseline.osi" if n==1 else "TC02_span20.osi"}; results/{case}_results.xlsx')
 note='# '+title+'\n\n'+prov+'\n\nSource commit: d74f56dd7f22925fb8148cabf5740ed8d1e39ff3.\n\n'
 for name,rows in data.items():
  note+='## '+name+'\n\n| '+' | '.join(map(str,rows[0]))+' |\n|'+'|'.join(['---']*len(rows[0]))+'|\n'
  for row in rows[1:]:note+='| '+' | '.join(map(str,row))+' |\n'
  note+='\n'
 if n==1:
  extra,_=report_section('TC01: separately dated replay',replay/'results.xlsx',(replay/'PROVENANCE.txt').read_text(),replay/'cad.png','runs/TC01/replay1; logs/TC01_replay1.log')
  story += [PageBreak()]+extra
  note+='## Replay\n\n'+(replay/'PROVENANCE.txt').read_text()+'\n[Live replay log](../logs/TC01_replay1.log). Original evidence remains in runs/TC01/original.\n'
 else:note+='[Original final runtime log](../logs/TC02_final.log).\n'
 write(root/f'notes/{case}_evidence_report.md',note)
 report=root/f'reports/{case}_Test_Report.pdf'
 SimpleDocTemplate(str(report),pagesize=A4,leftMargin=42,rightMargin=42,topMargin=32,bottomMargin=32).build(story);include(report)

old_report=root/'reports/Task1_TC03_TC17_Test_Report.pdf';pdf=PdfReader(old_report)
assert len(pdf.pages)==18
for n in range(3,18):
 case=f'TC{n:02}';run=root/f'runs/{case}/attempt1'
 copy(run/'input.osi',root/f'osi/{case}_input.osi')
 copy(run/'results.xlsx',root/f'results/{case}_results.xlsx')
 for f in run.glob('*.png'):copy(f,root/'screenshots'/(case+'_'+f.name))
 copy(root/f'logs/{case}_attempt1.log',run/'runtime.log')
 writer=PdfWriter();writer.add_page(pdf.pages[n]);file=root/f'reports/{case}_Test_Report.pdf'
 with file.open('wb') as f:writer.write(f)
 include(file)
combined=PdfWriter()
for name in ['TC01_Test_Report.pdf','TC02_Test_Report.pdf','Task1_TC03_TC17_Test_Report.pdf']:
 combined.append(str(root/'reports'/name))
file=root/'reports/Task1_TC01_TC17_Test_Report.pdf'
with file.open('wb') as f:combined.write(f)
include(file);include(old_report)

index=[]
for n in range(1,18):
 case=f'TC{n:02}';osi=f'osi/{case}_input.osi' if n>2 else ('osi/TC01_baseline.osi' if n==1 else 'osi/TC02_span20.osi')
 log=f'logs/{case}_attempt1.log' if n>2 else ('logs/TC01_replay1.log' if n==1 else 'logs/TC02_final.log')
 shots=sorted(f.name for f in (root/'screenshots').glob(case+'_*.png'))
 index.append({'case':case,'osi':osi,'report':f'reports/{case}_Test_Report.pdf','results':f'results/{case}_results.xlsx','runtime_log':log,'run_folder':f'runs/{case}/','screenshots':'; '.join('screenshots/'+x for x in shots),'provenance':'Original runtime log unavailable; listed log is separately dated replay' if n==1 else ('Original final run' if n==2 else 'Original attempt1')})
 for path in [osi,log,f'reports/{case}_Test_Report.pdf',f'results/{case}_results.xlsx']:include(root/path)
 assert shots
with (root/'PACKAGE_INDEX.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=index[0]);w.writeheader();w.writerows(index)
include(root/'PACKAGE_INDEX.csv')
# Update links while preserving the original test dates and outcomes.
testlog=root/'results/test_log.csv'
with testlog.open(newline='') as f:
 reader=csv.DictReader(f);fields=reader.fieldnames;testrows=list(reader)
for row in testrows:
 case=row['test_id'].replace('-','')
 if case=='TC01':
  row['log_file']=str(root/'logs/TC01_replay1.log')
  extra='Original full runtime log unavailable. Linked log is a separately dated TC01 replay; original evidence is preserved in runs/TC01/original.'
  if extra not in row['notes']:row['notes']+=' '+extra
 elif case=='TC02':row['log_file']=str(root/'logs/TC02_final.log')
 extra=f'Individual test report: reports/{case}_Test_Report.pdf. Package locations: PACKAGE_INDEX.csv.'
 if extra not in row['notes']:row['notes']+=' '+extra
with testlog.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(testrows)
planning_dir=root.parents[1]/'planning'
planning_dir.mkdir(parents=True,exist_ok=True)
shutil.copy2(testlog,planning_dir/'test_log.csv')
write(root/'PACKAGE_AUDIT.json',json.dumps({'checked_at':stamp,'cases':17,'top_level_osi_cases':17,'individual_test_reports':17,'case_run_folders':17,'screenshot_case_groups':17,'runtime_log_cases':17,'original_runtime_log_missing':['TC01'],'TC01_replay_started_at':meta['started_at'],'TC01_replay_status':meta['status'],'note':'Every indexed path and every archived file hash is verified by repair_package.py. TC01 log is from a separate replay, not its original manual run.'},indent=2))
write(root/'PACKAGE_README.txt','''CORRECTED TASK 1 PACKAGE, VERSION 2

Open PACKAGE_INDEX.csv for all 17 cases and their exact file locations.
reports/Task1_TC01_TC17_Test_Report.pdf covers TC01 through TC17.
reports/TC01_Test_Report.pdf through TC17_Test_Report.pdf are individual test reports.
osi/ contains all 17 case inputs. screenshots/ contains images for all 17 cases.
results/ contains all 17 native workbooks. runs/ contains TC01 through TC17.
logs/ contains the recorded execution logs indexed in PACKAGE_INDEX.csv.

TC01 ORIGINAL LOG LIMITATION:
The original manual TC01 runtime log and output dictionary were never captured.
The original screenshots, OSI and workbook are preserved in runs/TC01/original.
A new TC01 execution captured a real runtime log and dictionaries under
runs/TC01/replay1. Its timestamp and provenance are explicit; it is not passed
off as the original run. TC02's original final log is logs/TC02_final.log.

These PDFs are testing reports, not application-generated full structural
design reports. Native full design-report PDFs remain outside this package.
Execution completion does not mean structural checks passed. Previously
documented input-retention and export findings remain unresolved.

The root category folders provide convenient copies of case evidence. The
same bytes may also appear inside runs/ for self-contained case records.
MANIFEST_SHA256.txt hashes all bundled files except the manifest itself.
The previous package is retained as Task1_TC01_TC17_Evidence_v1.zip.
''')
# Preserve all authoritative raw records; omit interrupted exploratory attempts.
for sub in ['runs','notes']:
 for f in (root/sub).rglob('*'):
  if f.is_file() and f.name!='.DS_Store':include(f)
for f in (root/'scripts').glob('*.py'):
 if f.name!='run_geometry_cases.py':include(f)
for name in ['TC03_TC17_review.json','default_reset_reproduction.json','test_log.csv','TC02_output_dictionary.json']:include(root/'results'/name)
for f in (root/'screenshots').glob('TC[0-9][0-9]_*.png'):include(f)
for name in ['TC02.log','TC02_first_export_attempt.log']:include(root/'logs'/name)
manifest=root/'MANIFEST_SHA256.txt'
manifest.write_text('\n'.join(hashlib.sha256(selected[k].read_bytes()).hexdigest()+'  '+k for k in sorted(selected))+'\n');include(manifest)
archive=root.parent/'Task1_TC01_TC17_Evidence_v2.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for rel,path in sorted(selected.items()):z.write(path,'Task1/'+rel)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for row in index:
  for key in ['osi','report','results','runtime_log']:assert 'Task1/'+row[key] in z.namelist()
  assert any(x.startswith('Task1/'+row['run_folder']) for x in z.namelist())
  for shot in row['screenshots'].split('; '):assert 'Task1/'+shot in z.namelist()
 for line in manifest.read_text().splitlines():
  digest,rel=line.split('  ',1);assert hashlib.sha256(z.read('Task1/'+rel)).hexdigest()==digest
primary=root.parent/'Task1_TC01_TC17_Evidence.zip';backup=root.parent/'Task1_TC01_TC17_Evidence_v1.zip'
if not backup.exists():shutil.copy2(primary,backup)
shutil.copy2(archive,primary)
print(json.dumps({'archive':str(archive),'files':len(selected),'cases':len(index),'size_MiB':round(archive.stat().st_size/2**20,1),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'verified_at':stamp},indent=2))
