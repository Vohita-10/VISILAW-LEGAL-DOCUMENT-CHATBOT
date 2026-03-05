import faiss
import numpy as np
from pathlib import Path


class FAISSIndex:
    def __init__(self, index_path: str):
        self.index_path = Path(index_path)
        self.index = None

    def load(self):
        if not self.index_path.exists():
            raise FileNotFoundError(f"FAISS index not found: {self.index_path}")

        self.index = faiss.read_index(str(self.index_path))

    def search(self, query_embedding: np.ndarray, top_k: int):
        if self.index is None:
            raise RuntimeError("FAISS index not loaded")

        distances, indices = self.index.search(query_embedding, top_k)
        return [
            (int(i), float(d))
            for i, d in zip(indices[0], distances[0])
        ]