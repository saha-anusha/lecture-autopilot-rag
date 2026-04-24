"""Stage 2: LCEL chain — GPT-4o converts structured outlines into LaTeX sections."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from config import GPT4O_MODEL

SYSTEM_PROMPT = """\
You are a LaTeX typesetting expert. Convert the provided structured outline \
into a clean LaTeX \\section or \\subsection block. \
Use appropriate environments: itemize, enumerate, definition, theorem as needed. \
Do NOT wrap in a full document — emit only the section body."""

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Convert this outline to LaTeX:\n\n{outline}"),
])

_llm = ChatOpenAI(model=GPT4O_MODEL, temperature=0)

# LCEL chain: prompt → GPT-4o → plain string
format_chain: Runnable = _prompt | _llm | StrOutputParser()


def format_section(outline: str) -> str:
    return format_chain.invoke({"outline": outline})


def format_all(outlines: list[str]) -> list[str]:
    return format_chain.batch([{"outline": o} for o in outlines])
