import json
import re


class DocumentAnalyzer:
    """
    LLM-powered contract analyzer.
    Extracts structured insights: parties, dates, risks, summary.
    """

    def __init__(self, llm_client, bm25_engine):
        self.llm  = llm_client
        self.bm25 = bm25_engine

    # ── BM25 chunk retrieval ──────────────────────────────────────────────────
    def _retrieve_key_chunks(self) -> list:
        queries = [
            "effective date", "agreement date", "parties to this agreement",
            "term of agreement", "termination clause", "payment terms",
            "liability clause", "confidentiality clause",
        ]
        seen, selected = set(), []
        for q in queries:
            for idx, _ in self.bm25.search(q, k=3):
                chunk = self.bm25.documents[idx]
                if chunk not in seen:
                    seen.add(chunk)
                    selected.append(chunk)
        return selected

    # ── Regex metadata extraction ─────────────────────────────────────────────
    def _regex_extract(self, chunks: list) -> dict:
        date_pat     = r"\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b"
        duration_pat = r"\b\d*\s*(month|months|year|years)\b"
        detected     = {"date_chunks": [], "duration_chunks": [], "dates": [], "durations": []}
        for c in chunks:
            if re.findall(date_pat, c):
                detected["date_chunks"].append(c)
                detected["dates"].extend(re.findall(date_pat, c))
            if re.findall(duration_pat, c, re.IGNORECASE):
                detected["duration_chunks"].append(c)
                detected["durations"].extend(re.findall(duration_pat, c, re.IGNORECASE))
        return detected

    # ── Prompt builder ────────────────────────────────────────────────────────
    def _build_prompt(self, context: str) -> str:
        return f"""You are a legal contract risk analyst.

Analyze the following clauses and return ONLY valid JSON with no markdown.

Format:
{{
  "summary": "",
  "parties": [],
  "agreement_date": "",
  "agreement_duration": "",
  "termination_clause": "",
  "payment_terms": "",
  "risky_clauses": [
    {{"clause": "", "risk_level": "high|medium|low", "reason": ""}}
  ],
  "plain_language_explanation": ""
}}

Rules:
- Use ONLY the provided clauses.
- Return "not_found" for missing fields.
- Do not invent information.

Clauses:
{context}"""

    # ── JSON parsing ─────────────────────────────────────────────────────────
    def _parse_response(self, response: str) -> dict:
        clean = re.sub(r"```json|```", "", response).strip()
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return self._default_output()

    def _default_output(self) -> dict:
        return {
            "summary": "analysis_failed",
            "parties": [],
            "agreement_date": "not_found",
            "agreement_duration": "not_found",
            "termination_clause": "not_found",
            "payment_terms": "not_found",
            "risky_clauses": [],
            "plain_language_explanation": "not_available",
        }

    # ── Main entry point ──────────────────────────────────────────────────────
    def analyze_document(self) -> dict:
        key_chunks = self._retrieve_key_chunks()
        if not key_chunks:
            return self._default_output()

        regex_data = self._regex_extract(key_chunks)
        combined   = list(set(
            key_chunks +
            regex_data["date_chunks"] +
            regex_data["duration_chunks"]
        ))

        context  = "\n\n".join(combined)
        prompt   = self._build_prompt(context)
        response = self.llm.generate(prompt)
        return self._parse_response(response)
