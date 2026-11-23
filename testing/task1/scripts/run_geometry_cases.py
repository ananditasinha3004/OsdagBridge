from pathlib import Path
import json, os, sys, time, yaml
from unittest.mock import patch
from PySide6.QtWidgets import QApplication, QLineEdit, QFileDialog
from osdagbridge.desktop.__main__ import CustomWindow, PlateGirderBridge, load_stylesheet
from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox

ROOT = Path(__file__).resolve().parents[1]
CASES = {
    "TC-03": ("span", "45", "span45"),
    "TC-04": ("carriageway_width", "4.25", "width425"),
    "TC-05": ("carriageway_width", "23.6", "width236"),
    "TC-06": ("skew_angle", "-15", "skewminus15"),
    "TC-07": ("skew_angle", "15", "skewplus15"),
}

app = QApplication(sys.argv)
app.setStyleSheet(load_stylesheet())

def pump(seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(.025)

for test_id, (field_key, value, slug) in CASES.items():
    w = CustomWindow("OsdagBridge", PlateGirderBridge)
    w.showMaximized()
    pump(.5)
    baseline = yaml.safe_load((ROOT / "osi/TC01_baseline.osi").read_text())
    w.input_dock.populate_from_dict(baseline)
    widget = w.input_dock.input_widget.findChild(QLineEdit, f"geometry.{field_key}")
    widget.setText(value)
    widget.editingFinished.emit()
    pump(.3)
    widget.grab().save(str(ROOT / f"screenshots/{test_id}_{slug}_field.png"))
    osi = ROOT / f"osi/{test_id}_{slug}.osi"
    with patch.object(QFileDialog, "getSaveFileName", return_value=(str(osi), "")), patch.object(CustomMessageBox, "exec", return_value=1):
        w.common_design_func("Save")
    w.input_dock.design_btn.click()
    deadline = time.monotonic() + 180
    while getattr(w, "_design_running", False) and time.monotonic() < deadline:
        pump(.1)
    pump(1)
    w.grab().save(str(ROOT / f"screenshots/{test_id}_{slug}_design.png"))
    w.cad_3d_widget.display.View.Dump(str(ROOT / f"screenshots/{test_id}_{slug}_cad.png"))
    output = dict(w.backend.output_dict)
    (ROOT / f"results/{test_id}_{slug}_output_dictionary.json").write_text(json.dumps(output, default=str, indent=1))
    print(test_id, field_key, value, "completed", flush=True)
    w.close()

os._exit(0)
