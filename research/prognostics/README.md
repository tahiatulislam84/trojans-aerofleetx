# AeroFleetX Experimental Prognostics

This directory documents the research-only prognostic interface introduced after the frozen NASA C-MAPSS FD001 experiment.

## Boundary

The existing AeroFleetX Predictive Intelligence module remains a deterministic demonstration based on simulated component values, warning/critical thresholds, and transparent Low/Medium/High rules. It is not replaced by this work.

The experimental prognostic adapter represents a separate research path:

`C-MAPSS sensor observations -> frozen Random Forest -> estimated RUL -> review band -> research priority`

The Android/WebView application does **not** train or execute the Random Forest on-device in this phase. The UI consumes frozen benchmark-example output records so the provenance, priority mapping, explanation evidence, and safety boundary can be exercised without presenting a synthetic live inference as if it were operational.

## Frozen experiment

- Dataset: NASA C-MAPSS FD001
- Raw archive SHA-256: `74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f`
- Model ID: `cmapss-fd001-rf-phase5-v1`
- Model: Random Forest
- Trees: 100
- `max_depth`: 10
- `max_features`: 0.7
- `min_samples_leaf`: 5
- Random state: 2026
- AeroFleetX baseline commit: `346d8db1a7e51cdd05ae5dc206e953ec6402fac2`

The 100-tree setting reflects the documented pre-test runtime amendment to the Phase 4 protocol.

## Experimental RUL-to-priority mapping

| Estimated RUL | Review band | Research priority |
| --- | --- | --- |
| `<= 10` | 0-10 cycles | High |
| `>10` and `<=25` | 11-25 cycles | High |
| `>25` and `<=60` | 26-60 cycles | Medium |
| `>60` and `<=100` | 61-100 cycles | Medium |
| `>100` | >100 cycles | Low |

These cut points preserve the pre-existing AeroFleetX review-horizon buckets. They were not optimized from the official FD001 test outcomes.

## Known Phase 5/6 limitations

The frozen Random Forest improved conventional RMSE/MAE over the simple age-only baseline, but it did not improve the asymmetric NASA score. Phase 6 found systematic optimistic RUL bias: 79 of 100 official-test engines had overestimated RUL. The experimental output therefore remains unsuitable for operational maintenance authority.

The strongest held-out permutation-importance signals were `sensor_9`, `sensor_11`, `sensor_14`, `sensor_4`, and `sensor_12`. These generic C-MAPSS labels are intentionally retained; this repository does not assign unsupported physical component meanings to them.

## Integration rules

- Keep deterministic demo logic and experimental prognostics visibly separate.
- Do not convert C-MAPSS cycles to calendar days using demo aircraft-utilization values.
- Do not create a synthetic 0-100 health score from RUL.
- Do not automatically create work orders or schedule maintenance from the research result.
- Preserve model, dataset, application-version, and explanation provenance.
- Missing/invalid RUL is `Unavailable`, never implicitly Low.
- No result is an airworthiness determination, approved maintenance instruction, or release-to-service authorization.

## Application implementation

`app/src/main/assets/web/research-prognostic.js` mounts a separate experimental card inside the existing Predictive Intelligence screen. It contains frozen benchmark examples and a deterministic RUL-to-priority adapter. It intentionally does not replace `predictiveRisk()` or `predictedCycles()` in `app.js`.
