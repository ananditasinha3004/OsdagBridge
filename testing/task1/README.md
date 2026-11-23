# OsdagBridge Task 1 - Input and Customization Testing

Task 1 covers TC-01 through TC-17 for basic geometry, boundary values,
additional inputs, custom member configuration, custom steel properties, and
custom concrete-deck properties. Both successful executions and confirmed
retention/export failures are preserved.

## Primary files

- `reports/Task1_TC01_TC17_Test_Report.pdf`: consolidated 21-page report.
- `results/test_log.csv`: master test-case index with inputs, expected/actual
  results, statuses, evidence paths, and issue mappings.
- `PACKAGE_INDEX.csv`: per-case map of OSI, report, workbook, log, run folder,
  and screenshots.
- `osi/`: submitted test-case input files.
- `runs/`: raw per-attempt dictionaries, screenshots, CAD, plots, workbooks,
  and run metadata.
- `notes/`: per-case observations and consolidated findings.
- `scripts/`: repeatable execution, review, documentation, and repair helpers.
- `MANIFEST_SHA256.txt`: checksums for every committed Task 1 file except the
  manifest itself.

## Video note

The original Task 1 MOV is intentionally excluded because it is larger than
GitHub's normal single-file limit. The final branch retains its generated OSI
and output evidence under `video/evidence/`. Use the Task 3 demonstration as the
form submission video; it covers the required custom-material, consecutive-run,
plot, and 3D-CAD workflow.
