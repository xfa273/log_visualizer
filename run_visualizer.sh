#!/usr/bin/env bash
set -euo pipefail

# Micromouse Log Visualizer launcher
# Usage:
#   ./run_visualizer.sh                # open GUI, select file in app
#   ./run_visualizer.sh <file.csv>     # open GUI and load a CSV immediately

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/venv/bin/python"
APP="$SCRIPT_DIR/plot_visualizer.py"

PY_BIN="$VENV_PY"
if [[ ! -x "$PY_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
    echo "[WARN] venv not found. Falling back to system python3." >&2
    echo "[HINT] If dependencies are missing, create venv under: $SCRIPT_DIR/venv" >&2
  else
    echo "[ERROR] Python venv not found and python3 not available." >&2
    echo "Please install python3 or create venv under: $SCRIPT_DIR/venv" >&2
    exit 1
  fi
fi

# venvが存在しても、そのpython自体がOS要件で起動できない場合があるので実行テストする
if [[ "$PY_BIN" == "$VENV_PY" ]]; then
  if ! "$PY_BIN" -c 'import sys; sys.exit(0)' >/dev/null 2>&1; then
    if command -v python3 >/dev/null 2>&1; then
      PY_BIN="python3"
      echo "[WARN] venv python failed to start. Falling back to system python3." >&2
    else
      echo "[ERROR] venv python failed to start, and python3 not available." >&2
      exit 1
    fi
  fi
fi

if [[ ! -f "$APP" ]]; then
  echo "[ERROR] Visualizer script not found: $APP" >&2
  exit 1
fi

# Prefer loading file if user passed arguments; otherwise open with file chooser
if [[ $# -gt 0 ]]; then
  exec "$PY_BIN" "$APP" "$@"
else
  exec "$PY_BIN" "$APP"
fi
