"""Filesystem helpers used across pipeline stages."""

from __future__ import annotations
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def list_files(directory: str | Path, suffix: str) -> list[Path]:
    return sorted(Path(directory).glob(f"*{suffix}"))
