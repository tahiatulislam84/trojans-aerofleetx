# AeroFleetX Experimental Prognostics

This directory is the version-controlled research package for the TROJANS AeroFleetX NASA C-MAPSS FD001 study.

The research path is deliberately separate from the existing AeroFleetX deterministic demonstration:

`C-MAPSS sensor observations -> frozen model -> estimated RUL -> review band -> research priority`

The Android/WebView application does **not** train the Random Forest on-device. The existing `predictiveRisk()` and `predictedCycles()` demonstration logic remains separate.

## Research and safety boundary

This package is a benchmark research artifact. It is **not an airworthiness determination**, approved maintenance instruction, operational dispatch tool, or release-to-service authority. C-MAPSS is simulated engine-degradation benchmark data, not validation on a real aircraft fleet.

The frozen Phase 5 model showed systematic optimistic RUL bias and did not improve the asymmetric NASA score even though it improved RMSE/MAE. Those limitations must remain visible in publications and software demonstrations.

## Dataset

Use the official NASA C-MAPSS archive obtained from the NASA/Data.gov source used in Phase 3.

Expected file:

`CMAPSSData.zip`

Locked SHA-256:

`74bef434a34db25c7bf72e668ea4cd52afe5f2cf8e44367c55a82bfd91a5a34f`

The raw NASA archive is intentionally **not committed or redistributed** in this repository. The public dataset record currently does not provide an explicit license field, so reproducibility is provided through source instructions, checksum verification, and scripts rather than repackaging the raw archive.

Do not commit `CMAPSSData.zip`.

## Environment

The Phase 5 reference experiment used:

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- scikit-learn 1.8.0
- joblib 1.5.3
- threadpoolctl 3.6.0

Install the locked Python packages:

```bash
python -m pip install -r research/prognostics/requirements.txt
```

See `ENVIRONMENT.md` for the CI/original-environment distinction.

## 1. Verify the dataset before analysis

```bash
python -m research.prognostics.verify_dataset /path/to/CMAPSSData.zip
```

The command checks:

- exact SHA-256;
- ZIP integrity;
- FD001 files;
- 26-column schema;
- row and engine counts;
- missing, duplicate, and non-finite values;
- linear training RUL generation.

It deliberately does **not** open `RUL_FD001.txt`.

## 2. Development-only experiment

```bash
python -m research.prognostics.run_experiment /path/to/CMAPSSData.zip \
  --output-dir research/prognostics/outputs
```

By default the official test answers are not loaded.

The development experiment reproduces the locked design:

- linear RUL: `max_cycle(engine) - current_cycle`;
- 5-fold engine-level outer CV, seed 42;
- 3-fold engine-level inner tuning;
- no engine can appear on both sides of a fold;
- zero-variance predictors are removed using the training side only;
- mean-RUL baseline;
- age-only linear baseline;
- Ridge;
- Random Forest;
- Histogram Gradient Boosting;
- primary metric: macro engine-level RMSE.

The exact protocol is stored in `protocol.json`.

## 3. Held-out explainability

To reproduce the Phase 6-style development-only permutation analysis:

```bash
python -m research.prognostics.run_experiment /path/to/CMAPSSData.zip \
  --output-dir research/prognostics/outputs \
  --explainability
```

Feature importance is computed on held-out development engines, not with official test RUL answers.

## 4. Official FD001 evaluation

The current study's official test was already opened once after model selection was frozen. Reproduction is allowed, but there is **no post-test retuning**.

The official answers are only loaded when the explicit flag is supplied:

```bash
python -m research.prognostics.run_experiment /path/to/CMAPSSData.zip \
  --output-dir research/prognostics/outputs \
  --evaluate-official-test
```

The frozen model is:

- `RandomForestRegressor`
- model ID `cmapss-fd001-rf-phase5-v1`
- 100 trees
- `max_depth=10`
- `max_features=0.7`
- `min_samples_leaf=5`
- random state 2026

The 100-tree choice is the documented Phase 4 runtime amendment made before Random Forest development results and before official-test evaluation.

## Reference results

`reference_results.json` records the Phase 5-7 result snapshot so a reproduction can be compared against the original run. It is evidence, **not a target for tuning**.

Key Phase 5 official-test values for the frozen Random Forest:

- RMSE: approximately 31.834 cycles
- MAE: approximately 23.441 cycles
- NASA asymmetric score: approximately 19,726.393
- mean signed error: approximately +19.119 cycles

Phase 6 found 79/100 optimistic RUL predictions.

## Experimental RUL-to-priority mapping

| Estimated RUL | Review band | Research priority |
| --- | --- | --- |
| `<= 10` | 0-10 cycles | High |
| `>10` and `<=25` | 11-25 cycles | High |
| `>25` and `<=60` | 26-60 cycles | Medium |
| `>60` and `<=100` | 61-100 cycles | Medium |
| `>100` | >100 cycles | Low |

Invalid, non-finite, or negative pre-clipping output maps to `Unavailable`, never Low.

The mapping preserves pre-existing AeroFleetX review-horizon boundaries. It was not optimized against official FD001 test results.

## Repository layout

```text
research/
  prognostics/
    pipeline.py
    run_experiment.py
    verify_dataset.py
    protocol.json
    reference_results.json
    rul-priority-mapping.json
    requirements.txt
    ENVIRONMENT.md
    README.md
```

Generated research outputs, models, and raw data directories are ignored by Git.

## Automated validation

`tests/test_research_pipeline.py` checks the scientific invariants, including:

- RUL target construction;
- engine-level split leakage protection;
- exact outer-fold assignment;
- training-only zero-variance handling;
- priority-boundary behavior;
- NASA-score asymmetry;
- official-test truth opt-in;
- frozen Random Forest parameters.

`tests/test_research_reproducibility.py` checks the reproducibility package and non-retuning/data-distribution boundaries.

These tests run inside the existing required GitHub Actions `verify` job. They do not weaken or replace the Android, lint, browser, or existing source regression checks.

## Integration rules

- Keep deterministic demo logic and experimental prognostics visibly separate.
- Do not convert C-MAPSS cycles to calendar days using demo aircraft-utilization values.
- Do not create a synthetic 0-100 health score from RUL.
- Do not automatically create work orders or schedule maintenance from the research result.
- Preserve model, dataset, application-version, and explanation provenance.
- No result is an approved maintenance decision or release-to-service authorization.
