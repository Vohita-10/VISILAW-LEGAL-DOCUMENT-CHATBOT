def rewrite_query_llm(user_query: str, chat_history: list, llm_client) -> str:
    """
    Rewrite the user query into a clean retrieval search string.
    llm_client is injected — no module-level instance.
    """
    history = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in (chat_history or [])[-6:]
    )

    prompt = f"""You are a query rewriting system for legal document retrieval.

Rewrite the user's question into a concise search query that retrieves
the most relevant document chunks.

Rules:
- Do NOT answer the question.
- Do NOT add new facts.
- Keep the same intent.
- Resolve pronouns and vague references using conversation history.
- Remove conversational filler.

Conversation history:
{history}

User question:
{user_query}

Return ONLY the rewritten search query:""".strip()

    rewritten = llm_client.generate(prompt).strip()
    return rewritten if rewritten else user_query
