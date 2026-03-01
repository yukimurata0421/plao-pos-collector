from __future__ import annotations

import argparse
import json
import signal
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .io import JsonlWriter


def _yyyymmdd(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y%m%d")


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _safe_int(x: Any) -> Optional[int]:
    try:
        if x is None:
            return None
        return int(x)
    except Exception:
        return None


def _pick_alt(ac: dict[str, Any]) -> tuple[Optional[int], str]:
    alt_baro = ac.get("alt_baro")
    if alt_baro is not None:
        return _safe_int(alt_baro), "baro"
    alt_geom = ac.get("alt_geom")
    if alt_geom is not None:
        return _safe_int(alt_geom), "geom"
    return None, "none"


@dataclass
class _Track:
    last_emit_ts: float = 0.0
    last_seen_ts: float = 0.0


class Collector:
    def __init__(
        self,
        out_dir: str,
        poll_interval_s: float,
        min_emit_interval_s: float,
        track_ttl_s: float,
        readsb_path: str,
        fsync_every: int = 200,
    ) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.poll_interval_s = float(poll_interval_s)
        self.min_emit_interval_s = float(min_emit_interval_s)
        self.track_ttl_s = float(track_ttl_s)
        self.readsb_path = readsb_path
        self.fsync_every = int(fsync_every)
        self.tracks: dict[str, _Track] = {}
        self._current_day: Optional[str] = None
        self._writer: Optional[JsonlWriter] = None
        self._stop = False
        self._last_warn_ts = 0.0

    def _open_for_ts(self, ts: float) -> None:
        day = _yyyymmdd(ts)
        if self._current_day == day and self._writer:
            return
        if self._writer:
            self._writer.close()
        path = self.out_dir / f"pos_{day}.jsonl"
        self._writer = JsonlWriter(path, fsync_every=self.fsync_every)
        self._current_day = day

    def _emit(self, ts: float, obj: dict[str, Any]) -> None:
        self._open_for_ts(ts)
        assert self._writer is not None
        self._writer.write(obj)

    def _read_aircraft_json(self) -> Optional[dict[str, Any]]:
        try:
            with open(self.readsb_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            self._warn_rate_limited("readsb JSON decode error")
            return None
        except FileNotFoundError:
            self._warn_rate_limited("readsb file not found")
            return None
        except OSError:
            self._warn_rate_limited("readsb read error")
            return None
        except Exception:
            self._warn_rate_limited("readsb unexpected error")
            return None

    def process_snapshot(self, ts: float, snap: dict[str, Any]) -> None:
        aircraft = snap.get("aircraft") or []
        for ac in aircraft:
            hexid = ac.get("hex")
            if not hexid:
                continue

            lat = _safe_float(ac.get("lat"))
            lon = _safe_float(ac.get("lon"))
            if lat is None or lon is None:
                continue

            seen = _safe_float(ac.get("seen"))
            alt, alt_src = _pick_alt(ac)
            track = _safe_float(ac.get("track"))
            gs = _safe_float(ac.get("gs"))

            tr = self.tracks.get(hexid)
            if tr is None:
                tr = _Track(
                    last_emit_ts=ts - self.min_emit_interval_s,
                    last_seen_ts=ts,
                )
                self.tracks[hexid] = tr
            else:
                tr.last_seen_ts = ts

            if ts - tr.last_emit_ts < self.min_emit_interval_s:
                continue

            ev = {
                "type": "pos",
                "schema_ver": 1,
                "ts": ts,
                "hex": hexid,
                "seen": seen,
                "lat": lat,
                "lon": lon,
                "alt": alt,
                "alt_src": alt_src,
                "track": track,
                "gs": gs,
            }
            self._emit(ts, ev)
            tr.last_emit_ts = ts

    def _cleanup_tracks(self, ts: float) -> None:
        for hexid, tr in list(self.tracks.items()):
            if ts - tr.last_seen_ts > self.track_ttl_s:
                del self.tracks[hexid]

    def _warn_rate_limited(self, msg: str) -> None:
        now = time.time()
        if now - self._last_warn_ts >= 30.0:
            print(f"[WARN] {msg}")
            self._last_warn_ts = now

    def request_stop(self) -> None:
        self._stop = True

    def close(self) -> None:
        if self._writer:
            self._writer.close()
            self._writer = None

    def run_forever(self) -> None:
        """Run until signaled. Shutdown latency is up to poll_interval."""
        while not self._stop:
            t0 = time.time()
            snap = self._read_aircraft_json()
            if snap is not None:
                self.process_snapshot(t0, snap)
            self._cleanup_tracks(t0)
            elapsed = time.time() - t0
            sleep_s = self.poll_interval_s - elapsed
            if sleep_s > 0:
                time.sleep(sleep_s)
        self.close()


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="plao-collect",
        description="PLAO raw JSONL position logger (append-only)",
    )
    ap.add_argument(
        "--out-dir",
        default="./data/plao_pos",
        help="Output directory for pos_YYYYMMDD.jsonl (default: ./data/plao_pos)",
    )
    ap.add_argument(
        "--poll-interval",
        type=float,
        default=2.0,
        help="Polling interval seconds (default: 2.0)",
    )
    ap.add_argument(
        "--min-emit-interval",
        type=float,
        default=2.0,
        help="Per-hex minimum emit interval seconds (default: 2.0)",
    )
    ap.add_argument(
        "--track-ttl",
        type=float,
        default=21600.0,
        help="Track TTL seconds for memory cleanup (default: 21600)",
    )
    ap.add_argument(
        "--readsb-path",
        default="/run/readsb/aircraft.json",
        help="Path to readsb aircraft.json (default: /run/readsb/aircraft.json)",
    )
    ap.add_argument(
        "--fsync-every",
        type=int,
        default=200,
        help="Flush+fsync every N records (default: 200)",
    )
    args = ap.parse_args()

    c = Collector(
        out_dir=args.out_dir,
        poll_interval_s=args.poll_interval,
        min_emit_interval_s=args.min_emit_interval,
        track_ttl_s=args.track_ttl,
        readsb_path=args.readsb_path,
        fsync_every=args.fsync_every,
    )

    def _handle_signal(signum: int, frame: Any) -> None:
        print(f"[INFO] Received signal {signum}. Shutting down.")
        c.request_stop()

    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    c.run_forever()


if __name__ == "__main__":
    main()
