# TC02: 20 m span

Original TC-02 Qt desktop run. runtime.log is an exact copy of logs/TC02_final.log. Before/after input snapshots were not captured by that earlier driver. No files in this original folder are a replay.


Source commit: d74f56dd7f22925fb8148cabf5740ed8d1e39ff3.

## Bridge Configuration Summary

| Overall Width (m) | Span (m) | No. of Girders | Girder Spacing (m) | Deck Overhang (m) | Skew Angle (deg) |
|---|---|---|---|---|---|
| 8.4 | 20 | 4 | 2.1 | 1.05 | 0 |

## Design Results Summary

| Member | Controlling Load Case / Combination | Controlling Design Check | Demand | Capacity | Utilization Ratio | Status |
|---|---|---|---|---|---|---|
| G1M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 197.76 MPa | 92.49 MPa | 2.138 | FAIL |
| G2M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 199.82 MPa | 92.49 MPa | 2.16 | FAIL |
| G3M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 204.88 MPa | 92.49 MPa | 2.215 | FAIL |
| G4M1 | SLS_FREQUENT_1: 1.0DL + 1.2DW + 0.75LL + 0.5WL | Fatigue Normal Stress | 204.88 MPa | 92.49 MPa | 2.215 | FAIL |

## Fatigue Assessment - Girder

| Girder | Stress Range, Δσ (MPa) | Fatigue Limit, ffd (MPa) | Utilization Ratio | Status |
|---|---|---|---|---|
| G1M1 | 197.76 | 92.49 | 2.14 | FAIL |
| G2M1 | 199.82 | 92.49 | 2.16 | FAIL |
| G3M1 | 204.88 | 92.49 | 2.22 | FAIL |
| G4M1 | 204.88 | 92.49 | 2.22 | FAIL |

## Deflection - Total Load

| Girder | Total Deflection, δₜₒₜₐₗ (mm) | Permissible Limit | Utilization Ratio | Status |
|---|---|---|---|---|
| G1 | 59.33 | L/600 = 33.3 mm | 1.78 | FAIL |
| G2 | 60.41 | L/600 = 33.3 mm | 1.812 | FAIL |
| G3 | 60.41 | L/600 = 33.3 mm | 1.812 | FAIL |
| G4 | 59.33 | L/600 = 33.3 mm | 1.78 | FAIL |

[Original final runtime log](../logs/TC02_final.log).
