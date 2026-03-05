# src/llm/prompt_builder.py

from enum import Enum


class AnswerMode(Enum):
    QA = "qa"
    SUMMARY = "summary"
    LIST = "list"
    EXPLAIN = "explain"


def _instruction_for_answer_mode(answer_mode: AnswerMode):

    instructions = {
        AnswerMode.QA: (
            "Provide a clear and factual answer to the user's question."
        ),

        AnswerMode.SUMMARY: (
            "Provide a concise summary of the relevant documentation."
        ),

        AnswerMode.LIST: (
            "List the relevant items clearly."
        ),

        AnswerMode.EXPLAIN: (
            "Explain the topic in detail using the documentation."
        )
    }

    return instructions.get(
        answer_mode,
        "Provide a helpful answer based on the documentation."
    )


def build_grounded_prompt(
    user_query: str,
    retrieved_chunks: list,
    chat_history: list,
    answer_mode: AnswerMode = AnswerMode.QA
):
    """
    Build a grounded prompt using retrieved legal chunks.
    """

    # Build context from retrieved chunks
    context = "\n\n".join(
        f"[{c.get('row_id')}] {c.get('text')}"
        for c in retrieved_chunks
        if c.get("text")
    )

    # Build chat history
    history = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in chat_history[-6:]
    ) if chat_history else ""

    mode_instruction = _instruction_for_answer_mode(answer_mode)

    prompt = f"""
You are a legal assistant answering questions using documentation.

Conversation history:
{history}

Documentation:
{context}

Instructions:
{mode_instruction}

Rules:
- Use ONLY the documentation above
- Cite the source chunk using [row_id]
- If the answer is not present, say:
  "The document does not contain this information."

User Question:
{user_query}

Answer:
"""

    return prompt.strip()


def build_chat_prompt(
    user_query: str,
    chat_history: list
):
    """
    Prompt for casual conversation.
    """

    history = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in chat_history[-6:]
    ) if chat_history else ""

    return f"""
You are a helpful assistant.

Conversation:
{history}

User:
{user_query}

Assistant:
""".strip()