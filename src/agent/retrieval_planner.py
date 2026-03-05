# src/agents/retrieval_planner.py

def retrieval_plan(query: str, intent: str) -> dict:
    """
    Decides HOW retrieval should be done.
    This is STEP 4: Query / Retrieval Planning
    """

    plan = {
        "use_bm25": True,
        "use_faiss": True,
        "use_reranker": True,
        "top_k": 5
    }

    q = query.lower()

    # ---- Definition / clause lookup ----
    if intent in ["definition_lookup", "clause_lookup"]:
        plan["use_faiss"] = False
        plan["top_k"] = 10

    # ---- Permission / explanation questions ----
    if intent in ["permission_check", "obligation_analysis"]:
        plan["use_faiss"] = True
        plan["use_bm25"] = True
        plan["top_k"] = 8

    # ---- Very short or weak queries ----
    if len(q.split()) < 3:
        plan["use_bm25"] = False
        plan["use_faiss"] = False
        plan["use_reranker"] = False

    return plan
