from __future__ import annotations

from plao.io import iter_jsonl


def test_iter_jsonl_no_file(tmp_path):
    missing = tmp_path / "missing.jsonl"
    items = list(iter_jsonl(missing))
    assert items == []
