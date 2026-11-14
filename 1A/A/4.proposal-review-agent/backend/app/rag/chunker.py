"""Section-aware chunking. Never merges text across headings, so citations stay precise.

PRODUCTION: size by tokens with the embedding model's tokenizer instead of characters.
"""

import re
from dataclasses import dataclass

from app.rag.parsers import Section


@dataclass
class Chunk:
    text: str
    heading: str
    page: int | None


def chunk_sections(
    sections: list[Section], max_chars: int = 1200, overlap_chars: int = 150
) -> list[Chunk]:
    chunks: list[Chunk] = []
    for s in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n", s.text) if p.strip()]
        current = ""
        for p in paragraphs:
            while len(p) > max_chars:  # one enormous paragraph
                chunks.append(Chunk(p[:max_chars], s.heading, s.page))
                p = p[max_chars - overlap_chars :]
            if current and len(current) + len(p) + 1 > max_chars:
                chunks.append(Chunk(current, s.heading, s.page))
                current = f"{current[-overlap_chars:]} {p}" if overlap_chars else p
            else:
                current = f"{current}\n{p}" if current else p
        if current:
            chunks.append(Chunk(current, s.heading, s.page))
    return chunks
