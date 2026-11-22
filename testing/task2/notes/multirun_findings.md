# Task 2 multi-run findings

## Scope and method

The successful session used one process (PID 15336), one `CustomWindow` object,
and one `PlateGirderBridge` backend object for all three runs. It drove the real
PySide6 widgets and signals, native Save and Design handlers, lock-button unlock,
Matplotlib plot widget, and OpenCascade CAD renderer. The source checkout was
unmodified at `d74f56d`; an unrelated untracked `results.xlsx` was left alone.

## Run comparison

| Run | UI span/skew | Input dictionary | Output dictionary | Mesh | Selected design values |
|---|---|---|---|---|---|
| 1 | 25 m / 0 deg | `"25"` / `"0"` | `25` / `0` | 108 nodes, 192 members | D=1390 mm, Mu=1639.20 kNm, Vu=236.91 kN |
| 2 | 30 m / +5 deg | `"30"` / `"5"` | `30` / `5` | 126 nodes, 225 members | D=1670 mm, Mu=2193.19 kNm, Vu=306.92 kN |
| 3 | 35 m / -5 deg | `"35"` / `"-5"` | `35` / `-5` | 144 nodes, 258 members | D=1950 mm, Mu=2770.54 kNm, Vu=442.77 kN |

The custom girder identifier and properties stayed consistent in UI/input/output:
`custom_steel_360_510`, Fy 360 MPa, Fu 510 MPa, E 205 GPa. The plot dataset
object changed each run, and all CAD and plot SHA-256 hashes were different.

## Unlock/state checks

After both unlock actions:

- `input_dock.is_locked == False`;
- `backend.output_dict` was empty;
- `plots_widget._ds_all is None`;
- the replacement blank plot figure contained zero axes;
- the UI remained responsive and accepted the next span/skew edits.

No stale result dictionary, prior plot dataset, crash, or timeout was observed in
this three-run geometry/material-retention scenario. This does not close the
broader stale-segment/custom-material scenario in upstream issue #125 because
that issue changes girder count and switches back from custom to standard grades.

## Confirmed defect and code path

All runs have `typical_section.no_of_girders = 4`, and the UI/CAD show four
structural girders, but `output_dict["design_results"]["n_girders"] == 6`.
This independently reproduces upstream issue #113.

Code path at the tested commit:

1. `plategirderbridge.py:_build_dtos()` sets `n_l = no_of_girders + 2` when the
   deck has overhang, adding two deck-edge grid lines.
2. `designer.py:DesignConfig.from_plate_girder_bridge()` assigns
   `n_girders = geom.n_l` instead of `bridge._girder_count()`.
3. Those edge lines are also given a full girder section, so this is not only a
   display-label error; it can distribute demand across six girder-stiff lines.

Suggested correction: model edge longitudinal lines as deck strips, pass
`edge_dist` into analysis-result naming, and set the design/report girder count
from `bridge._girder_count()`. Add a regression asserting that a 4-girder bridge
has exactly G1-G4 design rows and that edge lines are EB1/EB2, not girders.

## Existing issue map

- #113: deck-edge lines treated and designed as girders (reproduced here).
- #125: stale segment lengths/materials in a broader consecutive-run sequence.
- #71: Save Input overwrites committed additional inputs with defaults.
- #92: normal pipeline does not create thermal load cases; warnings appeared in
  every Task 2 design run.
- #43: custom cross-bracing/end-diaphragm grades stored but not used in design.
- #148: concrete Ecm GPa/MPa mismatch in deck SLS checks.
- #171: concrete export labels GPa values as MPa and inflates modular ratio.

## Visual review

The three CAD exports are complete and readable, with deck, crash barriers,
girders, bracing, stiffeners, and supports visible. Apparent bridge length/skew
changes between runs, and image hashes differ. The three plot exports are also
non-empty and distinct; mesh density increases with span. No prior model was
superimposed after rerun. The black central canvas captured immediately after
unlock is the expected cleared 3D view, not a failed render.
