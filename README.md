# Lecture Autopilot

Converts lecture transcripts and slide decks into structured, exam-ready LaTeX notes via a deterministic RAG pipeline.

## Pipeline Overview

```
transcript (.vtt/.txt)  ──┐
                           ├─► ingestion ─► indexing ─► retrieval ─► generation ─► assembly ─► notes.tex
slides (.pdf)           ──┘
```

### Stages

| # | Stage | Module | What it does |
|---|-------|--------|--------------|
| 1 | **Ingestion** | `ingestion/` | Parses WebVTT or plain-text transcripts into timed `TranscriptSegment` objects; extracts slide text chunks from PDF via PyMuPDF |
| 2 | **Indexing** | `indexing/` | Embeds slide chunks with `sentence-transformers` and stores them in a FAISS flat index; index is saved to disk and reused across runs |
| 3 | **Retrieval** | `retrieval/` | For each transcript segment, performs a FAISS nearest-neighbor search to surface the most relevant slide chunks → `AlignedSegment` |
| 4 | **Generation** | `generation/` | Two-stage LCEL pipeline: (1) **Claude** reasons over the aligned segment and produces a structured prose outline; (2) **GPT-4o** converts that outline into a LaTeX section body |
| 5 | **Assembly** | `assembly/` | Wraps all LaTeX section bodies in a complete document template and writes the final `.tex` file |

## Architecture

### Two-Stage Generation

The generation step is intentionally split across two models:

```
AlignedSegment
    │
    ▼
[Claude — claude_stage.py]
    Transcript + slide context → structured outline (plain prose)
    │
    ▼
[GPT-4o — gpt4o_stage.py]
    Outline → LaTeX section body
```

Claude handles reasoning and content structuring; GPT-4o handles deterministic LaTeX formatting. The two stages are composed as a single LCEL chain in `main.py` and executed with `.batch()` across all segments.

### Design Constraints

- **No agent loops** — the pipeline is a straight chain; each stage has a fixed input/output contract.
- **LangChain used only for LCEL** — `langchain-core` provides `RunnableLambda`, prompt templates, and output parsers. No autonomous agents or LangChain tooling beyond orchestration primitives.
- **FAISS index is persistent** — built once from slides and cached; pass `--rebuild-index` to regenerate.
- **Modular by stage** — each directory (`ingestion/`, `indexing/`, `retrieval/`, `generation/`, `assembly/`) is independently importable and testable.

## Project Structure

```
lecture-autopilot-rag/
├── main.py                  # Entry point; wires the full pipeline
├── config.py                # Model names, paths, constants
├── requirements.txt
├── .env.example
├── ingestion/
│   ├── transcript.py        # WebVTT + plain-text parser → TranscriptSegment
│   └── slides.py            # PDF → SlideChunk list via PyMuPDF
├── indexing/
│   ├── embedder.py          # sentence-transformers wrapper
│   └── faiss_index.py       # build / save / load FAISS index
├── retrieval/
│   └── retriever.py         # FAISS search → AlignedSegment
├── generation/
│   ├── claude_stage.py      # LCEL chain: aligned segment → outline (Claude)
│   └── gpt4o_stage.py       # LCEL chain: outline → LaTeX body (GPT-4o)
├── assembly/
│   └── assembler.py         # Joins LaTeX sections into a complete document
└── utils/
    └── io.py                # File helpers
```

## Setup

```bash
pip install -r requirements.txt

cp .env.example .env
# Add your keys:
#   ANTHROPIC_API_KEY=...
#   OPENAI_API_KEY=...
```

## Usage

```bash
python main.py \
  --transcript data/transcripts/lecture01.vtt \
  --slides     data/slides/lecture01.pdf \
  --output     output/lecture01.tex
```

Force a FAISS index rebuild (e.g. after updating slides):

```bash
python main.py --transcript ... --slides ... --rebuild-index
```

## Dependencies

| Package | Role |
|---------|------|
| `faiss-cpu` | Vector similarity search over slide embeddings |
| `sentence-transformers` | Local embedding model (no API call needed) |
| `langchain-core` | LCEL runnable composition |
| `langchain-anthropic` | Claude integration |
| `langchain-openai` | GPT-4o integration |
| `pymupdf` | PDF slide parsing |
| `pydantic` | Data models and validation |
| `python-dotenv` | `.env` key loading |
