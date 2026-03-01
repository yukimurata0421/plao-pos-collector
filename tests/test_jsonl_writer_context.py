from __future__ import annotations

from plao.io import JsonlWriter


def test_jsonl_writer_context(tmp_path):
    path = tmp_path / "out.jsonl"
    with JsonlWriter(path, fsync_every=1) as w:
        w.write({"a": 1})
    assert path.read_text(encoding="utf-8").strip() == "{\"a\": 1}"
