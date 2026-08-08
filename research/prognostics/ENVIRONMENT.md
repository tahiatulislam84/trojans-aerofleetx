# Phase 5 research environment

The Phase 5 reference results were generated in the analysis environment with:

- Python 3.13.5
- NumPy 2.3.5
- pandas 2.2.3
- SciPy 1.17.0
- scikit-learn 1.8.0
- joblib 1.5.3
- threadpoolctl 3.6.0

`research/prognostics/requirements.txt` pins the Python package versions. The project CI uses Python 3.12 for automated smoke/regression validation; full numerical reproduction should preferably use Python 3.13.5 when matching the original environment as closely as possible.

The official `CMAPSSData.zip` is intentionally not committed. Verify its SHA-256 before any experiment.
