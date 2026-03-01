from __future__ import annotations

from plao.cli_collect import Collector


def test_utc_filename(tmp_path):
    c = Collector(
        out_dir=str(tmp_path),
        poll_interval_s=1.0,
        min_emit_interval_s=1.0,
        track_ttl_s=10.0,
        readsb_path="/tmp/readsb.json",
        fsync_every=200,
    )
    try:
        ts = -3600.0  # 1969-12-31 23:00:00 UTC
        snap = {"aircraft": [{"hex": "abc123", "lat": 35.0, "lon": 139.0, "seen": 0.1}]}
        c.process_snapshot(ts, snap)
        expected = tmp_path / "pos_19691231.jsonl"
        assert expected.exists()
    finally:
        c.close()
