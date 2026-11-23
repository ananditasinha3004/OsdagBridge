OSDAGBRIDGE TASK 1 EVIDENCE

Start with reports/Task1_TC03_TC17_Test_Report.pdf or notes/TC03_TC17_index.md.
The 15 authoritative new runs are runs/TC03/attempt1 through runs/TC17/attempt1.
Each contains the actual application-saved OSI, native results workbook, input
snapshots, output dictionary, screenshots, live CAD capture and review data.
Runtime logs are in logs/TCnn_attempt1.log. Case notes are notes/TCnn.md.
results/test_log.csv includes the prior TC-01 and TC-02 records as context.

Observed outcomes:
- 15/15 new cases executed, rendered CAD and exported results.
- 11/15 retained every requested value through Save and Design.
- TC-09, TC-11, TC-12 and TC-13 reverted additional inputs during saving.
- TC-14, TC-15 and TC-17 exposed custom-material export discrepancies.
- Every native Design Results Summary contains at least one failed member.

This package documents testing, not a bridge design approval. The PDF is a
testing report, not an application-generated structural design report. Task 2
same-session testing, plots, screencast, GitHub publication and final assignment
submission are not claimed complete here. Source code was not modified.

Source: /Users/ananditasinha/OsdagBridge, dev branch, commit
d74f56dd7f22925fb8148cabf5740ed8d1e39ff3.
The source checkout and conda environment are not bundled in the evidence ZIP.

Reproduce a case in the same environment (choose a NEW attempt directory):
cd /Users/ananditasinha/OsdagBridge/src
QT_QPA_PLATFORM_PLUGIN_PATH=/opt/miniconda3/envs/osdagbridge-env/lib/python3.12/site-packages/PySide6/Qt/plugins/platforms PYTHONPATH=. /opt/miniconda3/envs/osdagbridge-env/bin/python -u /Users/ananditasinha/Documents/OsdagBridge_FOSSEE/Task1/scripts/task1_case.py 9 /Users/ananditasinha/Documents/OsdagBridge_FOSSEE/Task1/runs/TC09/attempt2

The driver uses actual Qt widgets/signals and native application handlers. It
records and automatically acknowledges dialogs. It does not mock the solver
or result exporter. It exits its own process after export; shutdown semaphore
warnings in the logs are preserved. Each case uses a fresh process, so these
runs do not establish consecutive-run behavior within one application session.

The ZIP excludes old interrupted geometry-run artifacts and PDF preview PNGs.
Those remain on disk for audit. MANIFEST_SHA256.txt hashes the bundled files.
