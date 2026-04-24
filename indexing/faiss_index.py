"""Build and persist a FAISS index over slide chunks."""

from __future__ import annotations
import json
from dataclasses import asdict
from pathlib import Path

import faiss
import numpy as np

from config import INDEX_PATH, METADATA_PATH
from indexing.embedder import embed
from ingestion.slides import SlideChunk


def build_index(chunks: list[SlideChunk]) -> tuple[faiss.Index, list[dict]]:
    texts = [c.text for c in chunks]
    vectors = embed(texts).astype(np.float32)
    dim = vectors.shape[1]

    index = faiss.IndexFlatIP(dim)   # inner-product = cosine (embeddings are l2-normalised)
    index.add(vectors)

    metadata = [asdict(c) for c in chunks]
    return index, metadata


def save_index(index: faiss.Index, metadata: list[dict]) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))


def load_index() -> tuple[faiss.Index, list[dict]]:
    index = faiss.read_index(str(INDEX_PATH))
    metadata = json.loads(METADATA_PATH.read_text())
    return index, metadata


def search(
    index: faiss.Index,
    metadata: list[dict],
    query: str,
    top_k: int,
) -> list[dict]:
    """Return top_k metadata dicts ranked by cosine similarity to query."""
    vec = embed([query]).astype(np.float32)
    scores, ids = index.search(vec, top_k)
    results = []
    for score, i in zip(scores[0], ids[0]):
        if i == -1:
            continue
        results.append({**metadata[i], "score": float(score)})
    return results
