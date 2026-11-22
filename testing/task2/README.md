# OsdagBridge Task 2 - Multi-Run and State Persistence

Tested against `Nidhikhare12/OsdagBridge` branch `dev`, commit
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`, on macOS with Python 3.12.16 and
PySide6 6.9.3.

## Result

Three designs completed consecutively in one `QApplication`, one main window,
and one backend instance. The application was unlocked between runs. Backend
output and plot state were empty immediately after each unlock. The UI, saved
OSI/input dictionaries, output dictionaries, plots, mesh counts, and CAD images
then updated for spans/skews 25 m/0 deg, 30 m/+5 deg, and 35 m/-5 deg.

The custom girder material (Fy 360 MPa, Fu 510 MPa, E 205 GPa) persisted in all
three runs. A critical pre-existing defect was independently reproduced: the
input and CAD contain 4 structural girders, while `design_results.n_girders`
reports 6 because two deck-edge grillage lines are treated as girders. This is
tracked upstream as https://github.com/Nidhikhare12/OsdagBridge/issues/113.

## Contents

- `scripts/run_multirun_session.py`: same-process Qt automation.
- `evidence/session_02/`: per-run UI, OSI, dictionaries, CAD, plot, and session
  metadata. `session_01/` is a preserved harness setup failure, not a product
  test result.
- `test_log.csv`: compact case index.
- `notes/multirun_findings.md`: detailed technical findings and issue map.
- `reports/Task2_MultiRun_State_Persistence_Report.pdf`: final report.
- `video/Task2_MultiRun_Demonstration.mp4`: 114.85 s silent screencast showing
  the custom material dialog, three consecutive same-session designs, regenerated
  structural plots, and regenerated 3D CAD. Public playback/download:
  https://github.com/ananditasinha3004/OsdagBridge/blob/codex/task2-multirun-testing/testing/task2/video/Task2_MultiRun_Demonstration.mp4
- `resume/`: supplied current resume attachment.

## Re-run

From the OsdagBridge `src` directory:

```sh
QT_QPA_PLATFORM_PLUGIN_PATH=/opt/miniconda3/envs/osdagbridge-env/lib/python3.12/site-packages/PySide6/Qt/plugins/platforms \
  /opt/miniconda3/bin/conda run -n osdagbridge-env \
  python /path/to/run_multirun_session.py /new/evidence/directory
```

The script refuses to overwrite an existing `session.json`.

Set `OSDAGBRIDGE_DEMO_PAUSE` to a positive number to slow the workflow for a
screen-recording demonstration. The optional `OSDAGBRIDGE_DEMO_*_FILE`
variables coordinate recorder start/stop without exposing other applications.
