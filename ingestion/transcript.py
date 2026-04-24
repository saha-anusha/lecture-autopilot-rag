"""Parse a lecture transcript into timed segments."""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TranscriptSegment:
    index: int
    start_time: float       # seconds
    end_time: float
    text: str
    tokens: list[str] = field(default_factory=list)


def parse_transcript(path: str | Path) -> list[TranscriptSegment]:
    """Load a plain-text or WebVTT transcript and return segments.

    Plain-text format (fallback): one sentence per line.
    WebVTT format: detected by 'WEBVTT' header.
    """
    path = Path(path)
    raw = path.read_text(encoding="utf-8").strip()

    if raw.startswith("WEBVTT"):
        return _parse_vtt(raw)
    return _parse_plaintext(raw)


def _parse_vtt(raw: str) -> list[TranscriptSegment]:
    segments: list[TranscriptSegment] = []
    blocks = re.split(r"\n\n+", raw)
    idx = 0
    for block in blocks:
        lines = block.strip().splitlines()
        timestamp_line = next(
            (l for l in lines if "-->" in l), None
        )
        if timestamp_line is None:
            continue
        start_s, end_s = [
            _vtt_time_to_seconds(t.strip())
            for t in timestamp_line.split("-->")
        ]
        text = " ".join(
            l for l in lines if "-->" not in l and not l.strip().isdigit()
        ).strip()
        if text:
            segments.append(
                TranscriptSegment(idx, start_s, end_s, text)
            )
            idx += 1
    return segments


def _parse_plaintext(raw: str) -> list[TranscriptSegment]:
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    return [
        TranscriptSegment(i, float(i * 30), float((i + 1) * 30), line)
        for i, line in enumerate(lines)
    ]


def _vtt_time_to_seconds(ts: str) -> float:
    parts = ts.replace(",", ".").split(":")
    parts = [float(p) for p in parts]
    if len(parts) == 3:
        h, m, s = parts
    else:
        h, m, s = 0, parts[0], parts[1]
    return h * 3600 + m * 60 + s
