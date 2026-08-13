"""Local knowledge retrieval for OL Mate.

The app can work immediately with built-in O/L revision notes, and it will also
use text, markdown, and PDF files placed in the knowledge_base directory.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from config import settings

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}
STOPWORDS = {
    "about", "after", "also", "and", "are", "ask", "can", "for", "from", "give",
    "has", "how", "into", "is", "it", "main", "of", "ol", "on", "or", "question",
    "show", "solve", "the", "this", "to", "use", "what", "when", "where", "why",
    "with",
}

DEFAULT_SUBJECT_NOTES = {
    "Mathematics": [
        "Algebra answers should show substitution, simplification, and the final value with units when needed.",
        "Geometry questions need the relevant theorem, known values, working steps, and a clear final angle or length.",
        "Statistics answers should identify the data, choose the correct average or graph, and show calculation steps.",
    ],
    "Science": [
        "Photosynthesis uses carbon dioxide and water to make glucose in the presence of light and chlorophyll, releasing oxygen.",
        "Cells contain structures such as the nucleus, cytoplasm, cell membrane, and vacuole, each with a specific function.",
        "For forces and energy questions, state the law or principle, substitute values, and include the correct unit.",
    ],
    "English": [
        "Grammar answers should identify the tense, subject agreement, punctuation, or word class before giving the correction.",
        "Comprehension answers need evidence from the passage and should be written in clear complete sentences.",
        "Writing tasks should have a suitable opening, ordered ideas, linking words, and a focused ending.",
    ],
    "Sinhala": [
        "Sinhala language answers should focus on meaning, grammar, sentence structure, and suitable vocabulary.",
        "Literature answers should mention the text, character or event, and explain the idea with a short example.",
    ],
    "Tamil": [
        "Tamil language answers should focus on meaning, grammar, sentence structure, and suitable vocabulary.",
        "Literature answers should mention the text, character or event, and explain the idea with a short example.",
    ],
    "History": [
        "History answers should place events in order and explain causes, key people, dates, and results.",
        "Cause-and-effect questions need both the reasons an event happened and the changes that followed.",
    ],
    "Buddhism": [
        "Buddhism answers should state the teaching, explain its meaning, and connect it to daily life.",
        "Value-based questions should include a practical example and a moral lesson.",
    ],
    "Christianity": [
        "Christianity answers should explain the teaching, its value, and how it can be practiced in daily life.",
        "Bible-related answers should connect the event or teaching to faith, conduct, and community.",
    ],
    "Islam": [
        "Islam answers should explain the teaching, its value, and how it guides daily conduct.",
        "Practice-based answers should connect belief, action, discipline, and respect for others.",
    ],
    "Hinduism": [
        "Hinduism answers should explain the teaching, its value, and how it shapes daily life.",
        "Practice-based answers should connect worship, duty, discipline, and respect for others.",
    ],
    "ICT": [
        "ICT answers should define the term, describe how it works, and give a practical example.",
        "Hardware and software questions should separate input, process, output, storage, and communication clearly.",
    ],
    "Commerce": [
        "Commerce answers should define the business term, explain its purpose, and give a simple real-life example.",
        "Accounting and trade questions need correct keywords, ordered steps, and clear calculations when required.",
    ],
    "Geography": [
        "Geography answers should explain location, physical or human factors, process, and impact.",
        "Map and climate questions should use correct terms, observations, and evidence from the given data.",
    ],
    "Civic Education": [
        "Civic Education answers should explain rights, responsibilities, institutions, and citizen participation.",
        "Society questions should connect the rule or value to school, family, community, and national life.",
    ],
}


@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    subject: str
    text: str


def process_pdf(file_path: str) -> dict:
    """Validate a PDF is readable and report how many text chunks it contains."""
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files can be processed with process_pdf")

    text = _read_pdf(path)
    chunks = list(_split_text(text))
    return {"filename": path.name, "chunks": len(chunks)}


def retrieve_relevant_context(query: str, subject: str = "", top_k: int = 5) -> str:
    """Retrieve relevant context from uploaded files and built-in subject notes."""
    clean_query = " ".join(query.split())
    if not clean_query and not subject:
        return ""

    chunks = _load_knowledge_chunks()
    scored_chunks = []
    query_terms = _tokenize(clean_query)

    for chunk in chunks:
        score = _score_chunk(chunk, query_terms, subject)
        if score > 0:
            scored_chunks.append((score, chunk))

    if not scored_chunks and subject:
        scored_chunks = [
            (1, chunk)
            for chunk in _default_chunks()
            if chunk.subject.lower() == subject.lower()
        ]

    scored_chunks.sort(key=lambda item: item[0], reverse=True)
    selected_chunks = [chunk for _, chunk in scored_chunks[:top_k]]
    return _format_context(selected_chunks)


def augment_query_with_context(question: str, context: str) -> str:
    """Combine a question with relevant context for an AI model prompt."""
    if not context:
        return question

    return (
        "Use this O/L knowledge context when helpful:\n"
        f"{context}\n\n"
        f"Student question: {question}"
    )


def _knowledge_base_path() -> Path:
    return Path(settings.KNOWLEDGE_BASE_PATH).expanduser().resolve()


def _load_knowledge_chunks() -> list[KnowledgeChunk]:
    chunks = _default_chunks()
    base_path = _knowledge_base_path()
    if not base_path.exists():
        return chunks

    for path in base_path.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        text = _read_document(path)
        subject = _infer_subject(path)
        for index, chunk_text in enumerate(_split_text(text), start=1):
            chunks.append(KnowledgeChunk(
                source=f"{path.name} #{index}",
                subject=subject,
                text=chunk_text,
            ))

    return chunks


def _default_chunks() -> list[KnowledgeChunk]:
    return [
        KnowledgeChunk(source="Built-in O/L notes", subject=subject, text=note)
        for subject, notes in DEFAULT_SUBJECT_NOTES.items()
        for note in notes
    ]


def _read_document(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("pypdf is required to read PDF knowledge files") from exc

    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def _infer_subject(path: Path) -> str:
    lower_parts = " ".join(part.lower() for part in path.parts)
    for subject in DEFAULT_SUBJECT_NOTES:
        if subject.lower() in lower_parts:
            return subject
    return "General"


def _split_text(text: str, chunk_size: int = 850) -> Iterable[str]:
    clean_text = re.sub(r"\s+", " ", text).strip()
    if not clean_text:
        return []

    chunks = []
    start = 0
    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        if end < len(clean_text):
            sentence_end = clean_text.rfind(".", start, end)
            if sentence_end > start + 200:
                end = sentence_end + 1
        chunks.append(clean_text[start:end].strip())
        start = end
    return chunks


def _score_chunk(chunk: KnowledgeChunk, query_terms: set[str], subject: str) -> int:
    chunk_terms = _tokenize(chunk.text)
    score = len(query_terms.intersection(chunk_terms))
    if score == 0:
        return 0
    if subject and chunk.subject.lower() == subject.lower():
        score += 3
    return score


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(token) > 2 and token not in STOPWORDS
    }


def _format_context(chunks: list[KnowledgeChunk]) -> str:
    if not chunks:
        return ""

    return "\n\n".join(
        f"Source: {chunk.source}\nSubject: {chunk.subject}\n{chunk.text}"
        for chunk in chunks
    )
