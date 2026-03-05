from src.security.abac import abac_allows
from src.retrieval.text_preprocessing import tokenize
from src.retrieval.hybrid_scoring import (
    rank_normalize,
    merge_candidates,
    rank_hybrid_candidates
)


class HybridRetriever:
    def __init__(
        self,
        bm25,
        faiss,
        metadata_store,
        chunks_df,
        reranker=None
    ):
        self.bm25 = bm25
        self.faiss = faiss
        self.meta = metadata_store
        self.chunks = chunks_df
        self.reranker = reranker

    def retrieve(self, query, query_embedding, user, top_k=5):
        # --------------------
        # 1. Retrieve
        # --------------------
        bm25_candidates = self.bm25.search(query, k=50)
        faiss_candidates = self.faiss.search(query_embedding, top_k=50)

        # --------------------
        # 2. ABAC filter
        # --------------------
        def filter_allowed(results):
            allowed = []
            for idx, score in results:
                meta = self.meta.get(idx)
                if meta is not None and abac_allows(meta, user):
                    allowed.append((idx, score))
            return allowed

        bm25_allowed = filter_allowed(bm25_candidates)
        faiss_allowed = filter_allowed(faiss_candidates)

        # SAFETY: never allow empty sets
        if not bm25_allowed:
            bm25_allowed = bm25_candidates[:top_k]
        if not faiss_allowed:
            faiss_allowed = faiss_candidates[:top_k]

        # --------------------
        # 3. Normalize scores
        # --------------------
        bm25_norm = rank_normalize(bm25_allowed)

        # FAISS → invert distance so higher = better
        faiss_norm = rank_normalize([
            (idx, -score) for idx, score in faiss_allowed
        ])

        # --------------------
        # 4. Merge
        # --------------------
        merged = merge_candidates(
            bm25_norm,
            faiss_norm,
            overlap_boost=0.1
        )

        hybrid_ranked = rank_hybrid_candidates(
            merged,
            top_k * 2
        )

        # --------------------
        # 5. Optional reranking
        # --------------------
        if self.reranker is not None:
            candidate_ids = [idx for idx, _ in hybrid_ranked]

            candidate_texts = [
                self.chunks.iloc[idx]["chunk_text"]
                for idx in candidate_ids
            ]

            rerank_scores = self.reranker.score(
                query,
                candidate_texts
            )

            reranked = list(zip(candidate_ids, rerank_scores))
            reranked_sorted = sorted(
                reranked,
                key=lambda x: x[1],
                reverse=True
            )

            return reranked_sorted[:top_k]

        return hybrid_ranked[:top_k]
