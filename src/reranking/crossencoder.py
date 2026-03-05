from typing import List
from sentence_transformers import CrossEncoder
import torch
from src.reranking.base import BaseReranker


class CrossEncoderReranker(BaseReranker):
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        device: str | None = None
    ):
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = CrossEncoder(model_name, device=device)

    def score(self, query: str, candidate_texts: List[str]) -> List[float]:
        pairs = [(query, text) for text in candidate_texts]
        scores = self.model.predict(pairs)
        return scores.tolist()