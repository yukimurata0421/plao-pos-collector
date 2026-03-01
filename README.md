# PLAO Position Collector

PLAO Position Collector is a durable, append-only ADS-B position producer designed for Raspberry Pi deployments.

It emits validated `pos_YYYYMMDD.jsonl` streams and hands them off to ARENA for downstream analytics (AUC, heatmaps, coverage evaluation).

PLAO is the producer layer.
ARENA is the consumer layer.
