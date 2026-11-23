# Tasks 1-5 Artifact Coverage Audit

This audit reconciles the final repository and ZIP against the original work
created across the separate Task 1, Task 2, Task 3, Task 4, and Task 5 working
folders.

## Recovered during final consolidation

- Task 1: 37 runtime/log files from the TC01-TC17 executions.
- Task 2: 100 files from two additional preserved multi-run evidence sessions
  and updated report-render QA pages.
- Task 3: the native-report `generation.log`, in addition to the already
  consolidated dictionaries, OSI files, workbooks, CAD, plots, reports, and
  fresh-session evidence.
- Tasks 4-5: 62 files from the earlier fresh same-session run and the final
  recording/reverification QA frame sets.

## Included categories

- Project source, tests, documentation, examples, and configuration.
- All preserved OSI inputs and saved run inputs.
- Input, UI-state, and output dictionaries in JSON form.
- Result workbooks, CSV logs, master logs, review files, and runtime logs.
- GUI input screenshots, custom-property dialogs, unlock states, status
  messages, design views, 3D CAD images, structural plots, output docks, and
  report/recording QA frames.
- Individual task reports, the detailed Tasks 1-5 report, the full screenshot
  appendix, reproduction scripts, issue drafts/maps, and validation scripts.
- A repository-wide SHA-256 manifest.

## Deliberate exclusions

- Resume/CV files: submitted separately, as requested.
- Raw `.mov`, `.mp4`, `.m4v`, and `.webm` recordings and failed-capture QA
  frames: uploaded/reviewed separately, as requested, and not part of the
  structural-test evidence ZIP.
- Old task ZIPs and nested copies of the final repository: redundant and would
  consume the upload limit without adding evidence.
- macOS `.DS_Store`, Python cache files, and temporary render directories.
- Redundant PDF-page render PNGs and composite contact sheets where the source
  PDF or every underlying full-resolution frame is already included. These are
  omitted only to remain below the portal's 100 MB ZIP limit.
- Exact duplicate screenshot payloads in the PDF appendix. One captioned source
  is embedded in the PDF; all non-duplicate evidence files remain in the ZIP.

The PDF is intentionally a readable evidence report rather than a binary file
dump. Machine-readable originals and full-resolution images are retained in the
ZIP and repository, while the PDF presents the findings, comparisons, tables,
and captioned visual evidence within the 10 MB form limit.
