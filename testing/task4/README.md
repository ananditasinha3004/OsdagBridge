# OsdagBridge Tasks 1-5 - Final Consolidated Submission

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

- Single consolidated Tasks 1-5 PDF:
  `reports/OsdagBridge_Tasks_1_to_5_Comprehensive_Testing_Report.pdf`
- Master logs: `test_log.csv` and `test_log.json`
- Atomic output audit: `data/task3/output_verification.csv` and `.json`
- Complete repository and evidence ZIP: `dist/OsdagBridge_Final_Submission.zip`
- Test inputs: `osi/task1/` and `osi/multirun/`
- Reproducible scripts: `scripts/`
- Video demonstration: retained outside the repository for later YouTube
  publication.
- Fresh recording evidence: `evidence/session_video_task4_fresh_02/`
  (custom material plus three consecutive same-process runs, plots, and 3D CAD)

Repository branch:
https://github.com/ananditasinha3004/OsdagBridge/tree/dev

Repository access: `Nidhikhare12` was verified as a direct collaborator in
GitHub repository settings on 23 November 2026 (IST).

## Live bug reports

- https://github.com/Nidhikhare12/OsdagBridge/issues/71
- https://github.com/Nidhikhare12/OsdagBridge/issues/43
- https://github.com/Nidhikhare12/OsdagBridge/issues/171
- https://github.com/Nidhikhare12/OsdagBridge/issues/113
- https://github.com/Nidhikhare12/OsdagBridge/issues/172
- https://github.com/Nidhikhare12/OsdagBridge/issues/257
- https://github.com/Nidhikhare12/OsdagBridge/issues/267

Issue #267 was created after an open-and-closed duplicate search. The skew=0
end-diaphragm evidence was added to existing issue #257 rather than duplicated.
Evidence-backed comments were also added to #71, #43, #171, and #172; the
same-session reproduction was already posted to #113. Each issue is mapped to
reproduced evidence, affected files, and a suggested code-level correction in
`notes/findings_and_issue_map.md` and Section 15 of the PDF.

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
OSI presence, archive integrity, exclusion of videos, and the SHA-256 manifest.

