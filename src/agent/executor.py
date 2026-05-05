from src.agent.intent_classifier    import classify_intent
from src.agent.tools                import RetrievalToolInput, retrieval_tool
from src.agent.agent_state          import AgentState
from src.agent.planner              import build_plan
from src.llm.prompt_builder         import build_grounded_prompt, AnswerMode
from src.memory.session_memory      import SessionState


def run_agent(user_query: str, session: SessionState, llm_client) -> str:
    """
    Agent Execution Loop — your original logic, cleaned up.

    Signature: run_agent(question, session, llm)
    Session carries chunks_df, bm25_engine, faiss_engine,
    embed_model, rerank_model, chat_history, kg — everything.
    """

    if not session.is_pipeline_ready():
        return "No document loaded. Please upload and process a document first."

    # ── Step 1: Detect Intent ─────────────────────────────────────────────────
    intent = classify_intent(user_query)
    session.last_intent = intent
    print(f"🧠 Intent Detected: {intent}")

    # ── Step 2: Build Plan ────────────────────────────────────────────────────
    agent_state = AgentState(last_retrieved_chunks=session.last_retrieved_chunks)
    plan        = build_plan(user_query, agent_state, session.chat_history, llm_client)
    print(f"📋 Plan: {plan}")

    response = None

    # ── Step 3: Execute Actions ───────────────────────────────────────────────
    for action in plan.actions:

        # ── Retrieve ──────────────────────────────────────────────────────────
        if action.type == "retrieve":
            print("🔎 Running Retrieval Tool...")

            tool_input = RetrievalToolInput(
                query        = user_query,
                top_k        = 5,
                use_reranker = True
            )

            retrieved_df = retrieval_tool(tool_input, session)

            # KG injection — if KG exists, boost missing seed chunks
            if session.kg is not None:
                from src.kg.kg_query_engine import kg_chunks_for_query
                import pandas as pd
                kg_seeds  = kg_chunks_for_query(session.kg, user_query, session.chunks_df)
                already   = set(retrieved_df["row_id"].tolist())
                missing   = [i for i in kg_seeds if i not in already][:3]
                if missing:
                    extra = [
                        {
                            "row_id":       idx,
                            "rerank_score": 0.0,
                            "text":         session.chunks_df.iloc[idx]["chunk_text"],
                            "chunk_id":     session.chunks_df.iloc[idx]["chunk_id"],
                        }
                        for idx in missing
                    ]
                    retrieved_df = pd.concat(
                        [retrieved_df, pd.DataFrame(extra)], ignore_index=True
                    )
                    print(f"🔗 KG injected {len(extra)} extra chunks.")

            # Save into session memory
            chunks = retrieved_df.to_dict("records")
            agent_state.last_retrieved_chunks = chunks
            session.last_retrieved_chunks     = chunks

            print(f"🔎 Query Used: {user_query}")
            print(f"   Retrieved {len(chunks)} chunks.")

        # ── Respond ───────────────────────────────────────────────────────────
        elif action.type == "respond":
            print("💬 Generating grounded response with LLM...")

            chunks = agent_state.last_retrieved_chunks or []

            if not chunks:
                response = "No supporting legal context found."
                continue

            # Detect answer mode from query
            q = user_query.lower()
            if any(k in q for k in ["summarize", "summary", "overview"]):
                answer_mode, ctx_limit = AnswerMode.SUMMARY, 10
            elif "list" in q:
                answer_mode, ctx_limit = AnswerMode.LIST, 8
            elif any(k in q for k in ["explain", "clarify"]):
                answer_mode, ctx_limit = AnswerMode.EXPLAIN, 7
            else:
                answer_mode, ctx_limit = AnswerMode.QA, 5

            # Build grounded prompt and call LLM
            prompt = build_grounded_prompt(
                user_query       = user_query,
                retrieved_chunks = chunks[:ctx_limit],
                chat_history     = session.chat_history,
                answer_mode      = answer_mode,
            )

            try:
                response = llm_client.generate(prompt)
            except Exception as e:
                print(f"LLM error: {e}")
                response = "LLM unavailable. Please try again."

    # ── Step 4: Save turn to session chat history ─────────────────────────────
    if response:
        session.add_turn("user",      user_query)
        session.add_turn("assistant", response)

    return response or "Could not generate a response."
