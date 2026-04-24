"""Stage 1: LCEL chain — Claude reasons about and structures each aligned segment."""

from __future__ import annotations

from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from config import CLAUDE_MODEL
from retrieval.retriever import AlignedSegment

SYSTEM_PROMPT = """\
You are an expert academic note-taker. Given a lecture transcript segment and \
relevant slide content, produce a concise, structured outline of the key concepts, \
definitions, and relationships. Use plain prose — no LaTeX yet. \
Be precise and exam-focused."""

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", (
        "## Transcript segment\n{transcript}\n\n"
        "## Relevant slide content\n{slides}\n\n"
        "Return a structured outline (headings, bullet points) covering the main ideas."
    )),
])

_llm = ChatAnthropic(model=CLAUDE_MODEL, max_tokens=1024)

# LCEL chain: prompt → Claude → plain string
structure_chain: Runnable = _prompt | _llm | StrOutputParser()


def _aligned_to_input(aligned: AlignedSegment) -> dict:
    slides_text = "\n\n".join(
        f"[Slide {c['slide_number']}] {c['text']}" for c in aligned.slide_chunks
    )
    return {"transcript": aligned.segment.text, "slides": slides_text}


def structure_segment(aligned: AlignedSegment) -> str:
    return structure_chain.invoke(_aligned_to_input(aligned))


def structure_all(aligned_segments: list[AlignedSegment]) -> list[str]:
    return structure_chain.batch([_aligned_to_input(a) for a in aligned_segments])
