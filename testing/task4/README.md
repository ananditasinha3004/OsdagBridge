# OsdagBridge Task 4 - Comprehensive Test-Case Documentation

Tested against `Nidhikhare12/OsdagBridge` branch `dev`, commit
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`.

## Outcome

- 36 master test/check records: 21 software PASS, 14 software FAIL, and one
  harness-only failure that stopped before Design.
- 20 completed solver designs: 17 independent Task 1 cases and three
  consecutive designs in one application session.
- 59 atomic output comparisons: 50 PASS and 9 FAIL.
- UI/Input/Output values matched for all selected fields in the three-run
  sequence; the custom girder Fy/Fu/E values remained 360/510/205.
- Every CAD and plot export in the sequence was non-empty and distinct.
- The critical 4-input-girders versus 6-design-girders defect was reproduced
  in every multi-run design.

An application run that completes but reports an engineering code-check FAIL
is classified as a software execution PASS. Silent input replacement, data
mismatch, missing output, and calculation-count inconsistency are software
FAIL results.

## Deliverables

- Comprehensive PDF:
  `reports/Task4_Comprehensive_Test_Case_Documentation.pdf`
- Master logs: `test_log.csv` and `test_log.json`
- Atomic output audit: `data/task3/output_verification.csv` and `.json`
- ZIP package: `dist/OsdagBridge_Task4_Submission.zip`
- Test inputs: `osi/task1/` and `osi/multirun/`
- Reproducible scripts: `scripts/`
- Fresh Task 4 demonstration: `video/Task4_Testing_Demonstration.mp4`
  (128.70 s, 1920 x 1200, H.264; session `TASK4-FRESH-VIDEO-01`)
- Fresh recording evidence: `evidence/session_video_task4_fresh_02/`
  (custom material plus three consecutive same-process runs, plots, and 3D CAD)

Repository branch:
https://github.com/ananditasinha3004/OsdagBridge/tree/codex/task4-test-case-documentation

Repository access: `Nidhikhare12` was verified as a direct collaborator in
GitHub repository settings on 23 November 2026 (IST).

Video:
https://github.com/ananditasinha3004/OsdagBridge/blob/codex/task4-test-case-documentation/testing/task4/video/Task4_Testing_Demonstration.mp4

## Live bug reports

- https://github.com/Nidhikhare12/OsdagBridge/issues/71
- https://github.com/Nidhikhare12/OsdagBridge/issues/43
- https://github.com/Nidhikhare12/OsdagBridge/issues/171
- https://github.com/Nidhikhare12/OsdagBridge/issues/113
- https://github.com/Nidhikhare12/OsdagBridge/issues/172
- https://github.com/ananditasinha3004/OsdagBridge/issues/1
- https://github.com/ananditasinha3004/OsdagBridge/issues/2

Each issue is mapped to reproduced evidence, affected files, and a suggested
code-level correction in `notes/findings_and_issue_map.md` and Section 15 of
the PDF.

## Rebuild and validation

From `testing/task4` in an environment containing ReportLab, Pillow, pypdf,
and Poppler:

```sh
python scripts/build_master_log.py
python scripts/build_report.py
python scripts/build_submission.py
python scripts/validate_submission.py
```

The report was rendered page-by-page with Poppler and visually reviewed. The
validator checks record counts, required fields, PDF readability and links,
MP4 signature, OSI presence, archive integrity, and the SHA-256 manifest.

