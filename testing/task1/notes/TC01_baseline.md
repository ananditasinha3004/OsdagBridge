# TC-01 baseline design: observed record

Date: 2026-11-21 (IST)
Source commit: `d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`
Input file: `../osi/TC01_baseline.osi`

## Input values confirmed in the saved OSI

- Location: Bhagalpur, Bihar
- Structure: Highway Bridge (visible in the initial Basic Inputs screen)
- Span: 25 m; carriageway width: 7.5 m; median: No; footpath: None; skew: 0 degrees
- Design type: Optimized
- Girder, cross bracing, and end diaphragm: E 350A; deck: M40
- Typical section: 4 girders, 2.10 m girder spacing, 1.05 m deck overhang, 8.40 m overall bridge width, 250 mm deck thickness

The Additional Geometry screenshot shows the selected Typical Section Details tab and only part of its lower fields. The OSI includes additional default input values, which should be reviewed before making a claim that every advanced setting was visually checked.

## Observed outcome

- The application displayed `Saved OSI Successfully!`.
- The analysis progress window reached stage 14/14, 100%, and displayed `ANALYSIS COMPLETE`; the displayed total solution time was 11.95 seconds.
- A 3D bridge CAD model rendered after analysis.
- The Output Dock populated. For girder G1 under load case `SW`, visible indicators show flexure 1%, shear 3%, interaction 1%, lateral torsional buckling 20%, resistance to longitudinal shear 24%, and stress limitation 2%. The upper and lower screenshots do not show every result or an explicit overall pass/fail statement.
- The Girder Analysis and Design Results Summary opened for Girder 1 / SW. Its Details tab shows E 350A welded section `1390 x 420 x 18 x 420 x 18`, section class Slender, total depth 1390 mm, web thickness 8 mm, and top/bottom flange width 420 mm and thickness 18 mm. The Design Check tab was not shown.
- The Generate Results Table selection dialog and Design Report setup dialog opened. No generated table or report was shown in the supplied screenshots.
- The Girder 1 / SW Design Check tab shows `PASS`, with 8 checks listed, 6 passed, and 0 failed. This is a check for one member/load case, not the overall design verdict.
- `../results/TC01_results.xlsx` was generated with 36 sheets. Its Bridge Configuration Summary agrees with the saved OSI on span 25 m, overall width 8.4 m, 4 girders, spacing 2.1 m, overhang 1.05 m, and skew 0 degrees. Its steel and concrete material sheets show E 350A and M40, matching the OSI grades.
- The workbook's Design Results Summary marks all four girders `FAIL`, controlled by Fatigue Normal Stress under `SLS_FREQUENT_1`. Utilization ratios are 1.967, 1.979, 1.998, and 1.998. The Fatigue Assessment sheet independently lists all four as `FAIL` (stress ranges 181.93-184.84 MPa versus 92.49 MPa limit).
- The Deflection - Total Load sheet lists all four girders as `FAIL`: 56.28-56.70 mm versus the L/600 limit of 41.7 mm.
- These failures are observed design outcomes for this input combination. They do not by themselves establish a software bug.
- The screenshots do not establish whether every design check passed, whether the Output Dictionary matches the displayed report, or whether structural plots are correct. Those checks remain open.

## Evidence

- `../screenshots/TC01_basic_inputs_materials.png`
- `../screenshots/TC01_location.png`
- `../screenshots/TC01_additional_geometry.png`
- `../screenshots/TC01_osi_saved.png`
- `../screenshots/TC01_analysis_complete.png`
- `../screenshots/TC01_3d_cad.png`
- `../screenshots/TC01_output_dock_upper.png`
- `../screenshots/TC01_output_dock_lower.png`
- `../screenshots/TC01_girder_summary_details.png`
- `../screenshots/TC01_results_table_selection.png`
- `../screenshots/TC01_report_setup.png`
- `../screenshots/TC01_girder_design_check_SW.png`
- `../screenshots/TC01_report_sections.png`
- `../results/TC01_results.xlsx`

## Next check

Finish generating the application report if needed, then compare representative workbook values with the report. Record the overall design as failed under fatigue and total-load deflection while noting that analysis and rendering completed. Keep the current session open if proceeding to consecutive-run testing.
