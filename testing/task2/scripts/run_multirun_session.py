"""Exercise three consecutive OsdagBridge designs in one Qt process.

The driver uses real widgets/signals and the application's native Save, Design,
unlock, plot, and OpenCascade CAD paths. Evidence is written per run plus a
session-level JSON record.
"""

from __future__ import annotations

import json
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import yaml


RUNS = [
    {"span": "25", "skew": "0", "label": "baseline-custom-steel"},
    {"span": "30", "skew": "5", "label": "extended-span-positive-skew"},
    {"span": "35", "skew": "-5", "label": "long-span-negative-skew"},
]
CUSTOM_GIRDER = {"fy": "360", "fu": "510", "e": "205"}
DEMO_PAUSE = float(os.environ.get("OSDAGBRIDGE_DEMO_PAUSE", "0"))
DEMO_READY_FILE = os.environ.get("OSDAGBRIDGE_DEMO_READY_FILE")
DEMO_GO_FILE = os.environ.get("OSDAGBRIDGE_DEMO_GO_FILE")
DEMO_DONE_FILE = os.environ.get("OSDAGBRIDGE_DEMO_DONE_FILE")
DEMO_STOP_FILE = os.environ.get("OSDAGBRIDGE_DEMO_STOP_FILE")
UI_KEYS = [
    "geometry.span",
    "geometry.skew_angle",
    "geometry.carriageway_width",
    "material.girder",
    "material.deck",
]


def main() -> int:
    from osdagbridge.desktop.__main__ import (
        QApplication,
        CustomWindow,
        PlateGirderBridge,
        load_stylesheet,
    )
    from osdagbridge.desktop.ui.dialogs.custom_messagebox import CustomMessageBox
    from osdagbridge.desktop.ui.dialogs.material_properties import MaterialPropertiesDialog
    from PySide6.QtWidgets import QComboBox, QFileDialog, QLineEdit, QMessageBox, QWidget

    task1 = Path("/Users/ananditasinha/Documents/OsdagBridge_FOSSEE/Task1")
    dest = Path(sys.argv[1]).resolve()
    if (dest / "session.json").exists():
        raise RuntimeError("Evidence already exists; choose a new output directory")
    dest.mkdir(parents=True, exist_ok=True)

    meta = {
        "session_id": "TASK2-MULTIRUN-01",
        "started_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "pid": os.getpid(),
        "method": (
            "One QApplication, one CustomWindow, real Qt edits/signals, native Save/Design, "
            "lock-button unlock, live Matplotlib plot, and live OpenCascade CAD"
        ),
        "runs": [],
        "messages": [],
    }

    def dump(path: Path, data) -> None:
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def persist() -> None:
        dump(dest / "session.json", meta)

    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    window = CustomWindow("OsdagBridge", PlateGirderBridge)
    window.showMaximized()

    def pump(seconds: float = 0.2) -> None:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            app.processEvents()
            time.sleep(0.02)

    def showcase(multiplier: float = 1.0) -> None:
        """Keep important GUI states visible when recording a demonstration."""
        if DEMO_PAUSE > 0:
            pump(DEMO_PAUSE * multiplier)

    def signal_and_wait(signal_path: str | None, wait_path: str | None) -> None:
        """Synchronize the GUI with an external screen recorder in demo mode."""
        if not signal_path:
            return
        Path(signal_path).write_text("ready\n", encoding="utf-8")
        if not wait_path:
            return
        deadline = time.monotonic() + 120
        while not Path(wait_path).exists() and time.monotonic() < deadline:
            pump(0.1)
        if not Path(wait_path).exists():
            raise TimeoutError(f"Demo synchronization timed out waiting for {wait_path}")

    def custom_message(box):
        box.show()
        pump(0.1)
        title = box.windowTitle() or getattr(box, "title", "")
        text = box.textLabel.text()
        record = {"title": title, "text": text}
        meta["messages"].append(record)
        box.grab().save(str(dest / f"message_{len(meta['messages']):02}.png"))
        persist()
        box.hide()
        return "Continue" if "Unlocking will delete" in text else 1

    def qt_message(_parent, title, text, *_args, **_kwargs):
        meta["messages"].append({"title": title, "text": text})
        persist()
        return QMessageBox.StandardButton.Ok

    def field(key: str) -> QWidget:
        widget = window.input_dock.input_widget.findChild(QWidget, key)
        if widget is None:
            raise AssertionError(f"Widget not found: {key}")
        return widget

    def edit(key: str, value: str) -> dict:
        widget = field(key)
        if not widget.isEnabled():
            raise AssertionError(f"Disabled widget: {key}")
        record = {"key": key, "before": value_of(widget), "requested": value}
        if isinstance(widget, QLineEdit):
            widget.setText(value)
            widget.textEdited.emit(value)
            widget.editingFinished.emit()
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(value)
        else:
            raise TypeError(type(widget).__name__)
        pump()
        record["after"] = value_of(widget)
        return record

    def value_of(widget: QWidget):
        if isinstance(widget, QLineEdit):
            return widget.text()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        return None

    def ui_values() -> dict:
        return {key: value_of(field(key)) for key in UI_KEYS}

    def output_signature(output: dict) -> dict:
        def count(value):
            if isinstance(value, dict):
                return len(value)
            if isinstance(value, (list, tuple)):
                return len(value)
            return None

        keys = sorted(output)
        return {
            "key_count": len(keys),
            "keys": keys,
            "container_sizes": {key: count(output[key]) for key in keys if count(output[key]) is not None},
        }

    with (
        patch.object(CustomMessageBox, "exec", custom_message),
        patch.object(QMessageBox, "information", qt_message),
        patch.object(QMessageBox, "warning", qt_message),
        patch.object(QMessageBox, "critical", qt_message),
    ):
        try:
            pump(0.8)
            baseline = yaml.safe_load((task1 / "osi/TC01_baseline.osi").read_text())
            window.input_dock.populate_from_dict(baseline)
            pump(0.5)
            window.setWindowTitle("OsdagBridge Task 02 — ready to record")
            signal_and_wait(DEMO_READY_FILE, DEMO_GO_FILE)

            def material_dialog(dialog):
                dialog.show()
                pump()
                for suffix, value in CUSTOM_GIRDER.items():
                    widget = dialog.field_inputs[f"material.girder.{suffix}"]
                    widget.setText(value)
                    widget.textEdited.emit(value)
                    widget.editingFinished.emit()
                pump()
                dialog.grab().save(str(dest / "custom_girder_dialog.png"))
                showcase(1.5)
                dialog._validate_and_save()
                meta["custom_girder_export_fields"] = dialog.get_export_fields()
                persist()
                dialog.hide()
                return dialog.result()

            with patch.object(MaterialPropertiesDialog, "exec", material_dialog):
                edit("material.girder", "Custom")

            for index, spec in enumerate(RUNS, start=1):
                window.setWindowTitle(
                    f"OsdagBridge Task 02 — Run {index}/3 — span {spec['span']} m, "
                    f"skew {spec['skew']}°"
                )
                run_dir = dest / f"run_{index}"
                run_dir.mkdir()
                run = {
                    "run_number": index,
                    "label": spec["label"],
                    "started_at": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
                    "process_pid": os.getpid(),
                    "window_id": id(window),
                    "backend_id": id(window.backend),
                    "edits": [],
                }
                meta["runs"].append(run)
                persist()

                if index > 1:
                    assert window.input_dock.is_locked
                    window.input_dock.lock_btn.click()
                    pump(0.5)
                    run["unlock_state"] = {
                        "input_locked": window.input_dock.is_locked,
                        "backend_output_empty": not bool(getattr(window.backend, "output_dict", {})),
                        "plot_dataset_cleared": window.plots_widget._ds_all is None,
                        "plot_axes_after_clear": len(window.plots_widget._fig.axes),
                    }
                    window.grab().save(str(run_dir / "after_unlock.png"))
                    assert not window.input_dock.is_locked
                    showcase()

                run["edits"].append(edit("geometry.span", spec["span"]))
                run["edits"].append(edit("geometry.skew_angle", spec["skew"]))
                run["ui_before_design"] = ui_values()
                dump(run_dir / "ui_before_design.json", run["ui_before_design"])
                dump(run_dir / "input_before_save.json", window.input_dict)
                window.grab().save(str(run_dir / "inputs.png"))
                showcase()

                osi_path = run_dir / f"TASK2_run_{index}.osi"
                with patch.object(QFileDialog, "getSaveFileName", return_value=(str(osi_path), "")):
                    window.common_design_func("Save")
                assert osi_path.exists()
                dump(run_dir / "input_after_save.json", window.input_dict)

                window.input_dock.design_btn.click()
                window.setWindowTitle(f"OsdagBridge Task 02 — Run {index}/3 — designing…")
                deadline = time.monotonic() + 300
                while getattr(window, "_design_running", False) and time.monotonic() < deadline:
                    pump(0.1)
                assert not getattr(window, "_design_running", False), "Design timeout"
                assert window.input_dock.is_locked, "Design workflow did not complete and lock inputs"
                window.setWindowTitle(
                    f"OsdagBridge Task 02 — Run {index}/3 complete — 3D CAD and plots updated"
                )

                run["finished_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
                run["ui_after_design"] = ui_values()
                run["input_locked"] = window.input_dock.is_locked
                run["input_dict_ids"] = {"window_input": id(window.input_dict), "backend_input": id(window.backend.input_dict)}
                output = dict(window.backend.output_dict)
                run["output_signature"] = output_signature(output)
                run["available_loadcases"] = list(window.backend.get_available_loadcases())
                nodes, members = window.backend.get_nodes_members()
                run["graph_counts"] = {"nodes": len(nodes), "members": len(members)}
                run["plot_state"] = {
                    "dataset_id": id(window.plots_widget._ds_all),
                    "axes": len(window.plots_widget._fig.axes),
                    "title": window.plots_widget._fig.axes[0].get_title() if window.plots_widget._fig.axes else "",
                }
                dump(run_dir / "ui_after_design.json", run["ui_after_design"])
                dump(run_dir / "input_after_design.json", window.input_dict)
                dump(run_dir / "output_dictionary.json", output)
                window.grab().save(str(run_dir / "design_view.png"))
                window.plots_widget._fig.savefig(run_dir / "plot.png", dpi=180, bbox_inches="tight")
                run["cad_saved"] = bool(window.cad_3d_widget.display.View.Dump(str(run_dir / "cad.png")))
                persist()
                showcase(1.5)
                if DEMO_PAUSE > 0:
                    window.plots_view_toggle()
                    window.setWindowTitle(
                        f"OsdagBridge Task 02 — Run {index}/3 complete — regenerated plot"
                    )
                    pump(0.5)
                    showcase(1.5)
                    window.cad_3d_view_toggle(force_show=True)
                    window.setWindowTitle(
                        f"OsdagBridge Task 02 — Run {index}/3 complete — regenerated 3D CAD"
                    )
                    pump(0.5)
                    showcase(1.5)

            meta["same_process_all_runs"] = len({r["process_pid"] for r in meta["runs"]}) == 1
            meta["same_window_all_runs"] = len({r["window_id"] for r in meta["runs"]}) == 1
            meta["same_backend_all_runs"] = len({r["backend_id"] for r in meta["runs"]}) == 1
            meta["status"] = "execution_completed"
            window.setWindowTitle("OsdagBridge Task 02 — all three consecutive runs complete")
            signal_and_wait(DEMO_DONE_FILE, DEMO_STOP_FILE)
        except BaseException:
            meta["status"] = "incomplete"
            meta["error"] = traceback.format_exc()
            print(meta["error"], flush=True)
        finally:
            meta["finished_at"] = datetime.now(ZoneInfo("Asia/Kolkata")).isoformat()
            persist()
            print("TASK2_FINISHED", meta["status"], flush=True)

    return 0 if meta["status"] == "execution_completed" else 1


if __name__ == "__main__":
    exit_code = main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(exit_code)
