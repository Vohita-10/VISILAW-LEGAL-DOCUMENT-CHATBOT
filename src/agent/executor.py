from src.agent.intent_classifier import classify_intent
from src.agent.tools import RetrievalToolInput, retrieval_tool
from src.agent.agent_state import AgentState
from src.agent.planner import build_plan

from src.llm.llm_client import GeminiClient
from src.llm.prompt_builder import build_grounded_prompt, AnswerMode


def run_agent(user_query, state, chat_history, chunks_df, bm25_engine, faiss_engine):
    """
    Agent Execution Loop (Aligned with AgentPlan Architecture)
    """

    # ---------------------------
    # Step 1 — Detect Intent
    # ---------------------------
    intent = classify_intent(user_query)
    state.last_intent = intent

    print(f"🧠 Intent Detected: {intent}")

    # ---------------------------
    # Step 2 — Build Plan
    # ---------------------------
    plan = build_plan(user_query, state, chat_history)
    print(f"📋 Plan: {plan}")

    response = None

    # ---------------------------
    # Step 3 — Execute Actions
    # ---------------------------
    for action in plan.actions:

        if action.type == "retrieve":

            print("🔎 Running Retrieval Tool...")

            tool_input = RetrievalToolInput(
                query=user_query,
                top_k=5,
                use_reranker=True
            )

            retrieved_df = retrieval_tool(
                tool_input=tool_input,
                chunks_df=chunks_df,
                bm25_engine=bm25_engine,
                faiss_engine=faiss_engine
            )

            # Save retrieved chunks to state
            state.last_retrieved_chunks = retrieved_df.to_dict("records")

        elif action.type == "respond":

            print("💬 Generating grounded response with LLM...")

            if state.last_retrieved_chunks:

                # Initialize Gemini
                llm = GeminiClient(api_key="AIzaSyCKr-P6fOHfInHs2wCawPNb9OEvWlAkncY")

                prompt = build_grounded_prompt(
                    user_query=user_query,
                    retrieved_chunks=state.last_retrieved_chunks[:5],
                    chat_history=chat_history,
                    answer_mode=AnswerMode.QA
                )

                response = llm.generate(prompt)

            else:
                response = "No supporting legal context found."

    return response