import numpy as np
import pandas as pd
import faiss


def rank_normalize(results: list) -> dict:
    """Min-max normalise (index, score) pairs to [0, 1]."""
    if not results:
        return {}
    scores = [s for _, s in results]
    max_s, min_s = max(scores), min(scores)
    if max_s == min_s:
        return {idx: 1.0 for idx, _ in results}
    return {idx: (s - min_s) / (max_s - min_s) for idx, s in results}


def legal_hybrid_retriever(
    query:          str,
    chunks_df,
    embed_model,
    rerank_model,
    bm25            = None,
    faiss_index     = None,
    top_k:          int   = 5,
    use_reranker:   bool  = True,
    kg_seed_ids:    list  = None,
    kg_boost:       float = 0.25,
) -> pd.DataFrame:
    """
    Hybrid BM25 + FAISS retriever with optional cross-encoder reranking
    and KG-seed boosting.

    kg_seed_ids: row indices from the KG query — these chunks get a
                 score boost so they surface near the top even if
                 BM25/FAISS didn't rank them highly.
    kg_boost:    how much extra score to add for KG-matched chunks.
    """
    # ── BM25 retrieval ────────────────────────────────────────────────────────
    bm25_candidates = bm25.search(query=query, k=50) if bm25 else []

    # ── FAISS retrieval ───────────────────────────────────────────────────────
    faiss_candidates = []
    if faiss_index is not None:
        q_emb = embed_model.encode([query]).astype("float32")
        faiss.normalize_L2(q_emb)
        f_scores, f_ids = faiss_index.search(q_emb, k=50)
        faiss_candidates = list(zip(f_ids[0].tolist(), f_scores[0].tolist()))

    # ── Hybrid fusion ─────────────────────────────────────────────────────────
    bm25_norm  = rank_normalize(bm25_candidates)
    faiss_norm = rank_normalize(faiss_candidates)

    merged: dict = {}
    for idx, s in bm25_norm.items():
        merged[idx] = merged.get(idx, 0.0) + s
    for idx, s in faiss_norm.items():
        overlap_boost   = 0.1 if idx in bm25_norm else 0.0
        merged[idx]     = merged.get(idx, 0.0) + s + overlap_boost

    # ── KG seed boost ─────────────────────────────────────────────────────────
    # Chunks the KG identified as relevant get an extra score boost,
    # ensuring they surface even if retrieval scored them lower.
    if kg_seed_ids:
        for idx in kg_seed_ids:
            merged[idx] = merged.get(idx, 0.0) + kg_boost
        print(f"KG boosted {len(kg_seed_ids)} chunks.")

    if not merged:
        return pd.DataFrame(columns=["row_id", "rerank_score", "text", "chunk_id"])

    # ── Select top-20 candidates for reranking ────────────────────────────────
    top20      = sorted(merged.items(), key=lambda x: x[1], reverse=True)[:20]
    cand_ids   = [i for i, _ in top20]
    cand_texts = [chunks_df.iloc[i]["chunk_text"] for i in cand_ids]

    # ── Optional cross-encoder reranking ─────────────────────────────────────
    if use_reranker and rerank_model is not None and cand_texts:
        scores = rerank_model.predict([(query, t) for t in cand_texts])
    else:
        scores = [s for _, s in top20]

    final = sorted(zip(cand_ids, scores), key=lambda x: x[1], reverse=True)[:top_k]

    return pd.DataFrame([
        {
            "row_id":       idx,
            "rerank_score": float(score),
            "text":         chunks_df.iloc[idx]["chunk_text"],
            "chunk_id":     chunks_df.iloc[idx].get("chunk_id", f"legal_chunk_{idx}"),
        }
        for idx, score in final
    ])
