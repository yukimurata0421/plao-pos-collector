# PLAO JSONL Schema

Each line is a single JSON object (append-only). PLAO does not perform analytics. It only guarantees durable, append-only emission of validated position records.

File naming: `pos_YYYYMMDD.jsonl`.
Rotation is by **UTC day**.

Example:

```json
{"type":"pos","schema_ver":1,"ts":1700000000.1,"hex":"abc123","seen":0.1,"lat":12.345,"lon":-98.765,"alt":12000,"alt_src":"baro","track":90.0,"gs":220.5}
```

## Record Contract (schema_ver=1)

Mandatory:

- `type` == `"pos"`
- `schema_ver` == `1`
- `ts` (epoch seconds; collector time)
- `hex` (ICAO 24-bit)
- `lat` (float)
- `lon` (float)
- alt_src:
    Type: string (enum)
    Values:
        - baro: barometric altitude
        - geom: geometric (GNSS-derived) altitude
        - none: altitude unavailable
    Always present.
`lat`/`lon` are mandatory. Records without valid `lat`/`lon` MUST NOT be emitted.

`seen` is **nullable**. If missing or null, ARENA should treat it as "unknown age".

Optional:

- `alt` (ft)
- `track` (degrees)
- `gs` (knots)

`alt_src` is always present. If altitude is not available, emit `alt` as null and set `alt_src` to `"none"`.

## Compatibility Policy

- `schema_ver=1` will remain readable indefinitely.
- Breaking changes must bump `schema_ver` or introduce a new record type.

Note: test fixtures are synthetic and do not represent real-world locations.
