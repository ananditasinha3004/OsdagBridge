# Task 1: TC-03 through TC-17

All 15 cases executed on 21 November 2026 (IST). Documentation reviewed on 22 November 2026. All runs produced OSI files, before/after input snapshots, output dictionaries, native 36-sheet results workbooks, screenshots, CAD images and runtime logs.

11/15 cases retained every requested value in the saved input and output dictionary. Four additional-input cases failed retention. Three material cases had export discrepancies despite retaining their inputs. Every run has at least one failed member in the native overall Design Results Summary.

| Case | Scenario | Input retention | Finding | Record |
|---|---|---|---|---|
| TC-03 | Span 45 m | PASS | None recorded | [Case record](TC03.md) |
| TC-04 | Carriageway width 4.25 m | PASS | None recorded | [Case record](TC04.md) |
| TC-05 | Carriageway width 23.6 m | PASS | None recorded | [Case record](TC05.md) |
| TC-06 | Skew -15 degrees | PASS | None recorded | [Case record](TC06.md) |
| TC-07 | Skew +15 degrees | PASS | None recorded | [Case record](TC07.md) |
| TC-08 | Median and footpaths on both sides | PASS | None recorded | [Case record](TC08.md) |
| TC-09 | Deck thickness 275 mm | FAIL | F01 | [Case record](TC09.md) |
| TC-10 | Custom G1M1 stiffener spacing 1800 mm | PASS | None recorded | [Case record](TC10.md) |
| TC-11 | Seismic damping 5% | FAIL | F01 | [Case record](TC11.md) |
| TC-12 | Deck top cover 60 mm | FAIL | F01 | [Case record](TC12.md) |
| TC-13 | Fatigue strength factor 1.25 | FAIL | F01 | [Case record](TC13.md) |
| TC-14 | Custom girder steel | PASS | F02 | [Case record](TC14.md) |
| TC-15 | Custom bracing and diaphragm steel | PASS | F02 | [Case record](TC15.md) |
| TC-16 | Custom G1M1 stiffener thicknesses | PASS | None recorded | [Case record](TC16.md) |
| TC-17 | Custom concrete deck | PASS | F03 | [Case record](TC17.md) |

## Method and limits

Each case starts in a fresh Qt desktop process from TC01_baseline.osi. The driver edits real widgets, emits their normal edit signals, invokes the application Save and Design handlers, and exports Select All results through the native exporter. Message boxes are recorded and acknowledged automatically. No solver or exporter results are substituted. CAD images are dumped from the live OpenCascade viewer because ordinary Qt window captures omit the native graphics surface.

These are Task 1 software-testing records. A completed run does not mean every structural check passed. Saved dictionaries establish retention, not independent verification that every calculation consumes every custom value. Full application design-report PDFs, structural-plot accuracy, same-session consecutive runs, screen recording, issue publication and final assignment submission remain separate work.

## Evidence locations

- `../runs/TC03/attempt1/` through `../runs/TC17/attempt1/`: authoritative completed runs.
- `../results/test_log.csv`: full TC-01 through TC-17 index.
- `../results/TC03_TC17_review.json`: extracted comparisons and native table values.
- `../reports/Task1_TC03_TC17_Test_Report.pdf`: readable testing report, not the application-generated structural design report.
- `findings_TC03_TC17.md`: observed defects, source locations and proposed fixes.

Earlier partial geometry-run artifacts outside `runs/` are preserved but are not the evidence used for these results. No GitHub issues were posted and no application source was edited.
