import streamlit as st
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH  = PROJECT_ROOT / "data_legal"
INDEX_PATH = DATA_PATH / "indexes"
INDEX_PATH.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="VisiLaw",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"],
section[data-testid="stMain"] > div,
.main, .main > div,
[class*="css"] {
    background-color: #212121 !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
    color-scheme: dark !important;
}

@media (prefers-color-scheme: light) {
    html, body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section[data-testid="stMain"] > div,
    .main, .main > div,
    [class*="css"] {
        background-color: #212121 !important;
        color: #ececec !important;
    }
}

#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #171717 !important;
    border-right: 1px solid #2f2f2f !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"],
[data-testid="stSidebar"] * { color: #ececec !important; }
[data-testid="collapsedControl"] { background-color: #171717 !important; }

/* ── Logo ── */
.vl-logo {
    font-family: 'Inter', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #ececec !important;
    padding: 1.2rem 1.4rem 0.8rem;
    border-bottom: 1px solid #2f2f2f;
    margin-bottom: 1rem;
    letter-spacing: -0.02em;
}
.vl-logo-sub {
    font-size: 0.65rem;
    color: #666 !important;
    font-weight: 400;
    display: block;
    margin-top: 3px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Upload label ── */
.up-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #666 !important;
    padding: 0 1rem;
    margin-bottom: 0.4rem;
}

/* ── Analysis cards ── */
.ac-wrap { padding: 0 1rem; margin-bottom: 0.75rem; }
.ac-label {
    font-size: 0.63rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #666 !important;
    margin-bottom: 0.3rem;
}
.ac-value {
    font-size: 0.88rem;
    color: #d1d1d1 !important;
    line-height: 1.6;
    background: #2a2a2a !important;
    border: 1px solid #333 !important;
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
}

/* ── Contract type badge ── */
.ct-badge {
    display: inline-block;
    background: #ececec !important;
    color: #111111 !important;
    border-radius: 4px;
    padding: 0.2rem 0.7rem;
    font-size: 0.72rem;
    font-weight: 700;
    margin: 0 1rem 0.8rem;
    letter-spacing: 0.04em;
}

/* ── Risk cards ── */
.rc { border-radius: 6px; padding: 0.65rem 0.85rem; margin-bottom: 0.5rem; font-size: 0.83rem; line-height: 1.55; }
.rc.high   { background: #2a1515 !important; border: 1px solid #3d2020; border-left: 3px solid #e05555; }
.rc.medium { background: #2a2010 !important; border: 1px solid #3d3015; border-left: 3px solid #cc9933; }
.rc.low    { background: #152515 !important; border: 1px solid #203020; border-left: 3px solid #44aa44; }
.rc-title  { font-weight: 600; color: #ececec !important; margin-bottom: 0.3rem; font-size: 0.83rem; }
.rc-body   { color: #aaaaaa !important; font-size: 0.8rem; line-height: 1.55; }

/* ── Welcome screen ── */
.welcome {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    height: 80vh; text-align: center; gap: 1rem;
    background: #212121 !important;
}
.welcome-title { font-size: 2.2rem; font-weight: 700; color: #ececec !important; letter-spacing: -0.03em; }
.welcome-sub   { font-size: 0.95rem; color: #888 !important; max-width: 400px; line-height: 1.7; }
.welcome-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; justify-content: center; margin-top: 0.5rem; }
.chip {
    background: #2a2a2a !important; border: 1px solid #3a3a3a;
    border-radius: 20px; padding: 0.35rem 0.9rem;
    font-size: 0.8rem; color: #aaaaaa !important;
}

/* ── Chat header ── */
.chat-hdr {
    padding: 0.9rem 2rem;
    border-bottom: 1px solid #2f2f2f;
    font-size: 0.88rem;
    color: #666 !important;
    font-style: italic;
    background: #212121 !important;
}

/* ── Messages ── */
.mu { display: flex; justify-content: flex-end; margin-bottom: 1rem; }
.mu-b {
    background: #2f2f2f !important;
    color: #ececec !important;
    border: 1px solid #3a3a3a;
    border-radius: 16px 16px 3px 16px;
    padding: 0.75rem 1.1rem; max-width: 65%;
    font-size: 0.93rem; line-height: 1.6;
}
.ma { display: flex; justify-content: flex-start; margin-bottom: 1rem; gap: 0.6rem; align-items: flex-start; }
.ma-av {
    width: 30px; height: 30px; border-radius: 50%;
    background: #ececec !important; color: #111111 !important;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.68rem; font-weight: 700; flex-shrink: 0; margin-top: 2px;
}
.ma-b {
    background: #2a2a2a !important;
    border: 1px solid #333 !important;
    color: #d1d1d1 !important;
    border-radius: 3px 16px 16px 16px;
    padding: 0.85rem 1.1rem; max-width: 75%;
    font-size: 0.93rem; line-height: 1.7;
}

/* ── Citation ── */
.citation {
    display: inline-block;
    background: #333 !important; border: 1px solid #444;
    color: #aaa !important; border-radius: 4px;
    padding: 1px 6px; font-size: 0.72rem; font-family: monospace; margin: 0 2px;
}

/* ── Streamlit widget overrides ── */
.stTextInput > div > div > input {
    background: #2a2a2a !important;
    border: 1.5px solid #3a3a3a !important;
    border-radius: 10px !important;
    color: #ececec !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
}
.stTextInput > div > div > input::placeholder { color: #555 !important; }
.stTextInput > div > div > input:focus {
    border-color: #ececec !important;
    box-shadow: 0 0 0 2px rgba(255,255,255,0.08) !important;
}

/* ── ALL BUTTONS FIX ── */
.stButton > button {
    background: #2a2a2a !important;
    color: #ececec !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #333333 !important;
    border-color: #555555 !important;
    color: #ffffff !important;
}
/* Send button — keep prominent */
.stButton > button[kind="primary"] {
    background: #ececec !important;
    color: #111111 !important;
    border: none !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: #cccccc !important;
    color: #111111 !important;
}
/* Disabled state */
.stButton > button:disabled,
.stButton > button[disabled] {
    background: #1e1e1e !important;
    color: #666666 !important;
    border-color: #2a2a2a !important;
    opacity: 1 !important;
    cursor: not-allowed !important;
}

[data-testid="stFileUploader"] {
    background: #2a2a2a !important;
    border: 1.5px dashed #3a3a3a !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"] * { color: #aaaaaa !important; }
[data-testid="stFileUploader"] button { background: #3a3a3a !important; color: #ececec !important; }

.stSpinner > div { border-top-color: #ececec !important; }
.stProgress > div > div > div { background: #ececec !important; }

div[data-testid="stMarkdownContainer"] p { color: #d1d1d1 !important; font-size: 0.92rem !important; }
div[data-testid="stMarkdownContainer"] small { color: #888 !important; }

hr { border-color: #2f2f2f !important; }
</style>
""", unsafe_allow_html=True)


def init_session():
    if "pipeline_ready" not in st.session_state:
        st.session_state.pipeline_ready  = False
        st.session_state.analyzed        = False
        st.session_state.chat_history    = []
        st.session_state.visilaw_session = None
        st.session_state.llm             = None
        st.session_state.insights        = {}
        st.session_state.doc_name        = ""
        st.session_state.input_key       = 0

init_session()


@st.cache_resource(show_spinner=False)
def load_models():
    from sentence_transformers import SentenceTransformer, CrossEncoder
    from src.llm.llm_client import GeminiClient
    embed_model  = SentenceTransformer("all-MiniLM-L6-v2")
    rerank_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    llm          = GeminiClient()
    return embed_model, rerank_model, llm


def process_document(uploaded_file):
    from src.memory.session_memory import SessionState
    from src.ingestion              import ingest_and_chunk_document
    from src.retrieval.indexer      import build_legal_search_indexes
    from src.document_analysis      import DocumentAnalyzer
    from src.kg.build_legal_kg      import build_legal_kg, save_graph

    embed_model, rerank_model, llm = load_models()
    suffix = ".pdf" if uploaded_file.name.endswith(".pdf") else ".txt"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    prog = st.progress(0, text="Reading document...")
    chunks_df = ingest_and_chunk_document(tmp_path)
    prog.progress(20, text="Building search indexes...")
    bm25_engine, faiss_engine, final_chunks_df = build_legal_search_indexes(
        chunks_df=chunks_df, embed_model=embed_model, index_path=INDEX_PATH)
    prog.progress(50, text="Analysing contract...")
    session = SessionState()
    session.chunks_df    = final_chunks_df
    session.bm25_engine  = bm25_engine
    session.faiss_engine = faiss_engine
    session.embed_model  = embed_model
    session.rerank_model = rerank_model
    analyzer = DocumentAnalyzer(llm_client=llm, bm25_engine=bm25_engine)
    insights = analyzer.analyze_document()
    session.populate_insights(insights)
    prog.progress(80, text="Building knowledge graph...")
    kg = build_legal_kg(final_chunks_df)
    save_graph(kg)
    session.kg = kg
    prog.progress(100, text="Done!")
    os.unlink(tmp_path)
    prog.empty()
    return session, llm, insights


def render_answer(text):
    import re
    return re.sub(r'\[([^\]]+)\]', r'<span class="citation">[\1]</span>', text)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="vl-logo">⚖️ VisiLaw<span class="vl-logo-sub">Legal Intelligence Platform</span></div>',
        unsafe_allow_html=True)

    st.markdown('<div class="up-label">Upload Document</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload", type=["txt","pdf"], label_visibility="collapsed")

    if uploaded:
        new_file = uploaded.name != st.session_state.doc_name

        if not st.session_state.pipeline_ready or new_file:
            # Reset state silently if a new file is detected
            if new_file and st.session_state.pipeline_ready:
                for k in ["pipeline_ready","analyzed","chat_history",
                          "visilaw_session","llm","insights"]:
                    st.session_state[k] = (
                        False if k in ["pipeline_ready","analyzed"]
                        else [] if k == "chat_history"
                        else {} if k == "insights"
                        else None
                    )
                st.session_state.doc_name = ""

            if st.button("Analyse Document", use_container_width=True):
                st.session_state.doc_name = uploaded.name
                with st.spinner("Processing..."):
                    session, llm, insights = process_document(uploaded)
                st.session_state.visilaw_session = session
                st.session_state.llm             = llm
                st.session_state.insights        = insights
                st.session_state.pipeline_ready  = True
                st.session_state.analyzed        = True
                st.session_state.chat_history    = []
                st.rerun()

    if st.session_state.analyzed:
        ins = st.session_state.insights
        st.markdown("---")
        name = st.session_state.doc_name
        st.markdown(f'<div class="up-label">📄 {name[:26]}{"..." if len(name)>26 else ""}</div>',
                    unsafe_allow_html=True)

        ct = ins.get("contract_type","")
        if ct and ct not in ("Unknown",""):
            st.markdown(f'<span class="ct-badge">{ct}</span>', unsafe_allow_html=True)

        def card(label, val):
            if not val or str(val) in ("not_found","analysis_failed","not_available","[]",""):
                return
            v = ", ".join(str(x) for x in val) if isinstance(val, list) else str(val)
            if v.strip():
                st.markdown(
                    f'<div class="ac-wrap"><div class="ac-label">{label}</div>'
                    f'<div class="ac-value">{v}</div></div>',
                    unsafe_allow_html=True)

        card("Summary",         ins.get("summary"))
        card("Parties",         ins.get("parties"))
        card("Agreement Date",  ins.get("agreement_date"))
        card("Duration",        ins.get("agreement_duration"))
        card("Termination",     ins.get("termination_clause"))
        card("Payment Terms",   ins.get("payment_terms"))
        card("Plain Language",  ins.get("plain_language_explanation"))

        field_labels = {
            "product_description":"Product","pricing_terms":"Pricing",
            "delivery_terms":"Delivery","quality_warranty":"Quality/Warranty",
            "licensed_ip":"Licensed IP","license_scope":"License Scope",
            "royalty_terms":"Royalties","commission_structure":"Commission",
            "distribution_territory":"Territory","exclusivity":"Exclusivity",
            "governing_law":"Governing Law","confidentiality_clause":"Confidentiality",
            "force_majeure":"Force Majeure","ip_ownership":"IP Ownership",
            "indemnification":"Indemnification","limitation_of_liability":"Liability Cap",
            "dispute_resolution":"Dispute Resolution","assignment_rights":"Assignment",
            "franchise_fee":"Franchise Fee","royalty_structure":"Royalty Structure",
            "sponsorship_fee":"Sponsorship Fee","consulting_scope":"Consulting Scope",
        }
        skip = {"summary","parties","agreement_date","agreement_duration","termination_clause",
                "payment_terms","plain_language_explanation","risky_clauses","contract_type"}
        for key, label in field_labels.items():
            if key not in skip:
                card(label, ins.get(key))

        risks = ins.get("risky_clauses",[])
        if risks:
            st.markdown('<div class="ac-wrap"><div class="ac-label">Risk Clauses</div></div>',
                        unsafe_allow_html=True)
            for r in risks:
                lvl    = r.get("risk_level","low").lower()
                clause = r.get("clause","")
                reason = r.get("reason","")
                icon   = {"high":"🔴","medium":"🟡","low":"🟢"}.get(lvl,"⚪")
                css    = lvl if lvl in ("high","medium","low") else "low"
                st.markdown(
                    f'<div class="rc {css}">'
                    f'<div class="rc-title">{icon} {lvl.upper()} — {clause}</div>'
                    f'<div class="rc-body">{reason}</div>'
                    f'</div>', unsafe_allow_html=True)


# ── MAIN AREA ─────────────────────────────────────────────────────────────────
if not st.session_state.pipeline_ready:
    st.markdown("""
    <div class="welcome">
        <div style="font-size:3rem">⚖️</div>
        <div class="welcome-title">VisiLaw</div>
        <div class="welcome-sub">Upload a legal contract in the sidebar to begin.
        Get instant analysis, risk flags, and cited answers.</div>
        <div class="welcome-chips">
            <span class="chip">Hybrid Retrieval</span>
            <span class="chip">Risk Analysis</span>
            <span class="chip">Cited Answers</span>
            <span class="chip">Knowledge Graph</span>
        </div>
    </div>""", unsafe_allow_html=True)

else:
    st.markdown(f'<div class="chat-hdr">Analysing: {st.session_state.doc_name}</div>',
                unsafe_allow_html=True)

    with st.container():
        st.markdown('<div style="padding:1.5rem 2rem">', unsafe_allow_html=True)

        if not st.session_state.chat_history:
            st.markdown("""
            <div style="text-align:center;padding:3rem;color:#555;">
                <div style="font-size:1.8rem;margin-bottom:0.5rem">💬</div>
                <div style="font-size:0.95rem;color:#666">Document ready. Ask your first question below.</div>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="mu"><div class="mu-b">{msg["content"]}</div></div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="ma"><div class="ma-av">VL</div>'
                    f'<div class="ma-b">{render_answer(msg["content"])}</div></div>',
                    unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns([6,1])
    with c1:
        user_input = st.text_input(
            "Ask", placeholder="Ask anything about this document...",
            label_visibility="collapsed",
            key=f"ci_{st.session_state.input_key}")
    with c2:
        send = st.button("Send →", use_container_width=True)

    if not st.session_state.chat_history:
        st.markdown("<div style='padding:0.4rem 0;color:#aaaaaa;font-size:0.78rem;text-align:center'>Try asking</div>",
                    unsafe_allow_html=True)
        cols = st.columns(2)
        for i, sug in enumerate(["Summarize this agreement","What are the termination conditions?",
                                  "What are the payment terms?","Who indemnifies whom?"]):
            with cols[i%2]:
                if st.button(sug, key=f"s{i}", use_container_width=True):
                    user_input, send = sug, True

    if send and user_input and user_input.strip():
        from src.agent.executor import run_agent
        with st.spinner("Thinking..."):
            sess = st.session_state.visilaw_session
            ans  = run_agent(user_input.strip(), sess, st.session_state.llm)
        st.session_state.chat_history += [
            {"role":"user","content":user_input.strip()},
            {"role":"assistant","content":ans}]
        st.session_state.visilaw_session = sess
        st.session_state.input_key += 1
        st.rerun()