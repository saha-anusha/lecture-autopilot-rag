"""Embed text using a local HuggingFace sentence-transformer model."""

from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(texts: list[str]) -> np.ndarray:
    """Return float32 embeddings of shape (N, dim)."""
    return get_model().encode(texts, convert_to_numpy=True, normalize_embeddings=True)
