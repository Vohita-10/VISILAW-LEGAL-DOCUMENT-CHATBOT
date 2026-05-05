# VisiLaw AI — Legal Document Analysis Chatbot

An AI-powered chatbot for legal document search and summarization 
using custom-built Hybrid Retrieval RAG pipeline.

## Problem
Legal documents are lengthy, complex, and hard to navigate. 
Lawyers spend hours searching through them manually. 
For normal people, understanding legal language is nearly impossible.
VisiLaw solves this by letting you simply ask questions about 
any legal document in plain English.

## What it does
- Upload any legal document and instantly get a plain language 
  summary — key parties involved, obligations, and risky clauses
- Ask questions in natural language and get accurate answers 
  grounded in the document
- Hybrid retrieval system finds the most relevant sections accurately
- Knowledge graph captures legal relationships and context 
  between entities
- LLM generates clear, concise answers without hallucination
- Supports 25+ legal document and contract types

## Architecture
1. Ingestion — Recursive text splitting (1024 chars, 
   256 overlap) → Pandas DataFrame
2. Indexing — BM25 Engine + FAISS Index + Knowledge Graph 
   built simultaneously
3. Initial Analysis — Document analysis via Gemini LLM, 
   generates summary and metadata
4. Custom Orchestration (no LangChain) — Single 
   SessionState object manages entire pipeline
5. Execution Loop:
   - Intent Classification on user query
   - Retrieval Planner decides strategy
   - Context Sufficiency Check
   - Hybrid Search + Cross-encoder Reranking
   - Answer generation via Gemini API

## Tech Stack
- Python
- FAISS (dense vector search)
- BM25 (sparse keyword search)
- Hybrid Retrieval + Cross-encoder Reranking
- Knowledge Graphs (custom built)
- Google Gemini API
- Custom orchestration pipeline (no LangChain)
- Streamlit (UI)

## Challenges
- No GPU available — solved by integrating Gemini API 
  for LLM inference instead of running models locally
- Legal documents are highly complex — solved using 
  hybrid retrieval and knowledge graphs for better accuracy

## How to run
pip install -r requirements.txt
streamlit run app.py

Add your Gemini API key to a .env file:
GEMINI_API_KEY=your_key_here

## Built by
Vohita Nagarajan — B.Tech CSE (AIML), 2026
