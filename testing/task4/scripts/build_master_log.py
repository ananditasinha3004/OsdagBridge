#!/usr/bin/env python3
"""Build the Task 4 master test-case log from the Task 1-3 source logs."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMIT = "d74f56dd7f22925fb8148cabf5740ed8d1e39ff3"

FIELDS = [
    "test_id",
    "phase",
    "category",
    "scenario",
    "session_id",
    "run_number",
    "tested_at",
    "source_commit",
    "exact_parameters",
    "expected_output",
    "actual_output",
    "execution_status",
    "software_verdict",
    "evidence",
    "issue_url",
    "notes",
]

ISSUES = {
    "TC-09": "https://github.com/Nidhikhare12/OsdagBridge/issues/71",
    "TC-11": "https://github.com/Nidhikhare12/OsdagBridge/issues/71",
    "TC-12": "https://github.com/Nidhikhare12/OsdagBridge/issues/71",
    "TC-13": "https://github.com/Nidhikhare12/OsdagBridge/issues/71",
    "TC-14": "https://github.com/Nidhikhare12/OsdagBridge/issues/43",
    "TC-15": "https://github.com/Nidhikhare12/OsdagBridge/issues/43",
    "TC-17": "https://github.com/Nidhikhare12/OsdagBridge/issues/171",
    "T3-XLS-02": "https://github.com/Nidhikhare12/OsdagBridge/issues/171",
    "T3-XLS-03": "https://github.com/ananditasinha3004/OsdagBridge/issues/1",
    "T3-COMP-01": "https://github.com/ananditasinha3004/OsdagBridge/issues/2",
    "T3-COMP-02": "https://github.com/ananditasinha3004/OsdagBridge/issues/2",
    "T3-REPORT-01": "https://github.com/Nidhikhare12/OsdagBridge/issues/172",
}

T3_PARAMETERS = {
    "T3-RUN-01": "span=25 m; skew=0 deg; carriageway=7.5 m; 4 girders; spacing=2.10 m; overhang=1.05 m; deck=250 mm; custom girder Fy/Fu/E=360/510/205 MPa/MPa/GPa",
    "T3-RUN-02": "same session; unlock; span=30 m; skew=+5 deg; other Run 1 inputs retained",
    "T3-RUN-03": "same session; unlock; span=35 m; skew=-5 deg; other Run 1 inputs retained",
    "T3-DICT-01": "Runs 1-3: span/skew/carriageway/material identifier/Fy/Fu/E; 21 UI/Input/Output comparisons",
    "T3-XLS-01": "fresh baseline: span=25 m; carriageway=7.5 m; skew=0 deg; E 350A steel; M40 deck",
    "T3-XLS-02": "same baseline workbook; deck Ecm=33 GPa; steel E=200000 MPa",
    "T3-XLS-03": "same baseline workbook; G1M1-G4M1 D/bf/tf/bf/tf/tw=1390/420/18/420/18/8 mm",
    "T3-COMP-01": "same baseline output dictionary; audit girders, stiffeners, cross bracing, end diaphragms, shear connectors, deck",
    "T3-COMP-02": "same baseline workbook; audit cross-bracing and end-diaphragm demand/capacity/utilization/status exports",
    "T3-GRAPH-01": "Runs 1-3 CAD: 25 m/0 deg, 30 m/+5 deg, 35 m/-5 deg",
    "T3-GRAPH-02": "Runs 1-3 structural plots: 25 m/0 deg, 30 m/+5 deg, 35 m/-5 deg",
    "T3-COUNT-01": "baseline typical_section.no_of_girders=4; deck overhang=1.05 m",
    "T3-REPORT-01": "baseline native report generation from 25 m/0 deg completed design; generated TeX compiled without bundled pdflatex",
}


def portable(value: str) -> str:
    value = value or ""
    value = value.replace(
        "/Users/ananditasinha/Documents/OsdagBridge_FOSSEE/Task1/",
        "testing/task1/",
    )
    value = value.replace("evidence/session_02/", "testing/task2/evidence/session_02/")
    return value


def software_verdict(test_id: str, status: str, actual: str) -> str:
    if test_id in {"TC-09", "TC-11", "TC-12", "TC-13"}:
        return "FAIL - user input silently reverted"
    if test_id in {"TC-14", "TC-15", "TC-17"}:
        return "FAIL - exported values/units mismatch"
    if test_id in {"TC-01", "TC-02"}:
        return "PASS - application completed; engineering design checks failed"
    if test_id.startswith("T2-SETUP"):
        return "HARNESS FAIL - not a product defect"
    if "FAIL" in status.upper():
        return "FAIL"
    if "known" in status.lower():
        return "PASS - execution; known calculation defect present"
    if "finding" in status.lower() or "mismatch" in actual.lower():
        return "FAIL - finding recorded"
    return "PASS"


def task1_rows() -> list[dict[str, str]]:
    rows = []
    with (ROOT / "data/task1/test_log.csv").open(newline="", encoding="utf-8-sig") as stream:
        for source in csv.DictReader(stream):
            test_id = source["test_id"]
            evidence = "; ".join(
                portable(source.get(key, ""))
                for key in ("osi_file", "ui_screenshot", "output_dictionary", "cad_or_plot_evidence", "log_file")
                if source.get(key)
            )
            rows.append({
                "test_id": test_id,
                "phase": "Task 1",
                "category": source["requirement"],
                "scenario": source["scenario"],
                "session_id": source["session_id"],
                "run_number": source["run_number"],
                "tested_at": source["tested_at"],
                "source_commit": source["commit"],
                "exact_parameters": source["parameters"],
                "expected_output": source["expected_result"],
                "actual_output": source["actual_result"],
                "execution_status": "COMPLETED",
                "software_verdict": software_verdict(test_id, source["status"], source["actual_result"]),
                "evidence": evidence,
                "issue_url": source["issue_url"] or ISSUES.get(test_id, ""),
                "notes": portable(source["notes"]),
            })
    return rows


def task2_rows() -> list[dict[str, str]]:
    rows = []
    with (ROOT / "data/task2/test_log.csv").open(newline="", encoding="utf-8-sig") as stream:
        for source in csv.DictReader(stream):
            test_id = source["test_id"]
            rows.append({
                "test_id": test_id,
                "phase": "Task 2",
                "category": "Multi-run/state" if "RUN" in test_id else "Verification",
                "scenario": source["scenario"],
                "session_id": source["session_id"],
                "run_number": source["run_number"],
                "tested_at": "2026-11-22 IST",
                "source_commit": COMMIT,
                "exact_parameters": source["inputs"],
                "expected_output": source["expected"],
                "actual_output": source["actual"],
                "execution_status": "STOPPED BEFORE DESIGN" if "SETUP" in test_id else "COMPLETED",
                "software_verdict": software_verdict(test_id, source["status"], source["actual"]),
                "evidence": portable(source["evidence"]),
                "issue_url": source["issue"],
                "notes": "Same QApplication, main window, and backend for T2-RUN-01 through T2-RUN-03." if "RUN" in test_id else "",
            })
    return rows


def task3_rows() -> list[dict[str, str]]:
    rows = []
    with (ROOT / "data/task3/test_log.csv").open(newline="", encoding="utf-8-sig") as stream:
        for source in csv.DictReader(stream):
            test_id = source["test_id"]
            rows.append({
                "test_id": test_id,
                "phase": "Task 3",
                "category": "Output verification",
                "scenario": source["scenario"],
                "session_id": "TASK3-OUTPUT-AUDIT",
                "run_number": test_id.rsplit("-", 1)[-1] if test_id.startswith("T3-RUN") else "",
                "tested_at": "2026-11-22 IST",
                "source_commit": COMMIT,
                "exact_parameters": T3_PARAMETERS[test_id],
                "expected_output": source["expected"],
                "actual_output": source["actual"],
                "execution_status": "COMPLETED",
                "software_verdict": software_verdict(test_id, source["status"], source["actual"]),
                "evidence": f"testing/task3/{source['evidence']}",
                "issue_url": source["issue"] if source["issue"].startswith("http") else ISSUES.get(test_id, ""),
                "notes": "59 atomic checks are retained in data/task3/output_verification.csv." if test_id == "T3-DICT-01" else "",
            })
    return rows


def main() -> None:
    rows = task1_rows() + task2_rows() + task3_rows()
    assert len(rows) == 36, f"expected 36 master records, got {len(rows)}"
    assert len({row['test_id'] for row in rows}) == len(rows), "duplicate test IDs"
    for row in rows:
        missing = [field for field in ("test_id", "scenario", "exact_parameters", "expected_output", "actual_output", "software_verdict") if not row[field]]
        assert not missing, f"{row['test_id']} is missing {missing}"

    with (ROOT / "test_log.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    (ROOT / "test_log.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(rows)} records to {ROOT / 'test_log.csv'}")


if __name__ == "__main__":
    main()
