def rank_normalize(results):
    """
    Rank-based score normalization.

    Args:
        results: List of tuples (doc_index, score_or_distance)
                 Already sorted by relevance:
                 - BM25: descending score
                 - FAISS: ascending distance

    Returns:
        Dict[doc_index, normalized_score]
    """
    normalized = {}

    for rank, (doc_idx, _) in enumerate(results, start=1):
        normalized[doc_idx] = 1.0 / rank

    return normalized

def merge_candidates(bm25_norm, faiss_norm, overlap_boost=0.1):
    """
    Merge normalized BM25 and FAISS candidates using union + boost.

    Args:
        bm25_norm: Dict[doc_index, normalized_score]
        faiss_norm: Dict[doc_index, normalized_score]
        overlap_boost: float added if doc appears in both

    Returns:
        Dict[doc_index, merged_score]
    """
    merged = {}

    all_doc_indices = set(bm25_norm.keys()) | set(faiss_norm.keys())

    for doc_idx in all_doc_indices:
        score = 0.0

        if doc_idx in bm25_norm:
            score += bm25_norm[doc_idx]

        if doc_idx in faiss_norm:
            score += faiss_norm[doc_idx]

        if doc_idx in bm25_norm and doc_idx in faiss_norm:
            score += overlap_boost

        merged[doc_idx] = score

    return merged


def rank_hybrid_candidates(merged_scores, top_k=5):
    """
    Rank merged hybrid candidates and return top-K.

    Args:
        merged_scores: Dict[doc_index, final_score]
        top_k: number of results to return

    Returns:
        List of tuples: (doc_index, final_score)
    """
    ranked = sorted(
        merged_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:top_k]