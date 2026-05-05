# src/agent/retrieval_decision.py

import re


# Keywords that typically require document retrieval
RETRIEVAL_KEYWORDS = [
    "what",
    "how",
    "explain",
    "define",
    "policy",
    "rule",
    "requirement",
    "obligation",
    "restriction",
    "clause",
    "agreement",
    "contract",
    "advertising",
    "promotion",
    "compliance",
]


def should_retrieve(message: str) -> bool:
    """
    Decide whether retrieval is required for the user query.

    This avoids unnecessary retrieval for conversational
    messages like greetings or follow-ups.

    Deterministic and auditable logic (no LLM used).
    """

    if not message:
        return False

    msg = message.lower().strip()

    # Case 1: Question pattern
    if "?" in msg:
        return True

    # Case 2: Keyword trigger
    for kw in RETRIEVAL_KEYWORDS:
        if kw in msg:
            return True

    # Case 3: sentence starting with WH words
    if re.match(r"^(what|how|why|when|where)\b", msg):
        return True

    return False