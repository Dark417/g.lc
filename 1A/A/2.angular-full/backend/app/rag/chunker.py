"""Split documents into overlapping chunks. Paragraph-aware, character-budgeted.

PRODUCTION: token-based sizes (tiktoken / the model's tokenizer), heading-aware splitting for
markdown, and metadata (section title) carried on each chunk. LangChain/LlamaIndex text splitters
do this well if you already depend on them.
"""


def chunk_text(text: str, max_chars: int = 500, overlap_chars: int = 80) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 <= max_chars:
            current = f"{current}\n\n{p}".strip()
            continue
        if current:
            chunks.append(current)
        # carry the tail of the previous chunk so context isn't cut mid-thought
        tail = current[-overlap_chars:] if current and overlap_chars else ""
        current = f"{tail}\n\n{p}".strip() if tail else p
        while len(current) > max_chars:  # a single huge paragraph
            chunks.append(current[:max_chars])
            current = current[max_chars - overlap_chars :]
    if current:
        chunks.append(current)
    return chunks
