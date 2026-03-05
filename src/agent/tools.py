from dataclasses import dataclass


@dataclass
class RetrievalToolInput:
    """
    Structured input for retrieval tool.
    """
    query: str
    top_k: int = 5
    use_reranker: bool = True


def retrieval_tool(
    tool_input: RetrievalToolInput,
    chunks_df,
    bm25_engine,
    faiss_engine
):
    """
    Calls your legal_hybrid_retriever defined in the notebook.
    """

    # Import INSIDE function to avoid circular import problems
    from __main__ import legal_hybrid_retriever

    return legal_hybrid_retriever(
        query=tool_input.query,
        chunks_df=chunks_df,
        bm25=bm25_engine,
        faiss_index=faiss_engine,
        top_k=tool_input.top_k,
        use_reranker=tool_input.use_reranker
    )

