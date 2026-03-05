# src/agent/intent_classifier.py

def classify_intent(query: str) -> str:
    q = query.lower()

    if any(k in q for k in ["what does", "where is", "show me", "find clause"]):
        return "clause_lookup"

    if any(k in q for k in ["must", "required", "obligated", "shall"]):
        return "obligation_analysis"

    if any(k in q for k in ["can i", "allowed", "permitted", "may i"]):
        return "permission_check"

    if any(k in q for k in ["what is", "definition", "means"]):
        return "definition_lookup"

    return "general_legal_query"
