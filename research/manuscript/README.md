# TROJANS AeroFleetX — Manuscript-ready research evidence

## Status

Phase 10 consolidates the locked Phase 4 protocol and verified Phase 5–9 research outputs into a manuscript-rewrite evidence layer. This directory is **not** a substitute for the raw NASA dataset and does not contain or redistribute `CMAPSSData.zip`.

Current research baseline entering Phase 10:

`70d58b88fd4e602938ba99cd502c5a1e9427c4c5`

Locked C-MAPSS archive SHA-256:

`74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f`

## Manuscript research question

How can explainable degradation/RUL prediction be integrated into a traceable aviation-maintenance information workflow, and how does its predictive performance compare with simple baselines and the existing rule-based AeroFleetX approach?

## Primary quantitative evidence

The frozen Random Forest (`cmapss-fd001-rf-phase5-v1`) achieved on the 100-engine official FD001 test:

- RMSE: **31.834 cycles**
- MAE: **23.441 cycles**
- NASA asymmetric score: **19,726.393**
- mean signed error: **+19.119 cycles**

The age-only linear baseline achieved:

- RMSE: **39.310 cycles**
- MAE: **33.458 cycles**
- NASA asymmetric score: **17,239.683**

Paired engine-level bootstrap comparison, Random Forest versus age-only linear:

- RMSE improvement: **7.476 cycles**, 95% CI **1.075 to 13.825**
- MAE improvement: **10.016 cycles**, 95% CI **4.008 to 15.849**

## Critical negative result

The Random Forest improved RMSE and MAE but **did not improve the NASA asymmetric score**. Error analysis showed:

- 79/100 official-test engines had optimistic RUL errors;
- 99.71% of the Random Forest NASA penalty came from optimistic errors;
- the five largest-penalty engines contributed 80.5% of its total NASA score.

This limitation must be retained in the manuscript. The opened FD001 official test must not be reused for post-hoc retuning.

## Held-out explainability

Permutation importance was computed on held-out development engines only. The largest mean increases in macro engine-level RMSE were:

1. `sensor_9`: +6.161 cycles
2. `sensor_11`: +5.126 cycles
3. `sensor_14`: +1.486 cycles
4. `sensor_4`: +1.271 cycles
5. `sensor_12`: +1.045 cycles

The sensor names are generic C-MAPSS labels. No unsupported physical/component interpretation is assigned.

## Research-only RUL priority mapping

| Estimated RUL | Review band | Research priority |
|---|---|---|
| <=10 | 0–10 | High |
| 11–25 | 11–25 | High |
| 26–60 | 26–60 | Medium |
| 61–100 | 61–100 | Medium |
| >100 | >100 | Low |

Post-hoc official-test audit:

- priority accuracy: **72.0%**
- balanced accuracy: **74.6%**
- macro F1: **0.745**
- under-prioritized: **26** engines
- over-prioritized: **2** engines

This mapping remains research-only and is not operational maintenance authority.

## AeroFleetX integration boundary

The C-MAPSS layer is kept separate from the existing deterministic demonstration logic. The experimental presentation:

- is labelled `EXPERIMENTAL RESEARCH OUTPUT`;
- preserves model/dataset/app-version provenance;
- does not convert C-MAPSS cycles into calendar days;
- does not automatically create authoritative work orders;
- does not automatically schedule maintenance;
- does not determine airworthiness;
- does not authorize release to service.

## Reproducibility evidence

The version-controlled prognostics package provides:

- archive SHA-256 and ZIP integrity verification;
- FD001 schema/row/engine/missing/duplicate/finiteness checks;
- locked linear RUL construction;
- deterministic engine-level outer/inner folds;
- training-only preprocessing and zero-variance handling;
- predefined baselines and model families;
- macro engine-level metrics and NASA score;
- bootstrap and held-out permutation-importance helpers;
- frozen-model official-test evaluation;
- official-test truth opt-in rather than default loading;
- regression tests for scientific and safety boundaries.

The existing Android build/lint, source tests, browser validation, and required GitHub Actions `verify` check remain in place.

## Manuscript claims boundary

Supported claims include ordinary-error improvement over predefined baselines, held-out generic-feature importance, systematic optimistic-bias diagnosis, and provenance-aware integration of a benchmark prognostic layer.

Do **not** claim real-aircraft operational validation, certified maintenance decision capability, airworthiness/release-to-service authority, validated calendar-time scheduling from C-MAPSS cycles, or superiority under every metric.

## Next step

Use this evidence layer to rewrite the journal manuscript around the engineering-informatics contribution, quantitative validation, explainability, workflow integration, limitations, and reproducibility. Re-check the target journal's current scope, quartile/indexing, preprint policy, fees, disclosure requirements, and author instructions immediately before submission.
