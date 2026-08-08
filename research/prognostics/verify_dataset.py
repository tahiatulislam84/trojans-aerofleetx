#!/usr/bin/env python3
"""Verify the exact NASA C-MAPSS archive used by the AeroFleetX study."""
from __future__ import annotations

import argparse
from pathlib import Path

from research.prognostics.pipeline import add_linear_rul, load_fd001, verify_dataset_archive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    args = parser.parse_args()

    digest = verify_dataset_archive(args.archive)
    train, test, _ = load_fd001(args.archive, verify_hash=False, include_test_truth=False)
    labeled = add_linear_rul(train)

    print(f"SHA-256: {digest}")
    print(f"Training rows: {len(train)}")
    print(f"Training engines: {train.unit_id.nunique()}")
    print(f"Test rows: {len(test)}")
    print(f"Test engines: {test.unit_id.nunique()}")
    print(f"Training RUL range: {int(labeled.RUL.min())}..{int(labeled.RUL.max())}")
    print("Official RUL_FD001.txt was not opened.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
