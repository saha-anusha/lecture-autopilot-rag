"""Combine LaTeX section fragments into a compilable document."""

from __future__ import annotations
from pathlib import Path

PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage{amsmath,amssymb,amsthm}
\usepackage{enumitem}
\usepackage{geometry}
\geometry{margin=1in}
\newtheorem{definition}{Definition}
\newtheorem{theorem}{Theorem}
\title{Lecture Notes}
\date{}
\begin{document}
\maketitle
"""

POSTAMBLE = r"\end{document}"


def assemble(latex_sections: list[str], output_path: str | Path) -> Path:
    """Write a complete .tex file from a list of section fragments."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    body = "\n\n".join(latex_sections)
    full_doc = f"{PREAMBLE}\n{body}\n\n{POSTAMBLE}\n"
    output_path.write_text(full_doc, encoding="utf-8")
    return output_path
