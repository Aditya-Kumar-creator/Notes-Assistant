"""
PDF Notes Assistant
-------------------
Upload lecture PDFs, pick a page range (a "chapter"), then:
  - get a summary
  - generate a quiz
  - generate flashcards and export them to Anki
  - ask questions about the selected pages
  - keyword-search across all uploaded PDFs

Uses the free Google Gemini API (get a key at https://aistudio.google.com).
Scanned PDFs are read with OCR if Tesseract is installed (optional).

Setup:
    pip install streamlit pymupdf pypdf google-genai pytesseract pillow

Run:
    export GEMINI_API_KEY="your-key"     (Windows: set GEMINI_API_KEY=your-key)
    streamlit run notes_assistant.py
"""

import json
import os
import re

import io

import streamlit as st
from google import genai

try:  # PyMuPDF is the main PDF reader
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:  # for example Windows blocked its DLL file
    from pypdf import PdfReader  # simple fallback, no DLL needed
    HAS_FITZ = False

try:  # OCR is optional
    import pytesseract
    from PIL import Image
    # Windows only: uncomment and fix the path if Tesseract is not found
    # pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

MODEL = "gemini-3.5-flash"  # if you hit quota limits, try "gemini-2.5-flash"
MAX_CHARS = 60000            # limit text sent to the model


# ---------- helpers ----------

def ocr_page(page) -> str:
    """Read a scanned page image with Tesseract."""
    pix = page.get_pixmap(dpi=200)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    return pytesseract.image_to_string(img)


@st.cache_data
def extract_pages(file_bytes: bytes) -> list[str]:
    """Return the text of each page. Uses OCR for pages with no real text."""
    if not HAS_FITZ:  # fallback reader, no OCR
        reader = PdfReader(io.BytesIO(file_bytes))
        return [(p.extract_text() or "") for p in reader.pages]
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    pages = []
    for page in doc:
        text = page.get_text()
        if len(text.strip()) < 20 and OCR_AVAILABLE:
            try:
                text = ocr_page(page)
            except Exception:
                pass  # Tesseract engine not installed; keep empty text
        pages.append(text)
    return pages


def get_chapter_text(pages: list[str], start: int, end: int) -> str:
    return "\n".join(pages[start - 1:end])[:MAX_CHARS]


def ask_llm(client, prompt: str, max_tokens: int = 2000) -> str:
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text or ""
    except Exception as e:
        st.error(f"API error: {e}")
        return ""


def parse_json_list(text: str) -> list:
    """Pull the first JSON list out of the model's reply."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        return []
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return []


def search_notes(docs: dict, keyword: str) -> list[tuple]:
    """Find a keyword in every page of every PDF."""
    results = []
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    for name, pages in docs.items():
        for page_no, text in enumerate(pages, start=1):
            match = pattern.search(text)
            if match:
                s = max(0, match.start() - 60)
                e = min(len(text), match.end() + 60)
                snippet = text[s:e].replace("\n", " ")
                results.append((name, page_no, snippet))
    return results


def flashcards_to_anki(cards: list[dict]) -> str:
    """Tab-separated text, which Anki imports directly (File > Import)."""
    lines = []
    for c in cards:
        front = str(c.get("front", "")).replace("\t", " ").replace("\n", " ")
        back = str(c.get("back", "")).replace("\t", " ").replace("\n", " ")
        lines.append(f"{front}\t{back}")
    return "\n".join(lines)


# ---------- page setup ----------

st.set_page_config(page_title="PDF Notes Assistant", layout="wide")
st.title("PDF Notes Assistant")
if not HAS_FITZ:
    st.sidebar.info("PyMuPDF could not load, so the simpler pypdf reader is used. OCR is off.")

api_key = os.getenv("GEMINI_API_KEY") or st.sidebar.text_input(
    "Gemini API key (free)", type="password"
)
if not api_key:
    st.info("Add your free Gemini API key in the sidebar (or set GEMINI_API_KEY).")
    st.stop()
client = genai.Client(api_key=api_key)

uploaded = st.sidebar.file_uploader(
    "Upload PDFs", type="pdf", accept_multiple_files=True
)
if not uploaded:
    st.info("Upload one or more PDFs from the sidebar.")
    st.stop()

docs = {f.name: extract_pages(f.getvalue()) for f in uploaded}

# empty text usually means a scanned PDF
for name, pages in docs.items():
    if sum(len(p.strip()) for p in pages) < 50:
        st.warning(f"{name} has almost no extractable text. It may be a scanned PDF.")

# choose document and chapter (page range)
doc_name = st.sidebar.selectbox("Document", list(docs.keys()))
pages = docs[doc_name]
total = len(pages)
start = st.sidebar.number_input("Start page", 1, total, 1)
end = st.sidebar.number_input("End page", 1, total, min(total, 10))
if end < start:
    st.sidebar.error("End page must be after start page.")
    st.stop()

chapter = get_chapter_text(pages, start, end)
st.caption(f"Working on {doc_name}, pages {start} to {end} ({len(chapter)} characters)")

tab_sum, tab_quiz, tab_cards, tab_ask, tab_search = st.tabs(
    ["Summary", "Quiz", "Flashcards", "Ask", "Search"]
)

# ---------- summary ----------
with tab_sum:
    if st.button("Summarize these pages"):
        with st.spinner("Summarizing..."):
            st.session_state["summary"] = ask_llm(
                client,
                "Summarize these lecture notes for a student. Use short headings "
                "and bullet points, and list key terms at the end.\n\n" + chapter,
            )
    st.markdown(st.session_state.get("summary", ""))

# ---------- quiz ----------
with tab_quiz:
    n_q = st.slider("Number of questions", 3, 10, 5)
    if st.button("Generate quiz"):
        with st.spinner("Writing questions..."):
            reply = ask_llm(
                client,
                f"Create {n_q} multiple choice questions from these notes. "
                "Reply with ONLY a JSON list. Each item: "
                '{"question": "...", "options": ["A...", "B...", "C...", "D..."], '
                '"answer": "the correct option text", "explanation": "one line"}\n\n'
                + chapter,
                max_tokens=3000,
            )
            st.session_state["quiz"] = parse_json_list(reply)

    for i, q in enumerate(st.session_state.get("quiz", []), start=1):
        st.markdown(f"**Q{i}. {q.get('question', '')}**")
        choice = st.radio(
            "Your answer", q.get("options", []), key=f"quiz_{i}", index=None
        )
        if choice:
            if choice == q.get("answer"):
                st.success("Correct. " + q.get("explanation", ""))
            else:
                st.error(f"Not quite. Answer: {q.get('answer')}. " + q.get("explanation", ""))

# ---------- flashcards ----------
with tab_cards:
    n_c = st.slider("Number of flashcards", 5, 25, 10)
    if st.button("Generate flashcards"):
        with st.spinner("Making flashcards..."):
            reply = ask_llm(
                client,
                f"Create {n_c} flashcards from these notes. Reply with ONLY a JSON "
                'list. Each item: {"front": "question or term", "back": "short answer"}\n\n'
                + chapter,
                max_tokens=3000,
            )
            st.session_state["cards"] = parse_json_list(reply)

    cards = st.session_state.get("cards", [])
    for c in cards:
        with st.expander(c.get("front", "")):
            st.write(c.get("back", ""))
    if cards:
        st.download_button(
            "Download for Anki (.txt)",
            flashcards_to_anki(cards),
            file_name="flashcards.txt",
            help="In Anki: File > Import, choose this file, fields separated by tab.",
        )

# ---------- ask ----------
with tab_ask:
    question = st.text_input("Ask a question about these pages")
    if question:
        with st.spinner("Thinking..."):
            answer = ask_llm(
                client,
                "Answer the question using only the notes below. If the notes do "
                "not contain the answer, say so.\n\nNOTES:\n" + chapter
                + "\n\nQUESTION: " + question,
            )
        st.markdown(answer)

# ---------- search ----------
with tab_search:
    keyword = st.text_input("Search all uploaded PDFs")
    if keyword:
        hits = search_notes(docs, keyword)
        st.write(f"{len(hits)} page(s) found")
        for name, page_no, snippet in hits:
            st.markdown(f"**{name}**, page {page_no}: ...{snippet}...")
