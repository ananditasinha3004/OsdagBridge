"""Package one combined Task 1 report with all indexed evidence."""
from pathlib import Path
import csv, hashlib, io, zipfile
from pypdf import PdfReader

base = Path('/Users/ananditasinha/Documents/OsdagBridge_FOSSEE')
source = base / 'Task1_TC01_TC17_Evidence_v2.zip'
report = base / 'Task1/reports/Task1_TC01_TC17_Test_Report.pdf'
output = base / 'Task1_Final_TC01_TC17.zip'
assert len(PdfReader(report).pages) == 21

with zipfile.ZipFile(source) as archive:
    assert archive.testzip() is None
    files = {
        name: archive.read(name)
        for name in archive.namelist()
        if name.startswith('Task1/')
        and name != 'Task1/reports/Task1_TC03_TC17_Test_Report.pdf'
        and name not in {
            'Task1/MANIFEST_SHA256.txt', 'Task1/PACKAGE_INDEX.csv',
            'Task1/PACKAGE_README.txt', 'Task1/README.txt',
        }
    }
files['Task1/reports/Task1_TC01_TC17_Test_Report.pdf'] = report.read_bytes()
video = base / 'Task1/video/Task1_workflow_recording.mov'
assert video.exists() and video.stat().st_size > 100000
files['Task1/video/Task1_workflow_recording.mov'] = video.read_bytes()

with (base / 'Task1/PACKAGE_INDEX.csv').open(newline='') as stream:
    reader = csv.DictReader(stream)
    columns = reader.fieldnames
    rows = list(reader)
assert len(rows) == 17
for row in rows:
    row['report'] = 'reports/' + row['case'] + '_Test_Report.pdf'
    for key in ('osi', 'results', 'runtime_log', 'report'):
        assert 'Task1/' + row[key] in files, (row['case'], key)
    assert any(name.startswith('Task1/' + row['run_folder']) for name in files)
    for shot in row['screenshots'].split('; '):
        assert 'Task1/' + shot in files, (row['case'], shot)
text = io.StringIO()
writer = csv.DictWriter(text, fieldnames=columns)
writer.writeheader()
writer.writerows(rows)
files['Task1/PACKAGE_INDEX.csv'] = text.getvalue().encode()
files['Task1/README.txt'] = ("""FINAL TASK 1 EVIDENCE PACKAGE

Open reports/Task1_TC01_TC17_Test_Report.pdf for the single combined report
covering TC-01 through TC-17. All 17 individual case reports are also retained
as reports/TC01_Test_Report.pdf through reports/TC17_Test_Report.pdf.
Only the redundant TC-03 through TC-17 overview has been omitted.
PACKAGE_INDEX.csv maps every case to its individual report, saved OSI,
screenshots, results workbook, runtime log and run folder.

All 17 cases have inputs, screenshots, native result workbooks and run records.
The original TC-01 runtime log was never captured; logs/TC01_replay1.log is
from a separately dated replay. The original TC-01 evidence is preserved in
runs/TC01/original. TC-02's original final log is logs/TC02_final.log.

The combined PDF is a test evidence report, not an application-generated full
structural design report. Failed design checks and observed software findings
are recorded in the report and individual case notes. The source checkout
and Conda environment are not bundled.

MANIFEST_SHA256.txt records hashes of all packaged files except itself.
Task1/video/Task1_workflow_recording.mov is a native silent screen recording
captured during the Task 1 workflow.
""").encode()
manifest = ''.join(
    hashlib.sha256(data).hexdigest() + '  ' + name + '\n'
    for name, data in sorted(files.items())
)
files['Task1/MANIFEST_SHA256.txt'] = manifest.encode()

with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
    for name, data in sorted(files.items()):
        archive.writestr(name, data)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    expected_reports = {'Task1/reports/Task1_TC01_TC17_Test_Report.pdf'} | {
        f'Task1/reports/TC{n:02}_Test_Report.pdf' for n in range(1, 18)
    }
    assert {name for name in archive.namelist() if name.startswith('Task1/reports/')} == expected_reports
    with zipfile.ZipFile(source) as original:
        for name in original.namelist():
            if name.startswith(('Task1/logs/', 'Task1/runs/', 'Task1/osi/', 'Task1/screenshots/', 'Task1/results/')) or name in expected_reports:
                assert archive.read(name) == original.read(name), name
    for line in manifest.splitlines():
        digest, name = line.split('  ', 1)
        assert hashlib.sha256(archive.read(name)).hexdigest() == digest
print(output)
print('cases=17 report_pages=21 files=', len(files), 'bytes=', output.stat().st_size)
