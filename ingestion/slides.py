"""Extract text chunks from lecture slide PDFs."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

import fitz  # pymupdf

from config import CHUNK_SIZE


@dataclass
class SlideChunk:
    slide_number: int       # 1-indexed
    chunk_index: int        # within slide
    text: str
    source_file: str


def parse_slides(path: str | Path) -> list[SlideChunk]:
    """Return one or more text chunks per slide page."""
    path = Path(path)
    doc = fitz.open(str(path))
    chunks: list[SlideChunk] = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if not text:
            continue
        for chunk_idx, chunk in enumerate(_split_text(text, CHUNK_SIZE)):
            chunks.append(
                SlideChunk(
                    slide_number=page_num,
                    chunk_index=chunk_idx,
                    text=chunk,
                    source_file=path.name,
                )
            )

    doc.close()
    return chunks


def _split_text(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]
