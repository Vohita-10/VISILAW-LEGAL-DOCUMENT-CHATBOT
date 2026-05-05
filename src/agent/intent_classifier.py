# src/agent/intent_classifier.py

def classify_intent(query: str) -> str:
    """
    Deterministic intent classification for legal queries.
    This avoids LLM usage and keeps routing predictable.
    """

    q = query.lower().strip()

    # Summary requests
    if any(k in q for k in ["summarize", "summary", "briefly explain" , "overview" , "in-short" , "gist"]):
        return "summary_request"

    # Clause lookup
    if any(k in q for k in ["show clause", "find clause", "where is clause"]):
        return "clause_lookup"

    # Obligation analysis
    if any(k in q for k in ["must", "required", "obligated", "shall"]):
        return "obligation_analysis"

    # Permission check
    if any(k in q for k in ["can i", "allowed", "permitted", "may i"]):
        return "permission_check"

    # Definition lookup
    if any(k in q for k in ["what is", "definition", "means", "define"]):
        return "definition_lookup"

    # Explanation
    if any(k in q for k in ["explain", "clarify", "elaborate"]):
        return "explanation"

    return "general_legal_query"