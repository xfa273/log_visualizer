#!/usr/bin/env bash
set -euo pipefail

# Micromouse Log Visualizer launcher
# Usage:
#   ./run_visualizer.sh                # open GUI, select file in app
#   ./run_visualizer.sh <file.csv>     # open GUI and load a CSV immediately

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/venv/bin/python"
APP="$SCRIPT_DIR/plot_visualizer.py"
PNG_APP="$SCRIPT_DIR/png_visualizer.py"
WEB_APP="$SCRIPT_DIR/web_visualizer.py"

# macOSのバージョン互換モードでOSが古い番号に見えてabortすることがあるため無効化する
export SYSTEM_VERSION_COMPAT=0

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
  if ! env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" -c 'import sys; sys.exit(0)' >/dev/null 2>&1; then
    if command -v python3 >/dev/null 2>&1; then
      PY_BIN="python3"
      echo "[WARN] venv python failed to start. Falling back to system python3." >&2
    else
      echo "[ERROR] venv python failed to start, and python3 not available." >&2
      exit 1
    fi
  fi
fi

if [[ $# -gt 0 && "$1" == "--web" ]]; then
  shift
  if [[ ! -f "$WEB_APP" ]]; then
    echo "[ERROR] Web visualizer script not found: $WEB_APP" >&2
    exit 1
  fi
  if ! "$PY_BIN" -c 'import streamlit, plotly' >/dev/null 2>&1; then
    echo "[ERROR] Web dependencies are missing (streamlit/plotly)." >&2
    echo "[INFO] Python used: $PY_BIN" >&2
    echo "[HINT] Install deps with:" >&2
    echo "       $PY_BIN -m pip install -r \"$SCRIPT_DIR/requirements.txt\"" >&2
    echo "[HINT] If pip is missing:" >&2
    echo "       $PY_BIN -m ensurepip --upgrade" >&2
    exit 1
  fi

  if [[ $# -gt 0 && -f "$1" ]]; then
    export MICROMOUSE_WEB_DEFAULT_CSV="$1"
  fi

  # Streamlit must be run as a module/command; use python -m to respect selected interpreter
  exec env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" -m streamlit run "$WEB_APP" --server.headless false
fi

if [[ ! -f "$APP" ]]; then
  echo "[ERROR] Visualizer script not found: $APP" >&2
  exit 1
fi

# TkがOS要件等でabortする環境ではGUIが起動できないので、事前にTk生成を試してフォールバックする
if ! env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" -c 'import tkinter as tk; r=tk.Tk(); r.withdraw(); r.update(); r.destroy();' >/dev/null 2>&1; then
  echo "[WARN] tkinter GUI is not available on this system. Falling back to PNG output." >&2
  if [[ ! -f "$PNG_APP" ]]; then
    echo "[ERROR] PNG visualizer script not found: $PNG_APP" >&2
    exit 1
  fi
  if [[ $# -gt 0 ]]; then
    exec env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" "$PNG_APP" "$@"
  else
    exec env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" "$PNG_APP" --latest
  fi
fi

# Prefer loading file if user passed arguments; otherwise open with file chooser
if [[ $# -gt 0 ]]; then
  exec env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" "$APP" "$@"
else
  exec env SYSTEM_VERSION_COMPAT=0 "$PY_BIN" "$APP"
fi
