"""PLAO: Raspberry Pi POS JSONL logger."""

from .io import JsonlWriter, iter_jsonl, read_jsonl, write_jsonl

__all__ = [
    "__version__",
    "JsonlWriter",
    "iter_jsonl",
    "read_jsonl",
    "write_jsonl",
]
__version__ = "0.1.0"
