#!/usr/bin/env bash
set -euo pipefail

# Micromouse Log Visualizer launcher
# Usage:
#   ./run_visualizer.sh                # open GUI, select file in app
#   ./run_visualizer.sh <file.csv>     # open GUI and load a CSV immediately

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/venv/bin/python"
APP="$SCRIPT_DIR/plot_visualizer.py"

if [[ ! -x "$VENV_PY" ]]; then
  echo "[ERROR] Python venv not found or not executable: $VENV_PY" >&2
  echo "Please create or fix the virtual environment under: $SCRIPT_DIR/venv" >&2
  exit 1
fi

if [[ ! -f "$APP" ]]; then
  echo "[ERROR] Visualizer script not found: $APP" >&2
  exit 1
fi

# Prefer loading file if user passed arguments; otherwise open with file chooser
if [[ $# -gt 0 ]]; then
  exec "$VENV_PY" "$APP" "$@"
else
  exec "$VENV_PY" "$APP"
fi
