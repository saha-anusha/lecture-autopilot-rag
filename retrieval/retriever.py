"""Align each transcript segment with its most relevant slide chunks."""

from __future__ import annotations
from dataclasses import dataclass

import faiss

from config import TOP_K
from indexing.faiss_index import search
from ingestion.transcript import TranscriptSegment


@dataclass
class AlignedSegment:
    segment: TranscriptSegment
    slide_chunks: list[dict]    # top-k metadata dicts with scores


def retrieve(
    segments: list[TranscriptSegment],
    index: faiss.Index,
    metadata: list[dict],
    top_k: int = TOP_K,
) -> list[AlignedSegment]:
    """For each transcript segment, retrieve the closest slide chunks."""
    aligned: list[AlignedSegment] = []
    for seg in segments:
        hits = search(index, metadata, seg.text, top_k)
        aligned.append(AlignedSegment(segment=seg, slide_chunks=hits))
    return aligned
