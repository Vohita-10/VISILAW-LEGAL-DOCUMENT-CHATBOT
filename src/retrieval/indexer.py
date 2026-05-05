import faiss
import pickle
import numpy as np
from pathlib import Path
from src.retrieval.bm25 import BM25Index


def build_legal_search_indexes(chunks_df, embed_model, index_path: Path):
    """
    Build aligned BM25 (keyword) and FAISS (semantic) indexes.

    Args:
        chunks_df:   DataFrame with chunk_id, chunk_text, domain columns.
        embed_model: SentenceTransformer instance — passed in, not global.
        index_path:  Directory where indexes are saved.

    Returns:
        (bm25_engine, faiss_engine, chunks_df)
    """
    index_path = Path(index_path)
    index_path.mkdir(parents=True, exist_ok=True)

    chunks_df = chunks_df.reset_index(drop=True).copy()
    chunks_df["row_id"] = chunks_df.index
    texts = chunks_df["chunk_text"].astype(str).tolist()

    # ── BM25 ─────────────────────────────────────────────────────────────────
    print("Building BM25 index...")
    bm25 = BM25Index(documents=texts)
    with open(index_path / "bm25_legal.pkl", "wb") as f:
        pickle.dump(bm25, f)

    # ── FAISS ─────────────────────────────────────────────────────────────────
    print("Building FAISS index...")
    embeddings = embed_model.encode(
        texts, convert_to_numpy=True, show_progress_bar=True
    ).astype("float32")
    faiss.normalize_L2(embeddings)

    faiss_index = faiss.IndexFlatIP(embeddings.shape[1])
    faiss_index.add(embeddings)
    faiss.write_index(faiss_index, str(index_path / "faiss_legal.index"))

    print(f"Indexed {faiss_index.ntotal} chunks -> {index_path}")
    return bm25, faiss_index, chunks_df


def load_indexes(index_path: Path):
    """Load pre-built indexes from disk."""
    index_path = Path(index_path)
    with open(index_path / "bm25_legal.pkl", "rb") as f:
        bm25 = pickle.load(f)
    faiss_index = faiss.read_index(str(index_path / "faiss_legal.index"))
    return bm25, faiss_index
