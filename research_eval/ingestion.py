from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

from .contracts import PaperDocument, SourceSpan


@dataclass(frozen=True)
class Section:
    heading: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    section: str
    start: int
    end: int


def normalize_text(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\r\n", "\n")
    return re.sub(r"[ \t]+", " ", text).strip()


def segment_sections(text: str) -> list[Section]:
    pattern = re.compile(r"(?m)^(abstract|introduction|methods?|results?|discussion|conclusion|limitations?|references)\s*$", re.I)
    matches = list(pattern.finditer(text))
    if not matches:
        return [Section("document", text.strip(), 0, len(text))]
    sections = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(Section(match.group().lower(), text[match.end():end].strip(), match.start(), end))
    return sections


def chunk_document(document: PaperDocument, size: int = 800, overlap: int = 120) -> list[Chunk]:
    if size <= overlap or overlap < 0:
        raise ValueError("chunk size must exceed non-negative overlap")
    chunks = []
    for section in segment_sections(document.text):
        cursor = 0
        while cursor < len(section.text):
            end = min(len(section.text), cursor + size)
            text = section.text[cursor:end].strip()
            if text:
                chunks.append(Chunk(f"{document.id}:{len(chunks)}", document.id, text, section.heading, section.start + cursor, section.start + end))
            if end == len(section.text):
                break
            cursor = end - overlap
    return chunks


def deduplicate(chunks: Iterable[Chunk]) -> list[Chunk]:
    seen, output = set(), []
    for chunk in chunks:
        key = re.sub(r"\W+", " ", chunk.text.casefold()).strip()
        if key not in seen:
            seen.add(key)
            output.append(chunk)
    return output


def locate_quote(document: PaperDocument, quote: str, page: int = 1) -> SourceSpan | None:
    start = document.text.casefold().find(quote.casefold())
    return None if start < 0 else SourceSpan(document.id, page, start, start + len(quote), document.text[start:start + len(quote)])
