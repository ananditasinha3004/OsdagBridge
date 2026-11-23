from pathlib import Path
import os, sys, time, json, yaml
from unittest.mock import patch

ROOT = Path('/Users/ananditasinha/Documents/OsdagBridge_FOSSEE/Task1')
OUT = ROOT / 'video' / 'evidence'
OUT.mkdir(parents=True, exist_ok=True)

from osdagbridge.desktop.__main__ import QApplication, CustomWindow, PlateGirderBridge, load_stylesheet
from PySide6.QtWidgets import QLineEdit, QFileDialog, QMessageBox
from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox
from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog

app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet())
w = CustomWindow('OsdagBridge - Task 1 Video Demonstration', PlateGirderBridge)
w.showMaximized(); w.show()

def pump(seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents(); time.sleep(.03)

def activate():
    try:
        import AppKit
        AppKit.NSApplication.sharedApplication().activateIgnoringOtherApps_(True)
    except Exception:
        pass
    w.raise_(); w.activateWindow(); pump(.5)

def msg(box):
    box.show(); pump(.7); box.hide(); return 1

def qmsg(*args, **kwargs):
    pump(.5); return QMessageBox.StandardButton.Ok

def set_span(value):
    f = w.input_dock.input_widget.findChild(QLineEdit, 'geometry.span')
    f.setText(str(value)); f.textEdited.emit(str(value)); f.editingFinished.emit(); pump(1)

def custom_material(dialog):
    dialog.show(); activate()
    values = {'fy':'360', 'fu':'510', 'e':'205'}
    for suffix, value in values.items():
        f = dialog.field_inputs['material.girder.' + suffix]
        f.setText(value); f.textEdited.emit(value); f.editingFinished.emit()
    pump(4)
    dialog._validate_and_save(); dialog.hide(); return dialog.result()

def save(run):
    path = OUT / f'run_{run}.osi'
    with patch.object(QFileDialog, 'getSaveFileName', return_value=(str(path), '')):
        w.common_design_func('Save')

def design(run):
    w.input_dock.design_btn.click()
    deadline = time.monotonic() + 240
    while getattr(w, '_design_running', False) and time.monotonic() < deadline: pump(.1)
    (OUT / f'run_{run}_output.json').write_text(json.dumps(dict(w.backend.output_dict), indent=2, default=str))
    activate(); pump(2)
    w.cad_3d_view_toggle(force_show=True); pump(4)
    w.plots_view_toggle(); pump(4)

with patch.object(CustomMessageBox, 'exec', msg), patch.object(QMessageBox, 'information', qmsg), patch.object(QMessageBox, 'warning', qmsg), patch.object(QMessageBox, 'critical', qmsg):
    baseline = yaml.safe_load((ROOT / 'osi/TC01_baseline.osi').read_text())
    w.input_dock.populate_from_dict(baseline); activate(); pump(2)
    with patch.object(MaterialPropertiesDialog, 'exec', custom_material):
        combo = w.input_dock.input_widget.findChild(type(w.input_dock.input_widget.findChild(QLineEdit, 'geometry.span')), 'material.girder')
        # Use the normal material selector through the generic widget API.
        from PySide6.QtWidgets import QComboBox
        combo = w.input_dock.input_widget.findChild(QComboBox, 'material.girder')
        combo.setCurrentText('Custom'); pump(1)
    for run, span in enumerate((25, 20, 30, 35), 1):
        if run > 1:
            w.input_dock.toggle_lock(confirm=False); activate(); set_span(span)
        save(run); design(run)
    pump(5)

os._exit(0)
