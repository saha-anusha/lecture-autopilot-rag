# Lecture Autopilot

Deterministic multi-stage RAG pipeline that converts lecture transcripts and slides into structured, exam-ready LaTeX notes.

---

## Architecture

```
transcript (.vtt/.txt) ──┐
                         ├─→ [1] Ingestion ──→ [2] Indexing (FAISS) ──→ [3] Retrieval
slides (.pdf) ───────────┘                                                      │
                                                                                ↓
                                                         [4] LCEL generation pipeline (batch)
                                                          _aligned_to_input          (RunnableLambda)
                                                                 │
                                                          structure_chain            (prompt | Claude | StrOutputParser)
                                                                 │
                                                          format_chain               (prompt | GPT-4o | StrOutputParser)
                                                                 │
                                                         [5] Assembly → .tex
```

### Stage breakdown

| Stage | Module | Responsibility |
|-------|--------|----------------|
| Ingestion | `ingestion/transcript.py` | Parse VTT/plaintext transcripts into timed segments |
| Ingestion | `ingestion/slides.py` | Extract text chunks from slide PDFs (PyMuPDF) |
| Indexing | `indexing/embedder.py` | Embed text with `sentence-transformers/all-MiniLM-L6-v2` |
| Indexing | `indexing/faiss_index.py` | Build/persist/query a FAISS flat inner-product index |
| Retrieval | `retrieval/retriever.py` | Align each transcript segment with its top-k slide chunks |
| Generation | `generation/claude_stage.py` | LCEL chain: `prompt \| ChatAnthropic \| StrOutputParser` — structured outline per segment |
| Generation | `generation/gpt4o_stage.py` | LCEL chain: `prompt \| ChatOpenAI \| StrOutputParser` — LaTeX fragment per outline |
| Assembly | `assembly/assembler.py` | Joins fragments into a compilable `.tex` document |

### Design decisions

- **LCEL orchestration** — generation is a composed `Runnable` chain (`RunnableLambda | structure_chain | RunnableLambda | format_chain`) run via `.batch()`. No agent loops; the graph is a fixed DAG.
- **Two-stage generation** separates reasoning (Claude) from typesetting (GPT-4o); each stage is an independent LCEL chain so either can be swapped or tested in isolation.
- **FAISS flat index** is deterministic and exact — no approximate quantisation at this scale.
- **Index is cached** — rebuilt only on `--rebuild-index` or when missing, so re-runs over the same slides are cheap.

---

## Quickstart

```bash
# 1. Install dependencies (includes langchain-core, langchain-anthropic, langchain-openai)
pip install -r requirements.txt

# 2. Set API keys
cp .env.example .env
# edit .env: ANTHROPIC_API_KEY=... OPENAI_API_KEY=...

# 3. Run the pipeline
python main.py \
  --transcript data/transcripts/lecture01.vtt \
  --slides     data/slides/lecture01.pdf \
  --output     output/lecture01.tex

# 4. Compile PDF (requires a LaTeX distribution)
pdflatex output/lecture01.tex
```

### Input formats

- **Transcript**: WebVTT (`.vtt`) or plain text (`.txt`, one sentence per line).
- **Slides**: PDF. Text is extracted per page; each page may produce multiple chunks if text exceeds `CHUNK_SIZE`.

---

## Project structure

```
lecture-autopilot-rag/
├── main.py                  # Pipeline entry point
├── config.py                # Models, paths, constants
├── requirements.txt
├── ingestion/
│   ├── transcript.py
│   └── slides.py
├── indexing/
│   ├── embedder.py
│   └── faiss_index.py
├── retrieval/
│   └── retriever.py
├── generation/
│   ├── claude_stage.py      # Stage 1: reasoning + structure
│   └── gpt4o_stage.py       # Stage 2: LaTeX formatting
├── assembly/
│   └── assembler.py
├── utils/
│   └── io.py
├── data/
│   ├── transcripts/
│   └── slides/
└── output/                  # Generated index + .tex files
```

---

## Configuration

All tuneable parameters live in [`config.py`](config.py):

| Variable | Default | Purpose |
|----------|---------|---------|
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model for embeddings |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Claude model for stage 1 |
| `GPT4O_MODEL` | `gpt-4o` | OpenAI model for stage 2 |
| `TOP_K` | `5` | Slide chunks retrieved per segment |
| `CHUNK_SIZE` | `512` | Characters per slide chunk |
