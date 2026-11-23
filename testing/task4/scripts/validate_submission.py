#!/usr/bin/env python3
"""Validate the consolidated Tasks 1-5 report and repository-wide ZIP."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[3]
ROOT = REPO_ROOT / "testing/task4"
PDF = ROOT / "reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf"
ZIP_PATH = ROOT / "dist/OsdagBridge_Final_Submission.zip"
MANIFEST = REPO_ROOT / "testing/FINAL_SUBMISSION_MANIFEST_SHA256.txt"
VIDEO_SESSION = ROOT / "evidence/session_video_task4_fresh_02/session.json"

required = [
    ROOT / "README.md",
    ROOT / "test_log.csv",
    ROOT / "test_log.json",
    ROOT / "notes/findings_and_issue_map.md",
    ROOT / "data/task3/output_verification.csv",
    ROOT / "data/task3/output_verification.json",
    VIDEO_SESSION,
    PDF,
    ZIP_PATH,
    MANIFEST,
]
missing = [str(path) for path in required if not path.is_file() or path.stat().st_size == 0]
assert not missing, f"missing/empty required files: {missing}"

rows = list(csv.DictReader((ROOT / "test_log.csv").open(encoding="utf-8")))
assert len(rows) == 36
assert len({row["test_id"] for row in rows}) == 36
for row in rows:
    for field in ("scenario", "exact_parameters", "expected_output", "actual_output", "software_verdict"):
        assert row[field].strip(), f"{row['test_id']} missing {field}"
verdicts = Counter("HARNESS" if r["software_verdict"].startswith("HARNESS") else "FAIL" if r["software_verdict"].startswith("FAIL") else "PASS" for r in rows)
assert verdicts == {"PASS": 21, "FAIL": 14, "HARNESS": 1}

json_rows = json.loads((ROOT / "test_log.json").read_text())
assert [row["test_id"] for row in json_rows] == [row["test_id"] for row in rows]

audit = json.loads((ROOT / "data/task3/output_verification.json").read_text())
assert (audit["checks_total"], audit["pass"], audit["fail"]) == (59, 50, 9)
assert len(audit["checks"]) == 59

osi_files = list((ROOT / "osi").rglob("*.osi"))
assert len(osi_files) >= 20, f"only {len(osi_files)} OSI files"

reader = PdfReader(str(PDF))
assert len(reader.pages) == 21
text = "\n".join(page.extract_text() or "" for page in reader.pages)
for phrase in (
    "all five assignment tasks",
    "Executive Summary",
    "UI vs Input/Output Dictionaries",
    "3D CAD Generation Across Runs",
    "Live GitHub Issues and Code-Level Fix Map",
    "Submission Package and Reproducibility",
):
    assert phrase in text, phrase
assert not re.search(r"TODO|PLACEHOLDER|turn\d+(?:search|fetch)", text, re.I)

uris = []
for page in reader.pages:
    for annot_ref in page.get("/Annots", []):
        annot = annot_ref.get_object()
        action = annot.get("/A")
        if action and action.get("/URI"):
            uris.append(str(action.get("/URI")))
for issue in ("issues/43", "issues/71", "issues/113", "issues/171", "issues/172", "issues/257", "issues/267"):
    assert any(issue in uri for uri in uris), issue

video_session = json.loads(VIDEO_SESSION.read_text())
assert video_session["session_id"] == "TASK4-FRESH-VIDEO-01"
assert video_session["status"] == "execution_completed"
assert len(video_session["runs"]) == 3
for flag in ("same_process_all_runs", "same_window_all_runs", "same_backend_all_runs"):
    assert video_session[flag] is True, flag
for index, run in enumerate(video_session["runs"], 1):
    assert run["run_number"] == index
    assert (VIDEO_SESSION.parent / f"run_{index}/TASK4_video_run_{index}.osi").is_file()

manifest_entries = {}
for line in MANIFEST.read_text().splitlines():
    digest, relative = line.split("  ", 1)
    manifest_entries[relative] = digest
for relative, expected in manifest_entries.items():
    path = REPO_ROOT / relative
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, relative

with zipfile.ZipFile(ZIP_PATH) as archive:
    assert archive.testzip() is None
    names = set(archive.namelist())
    prefix = "OsdagBridge_Final_Submission/"
    for relative in (
        "pyproject.toml",
        "src/osdagbridge/cli/commands.py",
        "testing/task4/README.md",
        "testing/task4/test_log.csv",
        "testing/task4/reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf",
        "testing/FINAL_SUBMISSION_MANIFEST_SHA256.txt",
    ):
        assert prefix + relative in names
    assert sum(name.endswith(".osi") for name in names) >= 20
    assert not any(name.lower().endswith((".mp4", ".mov", ".m4v")) for name in names)
    assert not any("resume" in name.lower() or name.lower().endswith("/cv.pdf") for name in names)

print("Tasks 1-5 final submission validation PASS")
print(f"Records: {len(rows)} ({dict(verdicts)})")
print(f"Atomic checks: {audit['checks_total']} ({audit['pass']} pass, {audit['fail']} fail)")
print(f"PDF: {len(reader.pages)} pages, {len(uris)} link annotations")
print(f"OSI files: {len(osi_files)}")
print(f"ZIP entries: {len(names)}")
print(f"Fresh video session: {video_session['session_id']} ({len(video_session['runs'])} runs)")

