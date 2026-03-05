import re
from typing import List


def tokenize(text: str) -> List[str]:
    """
    Simple, transparent tokenizer for BM25.

    - Lowercases text
    - Keeps alphanumeric tokens
    - Removes punctuation
    """
    if not isinstance(text, str):
        return []

    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    return tokens