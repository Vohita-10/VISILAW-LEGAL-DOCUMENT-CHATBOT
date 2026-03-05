import numpy as np
from collections import Counter
from .tokenization import tokenize
import pickle


class BM25Index:
    def __init__(self, documents=None, k1=1.5, b=0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b

        if documents is not None:
            self._build(documents)

    # ---------- build ----------
    def _build(self, documents):
        self.tokenized = [tokenize(d) for d in documents]

        self.N = len(self.tokenized)
        self.doc_len = np.array([len(d) for d in self.tokenized])
        self.avgdl = self.doc_len.mean()

        self.df = Counter()
        for doc in self.tokenized:
            for term in set(doc):
                self.df[term] += 1

    # ---------- persistence ----------
    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path):
        with open(path, "rb") as f:
            return pickle.load(f)

    # ---------- scoring ----------
    def idf(self, term):
        df = self.df.get(term, 0)
        return np.log(1 + (self.N - df + 0.5) / (df + 0.5))

    def _score_doc(self, query_tokens, doc_index):
        tf = Counter(self.tokenized[doc_index])
        score = 0.0

        for term in query_tokens:
            if term not in tf:
                continue

            numerator = tf[term] * (self.k1 + 1)
            denominator = tf[term] + self.k1 * (
                1 - self.b + self.b * self.doc_len[doc_index] / self.avgdl
            )

            score += self.idf(term) * (numerator / denominator)

        return score

    def search(self, query, k=10):
        query_tokens = tokenize(query)
        scores = np.zeros(self.N)

        for i in range(self.N):
            scores[i] = self._score_doc(query_tokens, i)

        top_k_idx = np.argsort(scores)[::-1][:k]
        return [
            (int(idx), float(scores[idx]))
            for idx in top_k_idx
        ]
