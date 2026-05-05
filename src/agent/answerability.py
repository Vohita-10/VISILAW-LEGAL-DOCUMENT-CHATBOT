import re
from typing import List, Dict


def is_answerable(
    user_query: str,
    retrieved_chunks: List[Dict],
    min_chunks: int = 2,
) -> bool:
    """
    Lightweight heuristic: does the retrieved context likely contain
    enough information to answer the query?

    Checks token overlap between query and chunk text.
    Handles both 'text' and 'chunk_text' key variants.
    """
    if not retrieved_chunks or len(retrieved_chunks) < min_chunks:
        return False

    query_tokens = set(re.findall(r"\w+", user_query.lower()))
    overlap_count = 0

    for chunk in retrieved_chunks:
        # Support both key names used across the pipeline
        text = chunk.get("text") or chunk.get("chunk_text", "")
        chunk_tokens = set(re.findall(r"\w+", text.lower()))
        if len(query_tokens & chunk_tokens) >= 2:
            overlap_count += 1

    return overlap_count >= min_chunks
