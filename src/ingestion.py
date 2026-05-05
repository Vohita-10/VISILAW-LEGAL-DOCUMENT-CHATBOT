import pandas as pd


def ingest_and_chunk_document(
    file_path:     str,
    chunk_size:    int = 1024,
    chunk_overlap: int = 256,
) -> pd.DataFrame:
    """
    Legal-domain document ingestor.
    Supports .txt and .pdf files.
    Uses RecursiveCharacterTextSplitter with legal-aware separators.
    chunk_size=1024, chunk_overlap=256 preserves your original ~58 chunks.

    Returns DataFrame with columns: chunk_id, chunk_text, domain.
    """
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except ImportError:
        from langchain.text_splitter import RecursiveCharacterTextSplitter

    file_path = str(file_path)

    if file_path.lower().endswith(".pdf"):
        raw_text = _read_pdf(file_path)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            raw_text = f.read()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size    = chunk_size,
        chunk_overlap = chunk_overlap,
        separators    = ["\n\n", "\n", "ARTICLE", "SECTION", ".", " ", ""],
    )
    chunks = splitter.split_text(raw_text)

    df = pd.DataFrame({
        "chunk_id":   [f"legal_chunk_{i}" for i in range(len(chunks))],
        "chunk_text": chunks,
        "domain":     "legal",
    })

    print(f"Ingested : {len(df)} chunks")
    print(f"Avg len  : {df['chunk_text'].str.len().mean():.0f} chars")
    print(f"Min/Max  : {df['chunk_text'].str.len().min()} / {df['chunk_text'].str.len().max()} chars")
    return df


def _read_pdf(file_path: str) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Install pypdf: pip install pypdf")
    reader = PdfReader(file_path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def _clean_pdf_page(text: str) -> str:
    """
    Only insert paragraph breaks at REAL clause starts (beginning of line),
    not mid-sentence cross-references like 'granted in Section 6.1'.
    """
    lines = text.split("\n")
    
    # A real new clause ONLY if it starts at the beginning of a line
    new_clause = re.compile(
        r"^(\d+\.\d*\s+[A-Z]|\d+\.\s+[A-Z]|Section\s+\d|\([a-z]\)\s|ARTICLE\s+[IVXLC\d])"
    )
    
    result = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Real clause boundary → blank line before it
        if new_clause.match(stripped):
            result.append("")  # blank line = paragraph break
            result.append(stripped)
        else:
            result.append(stripped)

    text = "\n".join(result)
    
    # Now collapse single newlines (soft wraps) into spaces
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()

















































































# # Tool 1: The Ingestor

# import pandas as pd
# import os

# def ingest_and_chunk_document(file_path, chunk_size=1024, chunk_overlap=256):
#     """
#     LEGAL-DOMAIN INGESTOR: Optimized for contracts and agreements.
#     Logic consolidated from visilaw1 and visilaw2.
#     """
#     try:
#         from langchain_text_splitters import RecursiveCharacterTextSplitter
#     except ImportError:
#         from langchain.text_splitter import RecursiveCharacterTextSplitter
    
#     with open(file_path, 'r', encoding='utf-8') as f:
#         raw_text = f.read()
    
#     # Legal-specific splitting: Prioritize double-newlines (Section breaks) 
#     # and numbered lists.
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#         separators=["\n\n", "\n", "ARTICLE", "SECTION", ".", " ", ""]
#     )
    
#     chunks = text_splitter.split_text(raw_text)
    
#     chunks_df = pd.DataFrame({
#         "chunk_id": [f"legal_chunk_{i}" for i in range(len(chunks))],
#         "chunk_text": chunks,
#         "domain": "legal" # Domain Isolation
#     })
    
#     print(f"✅ Legal document processed into {len(chunks_df)} chunks.")
#     return chunks_df