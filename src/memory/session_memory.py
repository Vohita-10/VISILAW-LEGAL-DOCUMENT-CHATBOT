from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class SessionState:
    """
    Single source of truth for one document session.
    Holds pipeline outputs, document insights, and chat history.
    Pass this object through the full pipeline so every stage
    can read and update it.
    """

    # ── Pipeline engines (populated after ingestion + indexing) ──────────────
    chunks_df:    Optional[Any] = None   # pd.DataFrame
    bm25_engine:  Optional[Any] = None
    faiss_engine: Optional[Any] = None
    embed_model:  Optional[Any] = None   # SentenceTransformer
    rerank_model: Optional[Any] = None   # CrossEncoder
    kg:           Optional[Any] = None   # nx.DiGraph

    # ── Document metadata (populated after DocumentAnalyzer.analyze) ─────────
    summary:              Optional[str]        = None
    parties:              Optional[List[str]]  = None
    agreement_date:       Optional[str]        = None
    agreement_duration:   Optional[str]        = None
    termination_clause:   Optional[str]        = None
    payment_terms:        Optional[str]        = None
    risky_clauses:        Optional[List[Dict]] = None
    plain_language:       Optional[str]        = None

    # ── Agent working memory (updated each turn) ─────────────────────────────
    last_intent:            Optional[str]        = None
    last_answer_mode:       Optional[str]        = None
    last_retrieved_chunks:  Optional[List[Dict]] = None
    last_source_map:        Optional[Dict]       = None

    # ── Conversation history (appended each turn) ────────────────────────────
    chat_history: List[Dict] = field(default_factory=list)

    # ── Convenience helpers ──────────────────────────────────────────────────
    def add_turn(self, role: str, content: str) -> None:
        """Append a message to chat history."""
        self.chat_history.append({"role": role, "content": content})

    def is_pipeline_ready(self) -> bool:
        """True once ingestion, indexing, and models are all loaded."""
        return (
            self.chunks_df    is not None and
            self.bm25_engine  is not None and
            self.faiss_engine is not None and
            self.embed_model  is not None and
            self.rerank_model is not None
        )

    def is_analyzed(self) -> bool:
        """True once DocumentAnalyzer has run."""
        return self.summary is not None

    def populate_insights(self, insights: Dict) -> None:
        """Bulk-load DocumentAnalyzer output into session fields."""
        self.summary            = insights.get("summary")
        self.parties            = insights.get("parties", [])
        self.agreement_date     = insights.get("agreement_date")
        self.agreement_duration = insights.get("agreement_duration")
        self.termination_clause = insights.get("termination_clause")
        self.payment_terms      = insights.get("payment_terms")
        self.risky_clauses      = insights.get("risky_clauses", [])
        self.plain_language     = insights.get("plain_language_explanation")

    def reset(self) -> None:
        """Clear all state (e.g. when a new document is uploaded)."""
        self.__init__()
