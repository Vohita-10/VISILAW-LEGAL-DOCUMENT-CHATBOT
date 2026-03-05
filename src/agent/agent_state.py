from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class AgentState:
    """
    Session-scoped operational memory.

    This is NOT vector memory.
    It only remembers what happened during this conversation.
    """

    # Last detected intent from classifier
    last_intent: Optional[str] = None

    # Last retrieved chunks (evidence used to answer)
    last_retrieved_chunks: Optional[List[Dict]] = None

