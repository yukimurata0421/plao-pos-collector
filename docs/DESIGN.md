# DESIGN

PLAO is a Raspberry Pi service that polls `readsb` JSON and appends raw position records into daily JSONL files.

## Goals

- Append-only logging, safe for long-running operation.
- Minimal schema with versioning.
- No post-processing or enrichment on the producer side.
- Predictable failure modes (partial writes are tolerated).

## Failure-First Behavior

- PLAO may be killed or power-cycled at any time.
- JSONL append-only means existing lines remain intact.
- Partial writes are limited to the last line and can be ignored by consumers.

## Fsync Strategy

- `--fsync-every` controls how often data is flushed to disk.
- Smaller values improve durability but increase SD-card wear.

## Memory Bound (TTL)

- Tracks are evicted after a TTL to prevent unbounded growth.

## Signal Handling

- SIGTERM/SIGINT trigger a clean shutdown.
- Shutdown latency is up to `poll_interval`.

## Handoff Invariants

- File rotation is by UTC day (`pos_YYYYMMDD.jsonl`).
- Schema contract is defined in `docs/SCHEMA.md` and must be stable.
- PLAO only produces raw JSONL; ARENA handles analytics.
