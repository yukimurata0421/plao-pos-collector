from __future__ import annotations

import csv

from plao.cli_report import main as report_main


def test_report_metadata_columns(tmp_path, monkeypatch, copy_fixture):
    in_dir = tmp_path / "in"
    out_dir = tmp_path / "out"
    in_dir.mkdir()
    out_dir.mkdir()

    dst = in_dir / "pos_20240101.jsonl"
    copy_fixture("pos_small.jsonl", dst)

    monkeypatch.setattr(
        "sys.argv",
        ["plao-report", "--in-dir", str(in_dir), "--out-dir", str(out_dir)],
    )
    report_main()

    summary = out_dir / "summary.csv"
    assert summary.exists()

    with summary.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows
    assert rows[0]["first_ts"]
    assert rows[0]["last_ts"]
    assert rows[0]["n_files"]
    assert rows[0]["first_iso"]
    assert rows[0]["last_iso"]

    days = out_dir / "days.csv"
    assert days.exists()
    with days.open("r", encoding="utf-8") as f:
        day_rows = list(csv.DictReader(f))
    assert day_rows
    assert day_rows[0]["day_utc"]
