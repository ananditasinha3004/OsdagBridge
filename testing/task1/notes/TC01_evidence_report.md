# TC01: 25 m baseline

Original user-operated TC-01 run, 21 November 2026. The original full runtime log and output dictionary were not captured. Original screenshots include analysis completion. See ../replay1 for a separately dated fresh execution with its own real runtime log and dictionaries. Replay evidence must not be attributed to the original run.


Source commit: d74f56dd7f22925fb8148cabf5740ed8d1e39ff3.

## Bridge Configuration Summary

| Overall Width (m) | Span (m) | No. of Girders | Girder Spacing (m) | Deck Overhang (m) | Skew Angle (deg) |
|---|---|---|---|---|---|
| 8.4 | 25 | 4 | 2.1 | 1.05 | 0 |

## Design Results Summary

| Member | Controlling Load Case / Combination | Controlling Design Check | Demand | Capacity | Utilization Ratio | Status |
|---|---|---|---|---|---|---|
| G1M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 181.93 MPa | 92.49 MPa | 1.967 | FAIL |
| G2M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 183.06 MPa | 92.49 MPa | 1.979 | FAIL |
| G3M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 184.84 MPa | 92.49 MPa | 1.998 | FAIL |
| G4M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 184.84 MPa | 92.49 MPa | 1.998 | FAIL |

## Fatigue Assessment - Girder

| Girder | Stress Range, Δσ (MPa) | Fatigue Limit, ffd (MPa) | Utilization Ratio | Status |
|---|---|---|---|---|
| G1M1 | 181.93 | 92.49 | 1.97 | FAIL |
| G2M1 | 183.06 | 92.49 | 1.98 | FAIL |
| G3M1 | 184.84 | 92.49 | 2 | FAIL |
| G4M1 | 184.84 | 92.49 | 2 | FAIL |

## Deflection - Total Load

| Girder | Total Deflection, δₜₒₜₐₗ (mm) | Permissible Limit | Utilization Ratio | Status |
|---|---|---|---|---|
| G1 | 56.28 | L/600 = 41.7 mm | 1.351 | FAIL |
| G2 | 56.7 | L/600 = 41.7 mm | 1.361 | FAIL |
| G3 | 56.7 | L/600 = 41.7 mm | 1.361 | FAIL |
| G4 | 56.28 | L/600 = 41.7 mm | 1.351 | FAIL |

## Replay

TC-01 evidence-completion replay. Started 2026-11-22T08:29:31.632542+05:30; finished 2026-11-22T08:29:51.439666+05:30. Source commit d74f56dd7f22925fb8148cabf5740ed8d1e39ff3. This log was captured live during this replay, not the original manual test.

[Live replay log](../logs/TC01_replay1.log). Original evidence remains in runs/TC01/original.
