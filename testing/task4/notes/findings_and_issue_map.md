# Task 4 findings and live issue map

All observations below were made at `dev` commit
`d74f56dd7f22925fb8148cabf5740ed8d1e39ff3`. Existing upstream issues are
linked instead of duplicated. Two distinct Task 3 export/coverage findings
were published on the fork.

## F01 - User-controlled additional inputs revert during Save

Reproduced by TC-09, TC-11, TC-12, and TC-13:

| Field | UI/before Save | Saved, after Design, output |
|---|---:|---:|
| Deck thickness | 275 mm | 250 mm |
| Seismic damping | 5% | 2% |
| Deck top cover | 60 mm | 50 mm |
| Fatigue gamma_mf | 1.25 | 1.35 |

Likely source: `desktop/ui/template_page.py` calls
`solve_extend_basic_input_dict` during Save, and default-update helpers in
`core/bridge_types/plate_girder/defaults.py` overwrite present values.

Suggested fix: insert defaults only when keys are missing. Keep derived
geometry recomputation separate from user-controlled default assignment. Add
Save/reload/Design regressions for all four fields.

Live report: https://github.com/Nidhikhare12/OsdagBridge/issues/71

## F02 - Steel export reuses girder properties for other components

TC-14 retained custom girder Fy/Fu 360/510 MPa but exported those numbers for
bracing and diaphragm rows. TC-15 retained bracing 300/450 and diaphragm
320/470 MPa but exported 350/490 for both.

Likely source:
`desktop/ui/dialogs/generate_results_values_builder.py` obtains one
`steel_prop` and reuses it for all component rows.

Suggested fix: resolve girder, bracing, and diaphragm material objects
independently, convert units explicitly, and test three different component
materials in one workbook.

Live report: https://github.com/Nidhikhare12/OsdagBridge/issues/43

## F03 - Concrete export mixes GPa and MPa and ignores density

TC-17 retained Ecm 35 GPa and density 24 kN/m3 but exported Ecm 35 under an
MPa label, density 25, and an inflated modular ratio. The Task 3 baseline also
exported Ecm 33 under MPa and Es/Ecm = 6060.61 instead of about 6.06.

Suggested fix: convert Ecm to MPa before display and before Es/Ecm, and export
the selected material density instead of a hardcoded value.

Live report: https://github.com/Nidhikhare12/OsdagBridge/issues/171

## F04 - Deck-edge lines are assigned and designed as girders

All three same-session runs have four structural girders in the input and CAD,
but `design_results.n_girders` equals six. The positive-overhang grillage adds
two edge lines, gives them full girder stiffness, and passes the total
longitudinal-line count into the girder designer. This can distribute demand
across six girder-stiff lines and is potentially unconservative.

Suggested fix:

- In `plategirderbridge.py`, model edge longitudinal lines as slab strips and
  pass `edge_dist` when constructing analysis results.
- In `designer.py`, use `bridge._girder_count()` and exclude EB1/EB2 from
  per-girder design loops.
- Add a four-girder regression that asserts exactly G1-G4 design rows and a
  self-weight demand close to the expected per-physical-girder value.

Live report: https://github.com/Nidhikhare12/OsdagBridge/issues/113

## F05 - Girder dimensions are exported in metres under mm labels

The baseline Output Dictionary contains D/bf/tf/bf/tf/tw =
1390/420/18/420/18/8 mm. The workbook writes
1.39/0.42/0.02/0.42/0.02/0.01 while retaining mm headings for G1M1-G4M1.

Suggested fix: in
`generate_results_values_builder.py::resolve_girder_section_properties`, use
canonical `design_results` `*_mm` fields or convert normalized SI values back
to millimetres before export. Add an exact workbook regression.

Live report: https://github.com/ananditasinha3004/OsdagBridge/issues/1

## F06 - Empty end-diaphragm results and missing transverse checks

The baseline has three configured adjacent-girder diaphragm pairs but zero
non-empty diaphragm design results. The workbook exports cross-bracing and
end-diaphragm section-property sheets without demand, capacity, utilization,
or status sheets.

Suggested fix: normalize node identifiers in `_design_end_diaphragm_members`,
assert every configured pair maps to start/end elements, treat zero design
jobs as an error, and add workbook/report result resolvers for both transverse
systems.

Live report: https://github.com/ananditasinha3004/OsdagBridge/issues/2

## F07 - Native LaTeX report does not produce a portable PDF

The generated TeX retained temporary image paths and the tested environment
did not contain `pdflatex`. Upstream issue #172 also documents malformed
captioned `longtable` syntax that can stop compilation even when TeX is
installed.

Suggested fix: copy report assets into a self-contained output directory,
terminate every `longtable` caption row correctly, and add a clean-environment
PDF compilation test.

Live report: https://github.com/Nidhikhare12/OsdagBridge/issues/172

