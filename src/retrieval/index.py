import numpy as np
from .bm25 import BM25Index

class RetrievalIndex:
    def __init__(self, chunks_df):
        self.df = chunks_df
        self.bm25 = BM25Index(chunks_df["text"].astype(str).tolist())

    def search(self, query, k=5):
        scores = self.bm25.score(query)
        top_idx = np.argsort(scores)[::-1][:k]
        return self.df.iloc[top_idx]
