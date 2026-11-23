from pathlib import Path
import os, time, sys, json, yaml
from unittest.mock import patch
from osdagbridge.desktop.__main__ import QApplication, CustomWindow, PlateGirderBridge, load_stylesheet
from PySide6.QtWidgets import QLineEdit, QFileDialog, QDialog
from osdagbridge.desktop.ui.dialogs.generate_results_dialog import GenerateResultsDialog
from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox
if __name__ == '__main__':
    root=Path(__file__).resolve().parents[1]
    app=QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    w=CustomWindow("OsdagBridge", PlateGirderBridge)
    w.showMaximized()
    def pump(seconds):
        until=time.monotonic()+seconds
        while time.monotonic()<until:
            app.processEvents()
            time.sleep(.025)
    def shot(name):
        assert w.grab().save(str(root/'screenshots'/name))
    pump(1)
    baseline=yaml.safe_load((root/'osi/TC01_baseline.osi').read_text())
    w.input_dock.populate_from_dict(baseline)
    field=w.input_dock.input_widget.findChild(QLineEdit,'geometry.span')
    assert field.text()=='25'
    field.setText('20')
    field.editingFinished.emit()
    pump(.5)
    shot('TC02_span_input.png')
    with patch.object(QFileDialog,'getSaveFileName',return_value=(str(root/'osi/TC02_span20.osi'),'')), patch.object(CustomMessageBox,'exec',return_value=1):
        w.common_design_func('Save')
    assert yaml.safe_load((root/'osi/TC02_span20.osi').read_text())['geometry.span']=='20'
    w.input_dock.design_btn.click()
    deadline=time.monotonic()+150
    while getattr(w,'_design_running',False) and time.monotonic()<deadline:
        pump(.1)
    assert w.input_dock.is_locked
    pump(1)
    shot('TC02_design_view.png')
    assert w.cad_3d_widget.display.View.Dump(str(root/'screenshots/TC02_cad.png'))
    out=dict(w.backend.output_dict)
    (root/'results/TC02_output_dictionary.json').write_text(json.dumps(out,default=str,indent=1))
    merged={**w.input_dict,**getattr(w.input_dock,'input_dock_values',{}),**out}
    d=GenerateResultsDialog(input_dict=merged,bridge=w.backend)
    d.page_generate.select_all_items()
    d._handle_show_selections()
    d.page_export.select_all_items()
    with patch.object(QFileDialog,'getSaveFileName',return_value=(str(root/'results/TC02_results.xlsx'),'')):
        d.page_export._export_excel()
    print('TC02 EXPORT COMPLETE',flush=True)
    os._exit(0)
