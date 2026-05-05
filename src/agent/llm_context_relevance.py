from typing import Literal

ContextDecision = Literal["reuse", "retrieve"]


def judge_context_relevance_llm(
    user_query: str,
    retrieved_chunks: list,
    chat_history: list,
    llm_client,
) -> ContextDecision:
    """
    Ask the LLM whether existing retrieved context is sufficient
    to answer the query, or whether fresh retrieval is needed.

    llm_client is injected — no module-level GeminiClient instance.
    """
    if not retrieved_chunks:
        return "retrieve"

    context_preview = "\n".join(
        f"- {c.get('text', c.get('chunk_text', ''))[:250]}"
        for c in retrieved_chunks[:5]
    )

    conversation = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in (chat_history or [])[-6:]
    )

    prompt = f"""You are an AI assistant deciding if document retrieval is required.

Conversation history:
{conversation}

Previously retrieved documentation:
{context_preview}

User question:
{user_query}

Decision rules:
- Return "reuse" ONLY if the current context fully answers the question.
- If any required information is missing, return "retrieve".
- If the user asks about a new topic, return "retrieve".
- If unsure, return "retrieve".

Respond with exactly one word — reuse or retrieve:"""

    decision = llm_client.generate(prompt).strip().lower()
    return "reuse" if decision == "reuse" else "retrieve"
