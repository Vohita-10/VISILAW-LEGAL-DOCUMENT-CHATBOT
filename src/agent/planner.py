from src.agent.agent_state import AgentState
from src.agent.planner_types import AgentPlan, AgentAction


def build_plan(
    user_query: str,
    agent_state: AgentState,
    chat_history: list
) -> AgentPlan:
    """
    Simple deterministic planner (Step-6 version).

    Rules:
    1️⃣ If we have NO retrieved context → must retrieve.
    2️⃣ If we already have context → reuse it (for now).
    """

    # ---------------------------
    # HARD SAFETY RULE
    # ---------------------------
    if not agent_state.last_retrieved_chunks:
        return AgentPlan(actions=[
            AgentAction(type="retrieve", reason="Initial grounding required"),
            AgentAction(type="respond")
        ])

    # ---------------------------
    # Otherwise reuse context
    # ---------------------------
    return AgentPlan(actions=[
        AgentAction(type="respond", reason="Using existing grounded context")
    ])
