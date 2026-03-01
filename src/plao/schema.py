from __future__ import annotations

from typing import Literal, TypedDict

SchemaVersion = Literal[1]


class PosRecord(TypedDict):
    """Schema contract for PLAO records (documentation + static analysis only)."""
    type: Literal["pos"]  # required
    schema_ver: SchemaVersion  # required
    ts: float  # required
    hex: str  # required
    seen: float | None  # nullable (age seconds from readsb)
    lat: float  # required
    lon: float  # required
    alt: int | None  # optional
    alt_src: Literal["baro", "geom", "none"]  # required
    track: float | None  # optional
    gs: float | None  # optional
