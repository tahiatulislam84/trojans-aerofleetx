#!/usr/bin/env bash
set -euo pipefail
python3 -m pytest -m "not browser" -q
python3 -m pytest -m browser -q
