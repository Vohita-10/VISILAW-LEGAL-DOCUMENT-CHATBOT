import networkx as nx


def query_policy(graph: nx.DiGraph, policy_name: str) -> list:
    """Return clause IDs that govern a given policy keyword."""
    return [
        clause
        for node, data in graph.nodes(data=True)
        if data.get("type") == "policy" and policy_name.lower() in node.lower()
        for clause in graph.predecessors(node)
    ]


def query_obligations(graph: nx.DiGraph, clause_id: str) -> list:
    """Return obligation texts attached to a clause."""
    return [
        graph.nodes[n]["text"]
        for n in graph.successors(clause_id)
        if graph.nodes[n].get("type") == "obligation"
    ]


def query_restrictions(graph: nx.DiGraph, clause_id: str) -> list:
    """Return restriction texts attached to a clause."""
    return [
        graph.nodes[n]["text"]
        for n in graph.successors(clause_id)
        if graph.nodes[n].get("type") == "restriction"
    ]


def kg_chunks_for_query(graph: nx.DiGraph, query: str, chunks_df) -> list:
    """
    Query the KG for clause IDs relevant to the query, then return
    the corresponding row indices from chunks_df.

    These are used to seed / boost hybrid retrieval so KG knowledge
    directly influences which chunks the LLM sees.
    """
    import re
    # Extract candidate keywords from the query (nouns / key terms)
    stopwords = {"the", "a", "an", "is", "are", "was", "what", "who",
                 "how", "does", "do", "in", "of", "to", "and", "or",
                 "for", "with", "this", "that", "can", "will", "be"}
    tokens = [
        w for w in re.findall(r"\w+", query.lower())
        if w not in stopwords and len(w) > 3
    ]

    matched_clause_ids = set()
    for token in tokens:
        matched_clause_ids.update(query_policy(graph, token))

    if not matched_clause_ids:
        return []

    # Map clause_id strings back to DataFrame row indices
    chunk_id_to_row = {
        row["chunk_id"]: idx
        for idx, row in chunks_df.iterrows()
    }
    return [
        chunk_id_to_row[cid]
        for cid in matched_clause_ids
        if cid in chunk_id_to_row
    ]


def summarize_graph(graph: nx.DiGraph) -> dict:
    """High-level stats about the knowledge graph."""
    type_counts: dict = {}
    for _, data in graph.nodes(data=True):
        t = data.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    return {
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
        "by_type":     type_counts,
    }
