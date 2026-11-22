# OsdagBridge Task 3 - Comprehensive Output Verification

Tested against `Nidhikhare12/OsdagBridge` `dev` commit `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`.

## Outcome

- 59 automated comparisons: 50 pass, 9 confirmed failures.
- Three same-session designs retained correct UI/Input/Output values and regenerated distinct CAD and plots.
- All major steel systems and the deck were audited.
- Confirmed defects: four structural girders reported as six (#113); concrete Ecm export (#171); girder geometry exported in metre scale under mm labels; empty end-diaphragm result groups; missing transverse design-check exports.
- Native design-report TeX assembled, but application PDF compilation failed because `pdflatex` was unavailable. The copied TeX also retained temporary image paths.

## Contents

- `evidence/output_verification.json` and `.csv`: 59-check audit.
- `evidence/TC01_results.xlsx`: matching baseline Results Table.
- `scripts/`: reproducible audit, native report generation, and PDF report builder.
- `reports/`: final comprehensive PDF.
- `notes/github_issue_drafts.md`: archived issue bodies plus the two live Task 3 issue links.
- `resume/`: updated resume supplied in Task 2.
- `video/Task3_Testing_Demonstration.mp4`: newly recorded Task 3-only silent demonstration (111.39 s, 1920×1200). It shows the custom girder material, three consecutive same-session runs, regenerated structural plots, and regenerated 3D CAD/deck views.
- `evidence/session_video_redo/`: dictionaries, OSI files, screenshots, CAD images, plots, and session metadata created by the newly recorded run (`TASK3-REDO-VIDEO-02`).

Repository branch: https://github.com/ananditasinha3004/OsdagBridge/tree/codex/task3-comprehensive-output-verification

