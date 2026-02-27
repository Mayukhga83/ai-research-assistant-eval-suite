from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Protocol

from .ingestion import Chunk


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


@dataclass(frozen=True)
class SearchResult:
    chunk: Chunk
    score: float


class Retriever(Protocol):
    def search(self, query: str, limit: int = 5) -> list[SearchResult]: ...


class BM25Retriever:
    def __init__(self, chunks: Iterable[Chunk]) -> None:
        self.chunks = list(chunks)
        self.tokens = [tokenize(chunk.text) for chunk in self.chunks]
        self.df = Counter(term for tokens in self.tokens for term in set(tokens))
        self.avg = sum(map(len, self.tokens)) / max(1, len(self.tokens))

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        results = []
        for chunk, tokens in zip(self.chunks, self.tokens):
            counts, score = Counter(tokens), 0.0
            for term in tokenize(query):
                tf = counts[term]
                idf = math.log(1 + (len(self.chunks) - self.df[term] + 0.5) / (self.df[term] + 0.5))
                score += idf * tf * 2.5 / (tf + 1.5 * (0.25 + 0.75 * len(tokens) / max(1, self.avg))) if tf else 0
            results.append(SearchResult(chunk, score))
        return sorted(results, key=lambda item: (-item.score, item.chunk.id))[:limit]


def reciprocal_rank_fusion(lists: Iterable[list[SearchResult]], k: int = 60, limit: int = 5) -> list[SearchResult]:
    scores, chunks = defaultdict(float), {}
    for results in lists:
        for rank, result in enumerate(results, 1):
            scores[result.chunk.id] += 1 / (k + rank)
            chunks[result.chunk.id] = result.chunk
    return [SearchResult(chunks[key], scores[key]) for key in sorted(scores, key=lambda key: (-scores[key], key))[:limit]]


def decompose(query: str) -> list[str]:
    return [part.strip() for part in re.split(r"\s+(?:and|versus|vs\.?|then)\s+", query, flags=re.I) if part.strip()]


def verify_quote(result: SearchResult, quote: str) -> bool:
    return bool(quote.strip()) and quote.casefold() in result.chunk.text.casefold()
