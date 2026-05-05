import pickle
import hashlib
import networkx as nx

from src.kg.kg_extractor import (
    extract_policies,
    extract_obligations,
    extract_restrictions,
)


def build_legal_kg(chunks_df) -> nx.DiGraph:
    """
    Build a directed knowledge graph from legal chunks.
    Nodes: clause, domain, policy, obligation, restriction.
    Edges: typed relations between them.
    """
    G = nx.DiGraph()

    for _, row in chunks_df.iterrows():
        clause_id = str(row["chunk_id"])
        text      = row["chunk_text"]
        domain    = row["domain"]

        G.add_node(clause_id, type="clause", text=text, domain=domain)

        if not G.has_node(domain):
            G.add_node(domain, type="domain")
        G.add_edge(clause_id, domain, relation="CLAUSE_IN_DOMAIN")

        for policy in extract_policies(text):
            if not G.has_node(policy):
                G.add_node(policy, type="policy")
            G.add_edge(clause_id, policy, relation="CLAUSE_GOVERNS_POLICY")

        for obligation in extract_obligations(text):
            oid = "obligation_" + hashlib.md5(obligation.encode()).hexdigest()[:8]
            if not G.has_node(oid):
                G.add_node(oid, type="obligation", text=obligation)
            G.add_edge(clause_id, oid, relation="CLAUSE_IMPOSES_OBLIGATION")

        for restriction in extract_restrictions(text):
            rid = "restriction_" + hashlib.md5(restriction.encode()).hexdigest()[:8]
            if not G.has_node(rid):
                G.add_node(rid, type="restriction", text=restriction)
            G.add_edge(clause_id, rid, relation="CLAUSE_RESTRICTS_ACTION")

    return G


def save_graph(graph: nx.DiGraph, path: str = "legal_kg.pkl") -> None:
    with open(path, "wb") as f:
        pickle.dump(graph, f)
    print(f"Knowledge graph saved: {graph.number_of_nodes()} nodes, "
          f"{graph.number_of_edges()} edges -> {path}")


def load_graph(path: str = "legal_kg.pkl") -> nx.DiGraph:
    with open(path, "rb") as f:
        return pickle.load(f)
