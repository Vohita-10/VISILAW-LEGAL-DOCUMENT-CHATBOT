FOLLOWUP_PHRASES = [
    "that document", "this document", "those documents", "these documents",
    "that clause", "this clause", "that policy", "this policy",
    "that section", "this section", "the document you referred",
    "the document you used", "that one", "this one", "it", "they",
]


def refers_to_previous_docs(message: str) -> bool:
    """True if the query references previously retrieved content."""
    if not message:
        return False
    msg = message.lower()
    return any(phrase in msg for phrase in FOLLOWUP_PHRASES)
