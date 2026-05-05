from dataclasses import dataclass
from src.retrieval.hybrid import legal_hybrid_retriever


@dataclass
class RetrievalToolInput:
    """Structured input for the retrieval tool."""
    query:        str
    top_k:        int  = 5
    use_reranker: bool = True


def retrieval_tool(tool_input: RetrievalToolInput, session) -> "pd.DataFrame":
    """
    Run hybrid retrieval using engines stored in SessionState.
    All models come from session — no globals, no extra args.
    """
    return legal_hybrid_retriever(
        query        = tool_input.query,
        chunks_df    = session.chunks_df,
        bm25         = session.bm25_engine,
        faiss_index  = session.faiss_engine,
        embed_model  = session.embed_model,
        rerank_model = session.rerank_model,
        top_k        = tool_input.top_k,
        use_reranker = tool_input.use_reranker,
    )
