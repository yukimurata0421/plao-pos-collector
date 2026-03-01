# PLAO

PLAO is a **raw JSONL position logger** for Raspberry Pi. It polls `readsb` and appends position records to daily files. plao-report is intended for operational sanity checks, not performance evaluation.

PLAO is a raw JSONL position producer.

PLAO performs no evaluation, no optimization, and no performance interpretation.
It only produces append-only logs for downstream statistical analysis by ARENA.

## Architecture

- PLAO is the **raw JSONL producer**.
- Daily files are rotated by **UTC date**.
- Memory is bounded by **TTL cleanup** of inactive tracks.
- ARENA is the **consumer** that reads from the canonical handoff directory (default: `/mnt/e/arena/data/plao_pos`).
- Transfer is done by **external sync** (e.g., `rsync`) from the Pi to another machine.

Example output path:

- `data/plao_pos/pos_YYYYMMDD.jsonl`

## Recommended Deployment Model

PLAO runs on Raspberry Pi.
ARENA runs inside WSL on Windows.

Canonical data handoff path:

WSL (recommended):

- `/mnt/e/arena/data/plao_pos/pos_*.jsonl`

Windows example (path varies by user):

- `E:\\arena\\data\\plao_pos\\pos_*.jsonl`

Notes:

- WSL is the standard handoff target.
- Windows drive letters are user-dependent.
- PLAO does not assume a fixed Windows path.

ARENA consumer repository (GitHub):

```
https://github.com/yukimurata0421/arena-eval-engine
```

Data flow:

```
Raspberry Pi -> pos_YYYYMMDD.jsonl -> rsync -> WSL(/mnt/e/arena/...) -> ARENA
```

## Handoff to ARENA

PLAO is the producer. ARENA is the consumer.

Structure:

```
[Raspberry Pi]
  plao-collect (daemon / timer)
    -> append-only JSONL
       pos_YYYYMMDD.jsonl
    -> rsync (ops/sync)

[WSL on Windows]
  /mnt/e/arena/data/plao_pos/pos_*.jsonl

[ARENA (consumer)]
  distance AUC / heatmaps / reports
```

Run the sync script inside WSL:

```bash
bash ops/sync/sync_plao_pos_to_arena.sh
```

Edit these variables before running (required):

- `PI_USER`
- `PI_HOST`
- `PI_DIR` (Pi-side directory that contains `pos_*.jsonl`)
- `ARENA_DIR` (default is the WSL path above)

Rsync note:

- `--append-verify` requires rsync 3.x.

## Quickstart

```bash
python -m pip install -e .
plao-collect --out-dir data/plao_pos
plao-report --in-dir data/plao_pos --out-dir public
```

## What’s Included

- Code (`src/plao`)
- JSONL schema (`docs/SCHEMA.md`)
- Sample fixture (`tests/fixtures/pos_small.jsonl`) — synthetic data
- Tests + CI
- `configs/example_future_settings.toml` is a placeholder and is not loaded by PLAO yet.

## Security / Privacy

- **Do not publish raw JSONL logs.**
- `public/` contains only aggregated outputs (e.g., `summary.csv`).
- Site coordinates and other sensitive data must be handled carefully.
- `--fsync-every` lets you trade off SD-card wear vs. resilience to power loss.

## Design Principles

- append-only
- schema versioned
- long-running safe
- no Web dependency
- evaluation is externalized (handled by ARENA)

## systemd Unit

See `ops/systemd/plao_collect.service` for a Raspberry Pi unit template.

## Reports

`plao-report` is a minimal integrity report (not analytics).
