#!/usr/bin/env bash
set -euo pipefail
node --check app/src/main/assets/web/app.js
node --check app/src/main/assets/web/xr3d.js
