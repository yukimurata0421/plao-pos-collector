from __future__ import annotations

import csv
from plao.cli_report import main as report_main
from plao.io import read_jsonl


def test_fixture_readable(fixtures_dir):
    path = fixtures_dir / "pos_small.jsonl"
    records = read_jsonl(path)
    assert len(records) >= 10
    assert records[0]["type"] == "pos"


def test_report_generates_summary(tmp_path, monkeypatch, copy_fixture):
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
    assert rows[0]["day"] == "ALL"
    assert int(rows[0]["total_records"]) > 0
