# Manuscript claims and limitations gate

Use this file during manuscript rewriting and final pre-submission checks.

## Supported

- The frozen Random Forest reduced ordinary RUL error versus the predefined mean-RUL and age-only baselines on the official FD001 test.
- The Random Forest official-test RMSE was 31.834 cycles and MAE was 23.441 cycles.
- Versus age-only linear regression, paired bootstrap analysis estimated an RMSE improvement of 7.476 cycles (95% CI 1.075 to 13.825) and a MAE improvement of 10.016 cycles (95% CI 4.008 to 15.849).
- Held-out permutation analysis identifies generic C-MAPSS predictors whose disruption most degrades macro engine-level RMSE.
- The frozen Random Forest exhibits systematic optimistic RUL bias.
- The Random Forest NASA asymmetric score is worse than the age-only baseline despite lower RMSE and MAE.
- A provenance-aware experimental C-MAPSS presentation can be integrated into AeroFleetX without replacing the deterministic demonstration predictor.
- The RUL-to-priority mapping can be audited descriptively as a research mapping.

## Must remain qualified

- The priority mapping produced 26 under-prioritized engines in the post-hoc official-test audit and is not suitable for operational authority.
- The official FD001 test has already been opened; no further model, target, calibration, feature, or threshold tuning may be justified from that test outcome within this experiment.
- C-MAPSS sensor labels remain generic unless authoritative dataset documentation supports a physical interpretation.
- C-MAPSS cycles are benchmark operating cycles, not validated calendar-time maintenance intervals.

## Not supported

- Real-aircraft operational validation.
- Demonstrated real-world maintenance outcome improvement.
- Certified maintenance decision capability.
- Airworthiness determination.
- Release-to-service authority.
- Automatic operational work-order or maintenance-scheduling authority.
- A claim that the Random Forest is superior under every metric.
- A claim that the research layer replaces the existing deterministic AeroFleetX demo predictor.

## Publication language

The safest consistent description is **experimental benchmark prognostic research output**. The existing AeroFleetX predictor remains **deterministic demonstration logic**, not a trained AI model.
