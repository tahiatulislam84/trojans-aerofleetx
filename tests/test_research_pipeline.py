import inspect
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Pytest's console-script entry point does not guarantee that the repository
# root is importable in every CI environment. Add the checked-out project root
# explicitly so these tests exercise the version-controlled research package.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.prognostics.pipeline import (
    COLUMNS,
    FROZEN_RF_PARAMS,
    add_linear_rul,
    engine_folds,
    fit_predict,
    load_fd001,
    macro_engine_metrics,
    map_rul_to_priority,
    nasa_score,
    outer_engine_folds,
    snapshot_features,
)


def synthetic_training(engines=6, cycles=5):
    rows = []
    for unit in range(1, engines + 1):
        for cycle in range(1, cycles + unit):
            row = {
                "unit_id": unit,
                "cycle": cycle,
                "setting_1": unit * 0.1,
                "setting_2": cycle * 0.01,
                "setting_3": 1.0,
            }
            for sensor in range(1, 22):
                row[f"sensor_{sensor}"] = unit + cycle * (sensor / 100.0)
            rows.append(row)
    return pd.DataFrame(rows, columns=COLUMNS)


def test_linear_rul_ends_at_zero_for_every_engine():
    labeled = add_linear_rul(synthetic_training())
    terminal = labeled.sort_values(["unit_id", "cycle"]).groupby("unit_id").tail(1)
    assert terminal["RUL"].tolist() == [0] * 6
    assert (labeled["RUL"] >= 0).all()


def test_linear_rul_example_is_max_cycle_minus_current_cycle():
    frame = synthetic_training(engines=1, cycles=5)
    labeled = add_linear_rul(frame)
    max_cycle = int(frame["cycle"].max())
    expected = max_cycle - labeled["cycle"]
    assert labeled["RUL"].tolist() == expected.tolist()


def test_engine_splits_never_leak_units():
    folds = engine_folds(range(1, 31), n_splits=5, seed=42)
    seen_validation = set()
    for train_ids, val_ids in folds:
        assert set(train_ids).isdisjoint(set(val_ids))
        seen_validation.update(val_ids.tolist())
    assert seen_validation == set(range(1, 31))


def test_outer_fold_assignment_is_locked():
    expected_validation = [
        [1, 5, 11, 13, 19, 23, 31, 32, 34, 40, 45, 46, 54, 71, 74, 77, 78, 81, 84, 91],
        [6, 10, 12, 16, 17, 27, 29, 36, 41, 43, 48, 56, 66, 67, 70, 73, 86, 89, 94, 97],
        [4, 7, 8, 9, 14, 18, 20, 25, 26, 28, 35, 37, 39, 50, 63, 65, 79, 82, 90, 96],
        [33, 42, 44, 47, 49, 51, 55, 57, 58, 59, 60, 62, 68, 69, 76, 80, 95, 98, 99, 100],
        [2, 3, 15, 21, 22, 24, 30, 38, 52, 53, 61, 64, 72, 75, 83, 85, 87, 88, 92, 93],
    ]
    actual = [val.tolist() for _, val in outer_engine_folds(range(1, 101))]
    assert actual == expected_validation


def test_snapshot_features_drop_zero_variance_using_training_frame_only():
    frame = synthetic_training()
    features = snapshot_features(frame)
    assert "setting_3" not in features
    assert "setting_1" in features
    assert "sensor_9" in features
    assert "unit_id" not in features
    assert "cycle" not in features


def test_model_pipeline_produces_finite_nonnegative_output_without_engine_leakage():
    data = add_linear_rul(synthetic_training(engines=8, cycles=6))
    train_ids, val_ids = engine_folds(range(1, 9), n_splits=4, seed=7)[0]
    assert set(train_ids).isdisjoint(set(val_ids))
    train = data[data["unit_id"].isin(train_ids)]
    val = data[data["unit_id"].isin(val_ids)]
    predictions = fit_predict("ridge", {"alpha": 1.0}, train, val)
    assert len(predictions) == len(val)
    assert np.isfinite(predictions).all()
    assert (predictions >= 0).all()


@pytest.mark.parametrize(
    ("rul", "expected"),
    [
        (0, ("High", "0-10")),
        (10, ("High", "0-10")),
        (10.01, ("High", "11-25")),
        (25, ("High", "11-25")),
        (25.01, ("Medium", "26-60")),
        (60, ("Medium", "26-60")),
        (60.01, ("Medium", "61-100")),
        (100, ("Medium", "61-100")),
        (100.01, ("Low", ">100")),
        (-1, ("Unavailable", "Unavailable")),
        (float("nan"), ("Unavailable", "Unavailable")),
        (None, ("Unavailable", "Unavailable")),
    ],
)
def test_research_priority_mapping_boundaries(rul, expected):
    assert map_rul_to_priority(rul) == expected


def test_nasa_score_penalizes_equal_optimistic_error_more_than_conservative_error():
    truth = np.array([100.0])
    optimistic = nasa_score(truth, np.array([120.0]))
    conservative = nasa_score(truth, np.array([80.0]))
    assert optimistic > conservative


def test_macro_engine_metric_weights_engines_equally():
    frame = pd.DataFrame({"unit_id": [1, 1, 1, 2]})
    truth = np.zeros(4)
    pred = np.array([10.0, 10.0, 10.0, 0.0])
    result = macro_engine_metrics(frame, truth, pred)
    assert result["macro_engine_rmse"] == pytest.approx(5.0)
    assert result["pooled_rmse"] == pytest.approx(math.sqrt(75.0))


def test_official_truth_is_opt_in_not_default():
    signature = inspect.signature(load_fd001)
    assert signature.parameters["include_test_truth"].default is False


def test_frozen_random_forest_parameters_are_locked():
    assert FROZEN_RF_PARAMS == {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_leaf": 5,
        "max_features": 0.7,
        "random_state": 2026,
    }
