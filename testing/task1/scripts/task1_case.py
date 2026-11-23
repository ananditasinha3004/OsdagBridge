"""Real Qt desktop test driver. Run one case in a fresh process (spawn-safe)."""
from pathlib import Path
import os, sys, time, json, traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from unittest.mock import patch
import yaml

CASES = {
 1: {'basic': {}},
 3: {'basic': {'geometry.span':'45'}},
 4: {'basic': {'geometry.carriageway_width':'4.25'}},
 5: {'basic': {'geometry.carriageway_width':'23.6'}},
 6: {'basic': {'geometry.skew_angle':'-15'}},
 7: {'basic': {'geometry.skew_angle':'15'}},
 8: {'basic': {'geometry.include_median':'Yes','geometry.footpath':'Both Sides'}},
 9: {'additional': {'typical_section.deck_thickness':'275'}},
 10: {'basic': {'geometry.design_mode':'Custom'}, 'additional': {'member_properties.stiffener_details.intermediate_stiffener_spacing':'1800'}},
 11: {'additional': {'loading.seismic_load.damping':'5'}},
 12: {'additional': {'design_options.deck.top_clear_cover':'60'}},
 13: {'additional': {'design_options_cont.partial_factor.fatigue_strength.gamma_mf':'1.25'}},
 14: {'materials': {'material.girder': {'fy':'360','fu':'510','e':'205'}}},
 15: {'materials': {'material.cross_bracing': {'fy':'300','fu':'450'},'material.end_diaphragm': {'fy':'320','fu':'470'}}},
 16: {'basic': {'geometry.design_mode':'Custom'}, 'additional': {'member_properties.stiffener_details.intermediate_stiffener_thickness':'12','member_properties.stiffener_details.bearing_stiffener_plate_thickness':'12'}},
 17: {'materials': {'material.deck': {'fck':'45','fctm':'3.5','ecm':'35','density':'24.0'}}},
}

def main():
 from osdagbridge.desktop.__main__ import QApplication, CustomWindow, PlateGirderBridge, load_stylesheet
 from PySide6.QtWidgets import QWidget,QLineEdit,QComboBox,QFileDialog,QLabel,QTabWidget,QMessageBox
 from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox
 from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog
 from osdagbridge.desktop.ui.dialogs.generate_results_dialog import GenerateResultsDialog
 n=int(sys.argv[1]); root=Path(__file__).resolve().parents[1]; dest=Path(sys.argv[2]); dest.mkdir(parents=True,exist_ok=True)
 if (dest/'run.json').exists():raise RuntimeError('Evidence already exists; choose a new attempt directory.')
 meta={'case':f'TC-{n:02}','started_at':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'requested':CASES[n], 'method':'Qt widget edits and signals; native Save/Design/export handlers; fresh desktop process', 'messages':[], 'edits':[]}
 def dump(name,data): (dest/name).write_text(json.dumps(data,indent=2,default=str))
 def persist(): dump('run.json',meta)
 app=QApplication(sys.argv);app.setStyleSheet(load_stylesheet());w=CustomWindow('OsdagBridge',PlateGirderBridge);w.showMaximized()
 def pump(s=.2):
  end=time.monotonic()+s
  while time.monotonic()<end: app.processEvents();time.sleep(.02)
 def message(box):
  box.show();pump(.1)
  meta['messages'].append({'type':box.dialogType,'text':box.textLabel.text()})
  box.grab().save(str(dest/f'message_{len(meta["messages"]):02}.png'));print('DIALOG',meta['messages'][-1],flush=True);persist();box.hide();return 1
 def qtmessage(parent,title,text,*a,**k):
  meta['messages'].append({'type':title,'text':text});persist();return QMessageBox.StandardButton.Ok
 def edit(parent,key,value):
  field=parent.findChild(QWidget,key)
  assert field is not None,f'No widget: {key}'
  record={'key':key,'requested':value,'enabled':field.isEnabled(),'class':type(field).__name__};meta['edits'].append(record);persist()
  assert field.isEnabled(),f'Disabled input: {key}'
  # Select containing tabs so the edited field is represented in evidence.
  child=field; p=field.parentWidget()
  while p:
   if isinstance(p,QTabWidget):
    for i in range(p.count()):
     if p.widget(i).isAncestorOf(field):p.setCurrentIndex(i)
   child=p;p=p.parentWidget()
  if isinstance(field,QLineEdit):
   assert not field.isReadOnly(),f'Read-only input: {key}'
   record['before']=field.text();field.setText(value);field.textEdited.emit(value);field.editingFinished.emit();record['after']=field.text()
  elif isinstance(field,QComboBox):
   record['options']=[field.itemText(i) for i in range(field.count())];record['before']=field.currentText()
   assert value in record['options'],f'Unavailable option {value}: {record["options"]}'
   field.setCurrentText(value);record['after']=field.currentText()
  else:raise RuntimeError(f'Unsupported widget: {type(field)}')
  pump();field.grab().save(str(dest/f'field_{len(meta["edits"]):02}.png'));parent.grab().save(str(dest/f'input_{len(meta["edits"]):02}.png'));persist()
 with patch.object(CustomMessageBox,'exec',message),patch.object(QMessageBox,'information',qtmessage),patch.object(QMessageBox,'warning',qtmessage),patch.object(QMessageBox,'critical',qtmessage):
  try:
   pump(.5);baseline=yaml.safe_load((root/'osi/TC01_baseline.osi').read_text());w.input_dock.populate_from_dict(baseline);pump()
   for k,v in CASES[n].get('basic',{}).items():edit(w.input_dock.input_widget,k,v)
   if 'additional' in CASES[n]:
    w._show_additional_inputs();d=w._additional_inputs_dialog;pump()
    for k,v in CASES[n]['additional'].items():edit(d,k,v)
    d._save_inputs();dump('additional_saved.json',d.working_input_dict);d.hide()
   for component,values in CASES[n].get('materials',{}).items():
    def material_dialog(d):
     d.show();pump()
     for suffix,value in values.items():
      key=('material.deck.' if component=='material.deck' else 'material.girder.')+suffix
      f=d.field_inputs[key];f.setText(value);f.textEdited.emit(value);f.editingFinished.emit()
     pump();d.grab().save(str(dest/(component.replace('.','_')+'_custom.png')))
     d._validate_and_save();meta.setdefault('custom_dialogs',{})[component]={'result':d.result(),'fields':d.get_export_fields()};persist();d.hide();return d.result()
    with patch.object(MaterialPropertiesDialog,'exec',material_dialog):edit(w.input_dock.input_widget,component,'Custom')
   dump('input_before_save.json',w.input_dict)
   with patch.object(QFileDialog,'getSaveFileName',return_value=(str(dest/'input.osi'),'')):w.common_design_func('Save')
   assert (dest/'input.osi').exists(),'Save did not produce OSI'
   dump('input_after_save.json',w.input_dict);w.grab().save(str(dest/'inputs.png'))
   w.input_dock.design_btn.click();deadline=time.monotonic()+240
   while getattr(w,'_design_running',False) and time.monotonic()<deadline:pump(.1)
   assert not getattr(w,'_design_running',False),'Design timeout'
   meta['input_locked']=w.input_dock.is_locked;dump('input_after_design.json',w.input_dict)
   out=dict(w.backend.output_dict);dump('output_dictionary.json',out)
   assert w.input_dock.is_locked,'Application did not complete successful design workflow'
   pump(.5);w.grab().save(str(dest/'design_view.png'))
   try:meta['cad_saved']=bool(w.cad_3d_widget.display.View.Dump(str(dest/'cad.png')))
   except Exception:meta['cad_error']=traceback.format_exc()
   merged={**w.input_dict,**getattr(w.input_dock,'input_dock_values',{}),**out}
   d=GenerateResultsDialog(input_dict=merged,bridge=w.backend);d.page_generate.select_all_items();d._handle_show_selections();d.page_export.select_all_items()
   with patch.object(QFileDialog,'getSaveFileName',return_value=(str(dest/'results.xlsx'),'')):d.page_export._export_excel()
   meta['workbook_saved']=(dest/'results.xlsx').exists();meta['status']='execution_completed'
  except BaseException:meta['status']='incomplete';meta['error']=traceback.format_exc();print(meta['error'],flush=True)
  finally:
   meta['finished_at']=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat();persist();print('CASE_FINISHED',n,meta['status'],flush=True)
 return 0 if meta['status']=='execution_completed' else 1

if __name__=='__main__':
 code=main();sys.stdout.flush();sys.stderr.flush();os._exit(code)
