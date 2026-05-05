def retrieval_plan(query: str, intent: str) -> dict:
    """
    Return retrieval configuration based on detected intent.
    Used by the executor to tune top_k and engine selection.
    """
    plan = {
        "use_bm25":    True,
        "use_faiss":   True,
        "use_reranker": True,
        "top_k":       5,
    }

    if intent in ("definition_lookup", "clause_lookup"):
        plan["use_faiss"] = False
        plan["top_k"]     = 10

    if intent in ("permission_check", "obligation_analysis"):
        plan["top_k"] = 8

    if intent == "summary_request":
        plan["top_k"] = 15

    if len(query.split()) < 3:
        plan["use_bm25"]    = False
        plan["use_faiss"]   = False
        plan["use_reranker"] = False

    return plan
