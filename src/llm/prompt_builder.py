from enum import Enum


class AnswerMode(Enum):
    QA      = "qa"
    SUMMARY = "summary"
    LIST    = "list"
    EXPLAIN = "explain"


def _instruction_for_mode(mode: AnswerMode) -> str:
    return {
        AnswerMode.QA:      "Provide a clear, factual answer to the user's question.",
        AnswerMode.SUMMARY: "Provide a concise summary of the relevant documentation.",
        AnswerMode.LIST:    "List the relevant items clearly and completely.",
        AnswerMode.EXPLAIN: "Explain the topic in detail using the documentation.",
    }.get(mode, "Provide a helpful answer based on the documentation.")


def build_grounded_prompt(
    user_query: str,
    retrieved_chunks: list,
    chat_history: list,
    answer_mode: AnswerMode = AnswerMode.QA,
) -> str:
    """
    Build a grounded RAG prompt.
    Citations use chunk_id (e.g. legal_chunk_12) — consistent
    with citation_validator expectations.
    """
    context = "\n\n".join(
        f"[{c.get('chunk_id', c.get('row_id', i))}] {c.get('text', c.get('chunk_text', ''))}"
        for i, c in enumerate(retrieved_chunks)
        if c.get("text") or c.get("chunk_text")
    )

    history = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in (chat_history or [])[-6:]
    )

    return f"""You are a legal assistant answering questions using contract documentation.

Conversation history:
{history}

Documentation:
{context}

Instructions:
{_instruction_for_mode(answer_mode)}

Rules:
- Use ONLY the documentation above.
- Cite the source chunk using [chunk_id] after each claim.
- If the answer is not present say: "The document does not contain this information."

User Question:
{user_query}

Answer:""".strip()


def build_chat_prompt(user_query: str, chat_history: list) -> str:
    history = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in (chat_history or [])[-6:]
    )
    return f"""You are a helpful legal assistant.

Conversation:
{history}

User:
{user_query}
""".strip()