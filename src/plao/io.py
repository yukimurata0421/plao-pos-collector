from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Iterator


def iter_jsonl(path: str | Path) -> Iterator[dict]:
    """Yield JSON objects from a JSONL file. Malformed lines are skipped."""
    p = Path(path)
    if not p.exists():
        yield from ()
        return

    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                yield obj


def read_jsonl(path: str | Path) -> list[dict]:
    return list(iter_jsonl(path))


class JsonlWriter:
    def __init__(self, path: str | Path, fsync_every: int = 200) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")
        self._count = 0
        self._fsync_every = max(1, int(fsync_every))

    def __enter__(self) -> "JsonlWriter":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def write(self, record: dict) -> None:
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._count += 1
        if self._count % self._fsync_every == 0:
            self._fh.flush()
            os.fsync(self._fh.fileno())

    def close(self) -> None:
        try:
            self._fh.flush()
            os.fsync(self._fh.fileno())
        except Exception:
            pass
        try:
            self._fh.close()
        except Exception:
            pass


def write_jsonl(path: str | Path, record: dict | Iterable[dict], fsync_every: int = 200) -> None:
    writer = JsonlWriter(path, fsync_every=fsync_every)
    try:
        if isinstance(record, dict):
            writer.write(record)
        else:
            for rec in record:
                writer.write(rec)
    finally:
        writer.close()
