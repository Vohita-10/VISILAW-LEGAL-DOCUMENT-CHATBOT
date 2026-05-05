# src/agent/agent_state.py

from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class AgentState:
    """
    Session-scoped operational memory for the agent.

    This stores what happened during the current conversation.
    It is NOT vector memory or long-term storage.
    """

    # Last detected intent from classifier
    last_intent: Optional[str] = None

    # Retrieved chunks used as evidence for answering
    last_retrieved_chunks: Optional[List[Dict]] = None

    # Optional metadata returned by LLM intent classifier
    # Example: {"confidence": 0.82, "intent": "qa"}
    last_intent_metadata: Optional[Dict] = None

    # Answer mode chosen for the response
    # Example: QA / SUMMARY / EXPLAIN / LIST
    last_answer_mode: Optional[str] = None

    # Source mapping used for citation validation and follow-ups
    # Example:
    # {
    #   "LC00012": {"doc_id": "contract_1", "domain": "legal"},
    #   "LC00015": {"doc_id": "contract_1", "domain": "legal"}
    # }
    last_source_map: Optional[Dict[str, Dict]] = None
