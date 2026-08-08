#!/usr/bin/env python3
"""Run the locked TROJANS AeroFleetX FD001 reproducibility experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from research.prognostics.pipeline import (
    FROZEN_RF_PARAMS,
    evaluate_official_test,
    frozen_random_forest,
    heldout_permutation_importance,
    load_fd001,
    official_last_cycle_predictions,
    run_development_cv,
    summarize_development,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path, help="Path to the official CMAPSSData.zip")
    parser.add_argument("--output-dir", type=Path, default=Path("research/prognostics/outputs"))
    parser.add_argument(
        "--evaluate-official-test",
        action="store_true",
        help="Explicitly open RUL_FD001.txt after the methodology is frozen.",
    )
    parser.add_argument(
        "--explainability",
        action="store_true",
        help="Also run held-out permutation importance (development data only).",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train, test, test_rul = load_fd001(
        args.archive,
        verify_hash=True,
        include_test_truth=args.evaluate_official_test,
    )

    outer, tuning = run_development_cv(train)
    summary = summarize_development(outer)
    outer.to_csv(args.output_dir / "outer_cv_results.csv", index=False)
    tuning.to_csv(args.output_dir / "tuning_results.csv", index=False)
    summary.to_csv(args.output_dir / "development_summary.csv", index=False)

    manifest = {
        "official_test_opened": bool(args.evaluate_official_test),
        "frozen_random_forest": FROZEN_RF_PARAMS,
        "note": "Official test metrics must not be used for post-test retuning.",
    }

    if args.explainability:
        importance = heldout_permutation_importance(train, repeats=10)
        importance.to_csv(args.output_dir / "permutation_importance_foldwise.csv", index=False)
        (
            importance.groupby("feature", as_index=False)
            .agg(
                mean_delta_macro_rmse=("importance_delta_rmse", "mean"),
                sd_delta_macro_rmse=("importance_delta_rmse", "std"),
            )
            .sort_values("mean_delta_macro_rmse", ascending=False)
            .to_csv(args.output_dir / "permutation_importance_summary.csv", index=False)
        )

    if args.evaluate_official_test:
        if test_rul is None:
            raise RuntimeError("Official test truth was not loaded")
        model, features = frozen_random_forest(train)
        predictions = official_last_cycle_predictions(model, features, test)
        predictions["true_RUL"] = test_rul.to_numpy()
        predictions.to_csv(args.output_dir / "official_test_predictions.csv", index=False)
        manifest["official_test_metrics"] = evaluate_official_test(predictions, test_rul)

    (args.output_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))
    if "official_test_metrics" in manifest:
        print(json.dumps(manifest["official_test_metrics"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
