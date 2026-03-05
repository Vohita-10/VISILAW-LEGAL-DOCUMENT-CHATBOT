from abc import ABC, abstractmethod
from typing import List


class BaseReranker(ABC):
    @abstractmethod
    def score(self, query: str, candidate_texts: List[str]) -> List[float]:
        pass