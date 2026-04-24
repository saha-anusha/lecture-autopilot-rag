from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CLAUDE_MODEL = "claude-sonnet-4-6"
GPT4O_MODEL = "gpt-4o"

# Retrieval
TOP_K = 5
CHUNK_SIZE = 512        # characters per slide chunk

# Paths
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
INDEX_PATH = OUTPUT_DIR / "faiss.index"
METADATA_PATH = OUTPUT_DIR / "metadata.json"

# API keys (loaded from .env)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
