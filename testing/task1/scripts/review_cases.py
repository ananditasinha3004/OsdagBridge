"""Extract evidence without modifying native result workbooks."""
from pathlib import Path
import json,csv,math,hashlib
import openpyxl
root=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text()) if p.exists() else {}
def equal(a,b):
 try:return math.isclose(float(a),float(b),rel_tol=1e-8,abs_tol=1e-8)
 except (TypeError,ValueError):return a==b
records=[]
for n in range(3,18):
 attempts=sorted((root/f'runs/TC{n:02}').glob('attempt*'))
 if not attempts:continue
 p=attempts[-1];meta=read(p/'run.json')
 if 'finished_at' not in meta:continue
 before=read(p/'input_before_save.json');saved=read(p/'input_after_save.json');after=read(p/'input_after_design.json');out=read(p/'output_dictionary.json')
 requested={**meta['requested'].get('basic',{}),**meta['requested'].get('additional',{})}
 for component,fields in meta['requested'].get('materials',{}).items():requested.update({component+'.'+k:v for k,v in fields.items()})
 retention=[]
 for key,value in requested.items():
  r={'key':key,'requested':value,'before_save':before.get(key),'saved':saved.get(key),'after_design':after.get(key),'output':out.get(key)}
  r['retained']=all(equal(value,r[s]) for s in ['before_save','saved','after_design','output'])
  r['per_member_output']={k:v for k,v in out.items() if k.startswith(key+'.G')}
  retention.append(r)
 tables={};fails={};errors=[]
 if (p/'results.xlsx').exists():
  wb=openpyxl.load_workbook(p/'results.xlsx',read_only=True,data_only=True)
  for ws in wb:
   rows=list(ws.values);tables[ws.title]=rows
   bad=[r for r in rows[1:] if any(str(v).upper()=='FAIL' for v in r)]
   if bad:fails[ws.title]=bad
   for row in ws:
    for cell in row:
     if cell.data_type=='e':errors.append({'sheet':ws.title,'cell':cell.coordinate,'value':cell.value})
  wb.close()
 review={'case':meta['case'],'attempt':str(p),'status':meta['status'],'started_at':meta['started_at'],'finished_at':meta['finished_at'],'retention':retention,'all_requested_values_retained':all(r['retained'] for r in retention),'workbook_sheet_count':len(tables),'workbook_error_cells':errors,'tables':tables,'failed_check_rows':fails,'messages':meta['messages'],'error':meta.get('error'),'cad_saved':meta.get('cad_saved',False)}
 (p/'review.json').write_text(json.dumps(review,indent=2,default=str));records.append(review)
print(json.dumps([{k:r[k] for k in ['case','status','all_requested_values_retained','workbook_sheet_count']}|{'mismatches':[x for x in r['retention'] if not x['retained']]} for r in records],indent=2))
(root/'results/TC03_TC17_review.json').write_text(json.dumps(records,indent=2,default=str))
