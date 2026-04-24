"""
Lecture Autopilot — main pipeline entry point.

Usage:
    python main.py --transcript data/transcripts/lecture01.vtt \
                   --slides data/slides/lecture01.pdf \
                   --output output/lecture01.tex \
                   [--rebuild-index]
"""

import argparse
from pathlib import Path

from langchain_core.runnables import RunnableLambda

from ingestion.transcript import parse_transcript
from ingestion.slides import parse_slides
from indexing.faiss_index import build_index, save_index, load_index
from retrieval.retriever import retrieve
from generation.claude_stage import structure_chain, _aligned_to_input
from generation.gpt4o_stage import format_chain
from assembly.assembler import assemble
from config import INDEX_PATH

# End-to-end generation chain: AlignedSegment → outline → LaTeX fragment
generation_pipeline = (
    RunnableLambda(_aligned_to_input)
    | structure_chain
    | RunnableLambda(lambda outline: {"outline": outline})
    | format_chain
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate LaTeX lecture notes")
    p.add_argument("--transcript", required=True, help="Path to transcript (.vtt or .txt)")
    p.add_argument("--slides", required=True, help="Path to slides PDF")
    p.add_argument("--output", default="output/notes.tex", help="Output .tex path")
    p.add_argument("--rebuild-index", action="store_true", help="Force index rebuild")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # ── 1. Ingestion ──────────────────────────────────────────────────────────
    print("[1/5] Parsing transcript...")
    segments = parse_transcript(args.transcript)
    print(f"      {len(segments)} segments loaded")

    print("[1/5] Parsing slides...")
    chunks = parse_slides(args.slides)
    print(f"      {len(chunks)} slide chunks loaded")

    # ── 2. Indexing ───────────────────────────────────────────────────────────
    if args.rebuild_index or not INDEX_PATH.exists():
        print("[2/5] Building FAISS index...")
        index, metadata = build_index(chunks)
        save_index(index, metadata)
        print(f"      Index saved to {INDEX_PATH}")
    else:
        print("[2/5] Loading existing FAISS index...")
        index, metadata = load_index()

    # ── 3. Retrieval ──────────────────────────────────────────────────────────
    print("[3/5] Aligning transcript segments with slides...")
    aligned = retrieve(segments, index, metadata)
    print(f"      {len(aligned)} aligned segments")

    # ── 4. Generation ─────────────────────────────────────────────────────────
    print("[4/5] Running generation pipeline (Claude → GPT-4o) via LCEL batch...")
    latex_sections = generation_pipeline.batch(aligned)

    # ── 5. Assembly ───────────────────────────────────────────────────────────
    print("[5/5] Assembling final LaTeX document...")
    out_path = assemble(latex_sections, args.output)
    print(f"      Written to {out_path}")


if __name__ == "__main__":
    main()
