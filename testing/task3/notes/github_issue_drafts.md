# Task 3 GitHub issue drafts

The GitHub connector could read issues but returned `403 Resource not accessible by integration` for issue creation on both the upstream repository and the fork. These drafts are ready to paste upstream.

## Girder Section Properties workbook labels metre-normalized values as mm

On `dev` commit `d74f56d`, the exported **Girder Section Properties** worksheet labels dimensions in mm but writes metre-scale values for G1M1-G4M1: depth `1.39` instead of `1390`, flange width `0.42` instead of `420`, flange thickness `0.02` instead of `18`, and web thickness `0.01` instead of `8`. The Output Dictionary and Design Summary retain the correct final mm values.

Root cause: `generate_results_values_builder.py::resolve_girder_section_properties()` reads normalized per-girder keys through `_dim()` unchanged while the columns are labelled mm. Use canonical `design_results` `*_mm` values or explicitly convert normalized SI values at export. Add a regression asserting exported G1 geometry equals `D_mm`, `bf_top_mm`, `tf_top_mm`, and `tw_mm`. Upstream #82 and #171 concern different material-property unit fields.

## Fresh baseline has empty end-diaphragm results and no transverse check export

A fresh 25 m / 7.5 m / 0 degree optimized design renders end diaphragms and exports section-property rows, but `end_diaphragm_design_results` contains three empty pair dictionaries and `end_diaphragm_forces_dict["pairs"]` is empty. The workbook contains transverse section definitions but no cross-bracing/end-diaphragm demand-capacity-utilization-status sheets.

Root cause direction: `_design_end_diaphragm_members()` silently returns empty pair results when support-edge elements do not map to result-data girders and therefore creates no design jobs. Normalize node identifiers, assert every configured pair maps to start/end elements, and treat zero design jobs as an error. Add workbook/report result resolvers. Upstream #199 has a stale-state/OSI-load trigger; this reproduction is a fresh-process baseline.

