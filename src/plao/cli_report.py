from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

from .io import iter_jsonl


def _day_from_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y%m%d")


def _iso_from_ts(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="plao-report",
        description="PLAO minimal report (summary.csv)",
    )
    ap.add_argument(
        "--in-dir",
        default="./data/plao_pos",
        help="Input directory containing pos_*.jsonl (default: ./data/plao_pos)",
    )
    ap.add_argument(
        "--out-dir",
        default="./public",
        help="Output directory (default: ./public)",
    )
    args = ap.parse_args()

    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(in_dir.glob("pos_*.jsonl"))
    n_files = len(files)

    total_records = 0
    unique_hex: set[str] = set()
    days_seen: set[str] = set()
    first_ts: float | None = None
    last_ts: float | None = None

    per_day_count: dict[str, int] = {}
    per_day_hex: dict[str, set[str]] = {}
    per_day_first: dict[str, float] = {}
    per_day_last: dict[str, float] = {}

    for path in files:
        for rec in iter_jsonl(path):
            if rec.get("type") != "pos" or rec.get("schema_ver") != 1:
                continue
            ts = rec.get("ts")
            hexid = rec.get("hex")
            if ts is None or hexid is None:
                continue
            try:
                ts_f = float(ts)
            except Exception:
                continue
            day = _day_from_ts(ts_f)
            days_seen.add(day)
            unique_hex.add(str(hexid))
            total_records += 1
            per_day_count[day] = per_day_count.get(day, 0) + 1
            per_day_hex.setdefault(day, set()).add(str(hexid))
            if day not in per_day_first or ts_f < per_day_first[day]:
                per_day_first[day] = ts_f
            if day not in per_day_last or ts_f > per_day_last[day]:
                per_day_last[day] = ts_f
            if first_ts is None or ts_f < first_ts:
                first_ts = ts_f
            if last_ts is None or ts_f > last_ts:
                last_ts = ts_f

    rows: list[dict[str, str | int]] = [{
        "day": "ALL",
        "first_ts": "" if first_ts is None else f"{first_ts}",
        "last_ts": "" if last_ts is None else f"{last_ts}",
        "first_iso": "" if first_ts is None else _iso_from_ts(first_ts),
        "last_iso": "" if last_ts is None else _iso_from_ts(last_ts),
        "days_covered": len(days_seen),
        "n_files": n_files,
        "total_records": total_records,
        "unique_hex": len(unique_hex),
    }]

    out_path = out_dir / "summary.csv"
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "day",
                "first_ts",
                "last_ts",
                "first_iso",
                "last_iso",
                "days_covered",
                "n_files",
                "total_records",
                "unique_hex",
            ],
        )
        w.writeheader()
        w.writerows(rows)

    days_path = out_dir / "days.csv"
    with days_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "day_utc",
                "total_records",
                "unique_hex",
                "first_ts",
                "last_ts",
                "first_iso",
                "last_iso",
            ],
        )
        w.writeheader()
        for day in sorted(per_day_count.keys()):
            first = per_day_first[day]
            last = per_day_last[day]
            w.writerow({
                "day_utc": day,
                "total_records": per_day_count[day],
                "unique_hex": len(per_day_hex[day]),
                "first_ts": f"{first}",
                "last_ts": f"{last}",
                "first_iso": _iso_from_ts(first),
                "last_iso": _iso_from_ts(last),
            })


if __name__ == "__main__":
    main()
