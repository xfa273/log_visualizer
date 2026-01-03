#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def _default_logs_dir() -> Path:
    env_dir = os.environ.get("MICROMOUSE_LOG_DIR")
    if env_dir:
        return Path(env_dir).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Documents/micromouse_logs"
    return Path.home() / "micromouse_logs"


def _find_latest_csv(logs_dir: Path) -> Optional[Path]:
    if not logs_dir.is_dir():
        return None
    files = [p for p in logs_dir.iterdir() if p.is_file() and p.suffix.lower() == ".csv"]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]


def _load_csv(path: Path):
    import pandas as pd

    cols = ["time_ms", "param1", "param2", "param3", "param4", "param5", "param6", "param7"]
    return pd.read_csv(path, header=None, names=cols)


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("csv", nargs="?", default=None)
    ap.add_argument("--latest", action="store_true")
    ap.add_argument("--logs-dir", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    logs_dir = _default_logs_dir() if args.logs_dir is None else Path(args.logs_dir).expanduser()

    csv_path: Optional[Path]
    if args.latest or args.csv is None:
        csv_path = _find_latest_csv(logs_dir)
        if csv_path is None:
            print(f"[ERROR] No CSV found under: {logs_dir}", file=sys.stderr)
            print("[HINT] Specify a CSV path, or pass --logs-dir.", file=sys.stderr)
            return 2
    else:
        csv_path = Path(args.csv).expanduser()

    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}", file=sys.stderr)
        return 2

    out_path = Path(args.out).expanduser() if args.out else None
    if out_path is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = csv_path.with_name(f"{csv_path.stem}_{ts}.png")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    df = _load_csv(csv_path)

    fig, axes = plt.subplots(7, 1, figsize=(12, 10), sharex=True)
    for i in range(7):
        col = f"param{i+1}"
        axes[i].plot(df["time_ms"], df[col])
        axes[i].set_ylabel(col)
        axes[i].grid(True)

    axes[-1].set_xlabel("time_ms")
    fig.suptitle(csv_path.name)
    fig.tight_layout()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)

    print(f"[INFO] Saved: {out_path}")

    if (not args.no_open) and sys.platform == "darwin":
        try:
            subprocess.run(["open", str(out_path)], check=False)
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
