from src.agent.agent_state import AgentState
from src.agent.planner_types import AgentPlan, AgentAction
from src.agent.llm_context_relevance import judge_context_relevance_llm


def build_plan(
    user_query: str,
    agent_state: AgentState,
    chat_history: list,
    llm_client,
) -> AgentPlan:
    """
    Decide whether to retrieve fresh context or reuse existing chunks.

    Rules:
      1. No context yet          → retrieve then respond
      2. Context exists, check relevance via LLM:
         - insufficient/new topic → retrieve then respond
         - sufficient             → respond only (reuse context)
    """
    if not agent_state.last_retrieved_chunks:
        return AgentPlan(actions=[
            AgentAction(type="retrieve", reason="Initial grounding required"),
            AgentAction(type="respond"),
        ])

    decision = judge_context_relevance_llm(
        user_query=user_query,
        retrieved_chunks=agent_state.last_retrieved_chunks,
        chat_history=chat_history,
        llm_client=llm_client,
    )

    if decision == "retrieve":
        return AgentPlan(actions=[
            AgentAction(type="retrieve", reason="Existing context insufficient"),
            AgentAction(type="respond"),
        ])

    return AgentPlan(actions=[
        AgentAction(type="respond", reason="Reusing grounded context"),
    ])
