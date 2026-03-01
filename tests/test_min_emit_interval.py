from __future__ import annotations

from plao.cli_collect import Collector
from plao.io import read_jsonl


def test_min_emit_interval(tmp_path):
    c = Collector(
        out_dir=str(tmp_path),
        poll_interval_s=1.0,
        min_emit_interval_s=10.0,
        track_ttl_s=100.0,
        readsb_path="/tmp/readsb.json",
        fsync_every=1,
    )
    try:
        snap = {
            "aircraft": [
                {"hex": "abc123", "lat": 10.0, "lon": 20.0, "seen": 0.1}
            ]
        }
        c.process_snapshot(1000.0, snap)
        c.process_snapshot(1005.0, snap)

        path = tmp_path / "pos_19700101.jsonl"
        records = read_jsonl(path)
        assert len(records) == 1
    finally:
        c.close()
