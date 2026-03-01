from __future__ import annotations

from plao.cli_collect import Collector


def test_ttl_cleanup(tmp_path):
    c = Collector(
        out_dir=str(tmp_path),
        poll_interval_s=1.0,
        min_emit_interval_s=1.0,
        track_ttl_s=10.0,
        readsb_path="/tmp/readsb.json",
        fsync_every=200,
    )
    try:
        ts = 1000.0
        snap = {"aircraft": [{"hex": "abc123", "lat": 35.0, "lon": 139.0, "seen": 0.1}]}
        c.process_snapshot(ts, snap)
        assert "abc123" in c.tracks

        c._cleanup_tracks(ts + 11.0)
        assert "abc123" not in c.tracks
    finally:
        c.close()
