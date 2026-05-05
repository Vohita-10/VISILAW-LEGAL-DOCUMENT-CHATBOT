"""
src/eval.py — Simple retrieval + answer evaluation for VisiLaw.

Usage:
    from src.eval import run_eval, print_eval_report

    # Define your test set — questions + the chunk_ids you expect to appear
    TEST_SET = [
        {
            "question":        "What is the advertising policy?",
            "expected_chunks": ["legal_chunk_12", "legal_chunk_15"],
            "expected_keywords": ["advertising", "promote", "approval"],
        },
        ...
    ]

    report = run_eval(TEST_SET, session, llm_client)
    print_eval_report(report)
"""

from src.retrieval.hybrid   import legal_hybrid_retriever
from src.agent.executor     import run_agent


def _retrieval_hit_rate(retrieved_chunks: list, expected_chunk_ids: list) -> float:
    """
    What fraction of expected chunks appeared in the retrieved set?
    1.0 = all expected chunks were retrieved.
    """
    if not expected_chunk_ids:
        return 1.0
    retrieved_ids = {c.get("chunk_id", "") for c in retrieved_chunks}
    hits = sum(1 for cid in expected_chunk_ids if cid in retrieved_ids)
    return hits / len(expected_chunk_ids)


def _keyword_coverage(answer: str, expected_keywords: list) -> float:
    """
    What fraction of expected keywords appear in the answer?
    Simple proxy for answer completeness.
    """
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return hits / len(expected_keywords)


def run_eval(test_set: list, session, llm_client) -> dict:
    """
    Run the full eval loop over a test set.

    Each test case is a dict with:
        question          (str)  — the query to ask
        expected_chunks   (list) — chunk_ids that should be retrieved
        expected_keywords (list) — words that should appear in the answer

    Returns a report dict with per-question scores and aggregate metrics.
    """
    results = []

    for i, case in enumerate(test_set):
        question          = case["question"]
        expected_chunks   = case.get("expected_chunks",   [])
        expected_keywords = case.get("expected_keywords", [])

        print(f"[{i+1}/{len(test_set)}] Evaluating: {question[:60]}...")

        # Run retrieval
        retrieved_df = legal_hybrid_retriever(
            query        = question,
            chunks_df    = session.chunks_df,
            embed_model  = session.embed_model,
            rerank_model = session.rerank_model,
            bm25         = session.bm25_engine,
            faiss_index  = session.faiss_engine,
            top_k        = 5,
        )
        retrieved_chunks = retrieved_df.to_dict("records")

        # Run agent for full answer
        from src.memory.session_memory import SessionState
        eval_session = SessionState(
            chunks_df    = session.chunks_df,
            bm25_engine  = session.bm25_engine,
            faiss_engine = session.faiss_engine,
            embed_model  = session.embed_model,
            rerank_model = session.rerank_model,
            kg           = session.kg,
        )
        answer = run_agent(question, eval_session, llm_client)

        hit_rate = _retrieval_hit_rate(retrieved_chunks, expected_chunks)
        kw_score = _keyword_coverage(answer, expected_keywords)

        results.append({
            "question":          question,
            "hit_rate":          hit_rate,
            "keyword_coverage":  kw_score,
            "retrieved_ids":     [c.get("chunk_id") for c in retrieved_chunks],
            "expected_ids":      expected_chunks,
            "answer_preview":    answer[:200],
        })

    # Aggregate
    avg_hit  = sum(r["hit_rate"]         for r in results) / len(results)
    avg_kw   = sum(r["keyword_coverage"] for r in results) / len(results)

    return {
        "results":             results,
        "avg_hit_rate":        round(avg_hit, 3),
        "avg_keyword_coverage": round(avg_kw,  3),
        "n":                   len(results),
    }


def print_eval_report(report: dict) -> None:
    """Pretty-print the eval report."""
    print(f"\n{'='*60}")
    print(f"VisiLaw Eval Report  |  n={report['n']} questions")
    print(f"{'='*60}")
    print(f"Avg retrieval hit rate   : {report['avg_hit_rate']:.1%}")
    print(f"Avg keyword coverage     : {report['avg_keyword_coverage']:.1%}")
    print(f"\nPer-question breakdown:")
    for i, r in enumerate(report["results"]):
        status = "✅" if r["hit_rate"] >= 0.5 and r["keyword_coverage"] >= 0.5 else "❌"
        print(f"\n  {status} Q{i+1}: {r['question'][:55]}...")
        print(f"       Hit rate  : {r['hit_rate']:.1%}  |  "
              f"Keyword coverage: {r['keyword_coverage']:.1%}")
        if r["hit_rate"] < 1.0 and r["expected_ids"]:
            missing = set(r["expected_ids"]) - set(r["retrieved_ids"])
            print(f"       Missed chunks: {missing}")
    print(f"\n{'='*60}\n")
