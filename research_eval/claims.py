from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

from .contracts import SourceSpan


@dataclass(frozen=True)
class Claim:
    id: str
    text: str
    kind: str
    evidence: tuple[SourceSpan, ...] = ()
    confidence: float = 0.5

    def __post_init__(self) -> None:
        if self.kind not in {"finding", "method", "assumption", "limitation", "background"}:
            raise ValueError("unsupported claim kind")
        if not 0 <= self.confidence <= 1:
            raise ValueError("invalid claim confidence")


@dataclass
class ClaimGraph:
    claims: dict[str, Claim] = field(default_factory=dict)
    edges: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, claim: Claim) -> None:
        self.claims[claim.id] = claim

    def relate(self, source: str, relation: str, target: str) -> None:
        if source not in self.claims or target not in self.claims:
            raise KeyError("both claims must exist")
        if relation not in {"supports", "refutes", "extends", "duplicates"}:
            raise ValueError("unsupported relation")
        self.edges.append((source, relation, target))


def segment_claims(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in sentences if len(sentence.split()) >= 4]


def classify_claim(text: str) -> str:
    lowered = text.casefold()
    if any(term in lowered for term in ("we use", "method", "trained", "dataset")):
        return "method"
    if any(term in lowered for term in ("limitation", "however", "cannot", "future work")):
        return "limitation"
    if any(term in lowered for term in ("improves", "outperforms", "results", "achieves")):
        return "finding"
    return "background"


def lexical_similarity(left: str, right: str) -> float:
    a, b = set(re.findall(r"\w+", left.casefold())), set(re.findall(r"\w+", right.casefold()))
    return len(a & b) / len(a | b) if a | b else 1.0


def deduplicate_claims(claims: Iterable[Claim], threshold: float = 0.85) -> list[Claim]:
    output = []
    for claim in claims:
        if not any(lexical_similarity(claim.text, previous.text) >= threshold for previous in output):
            output.append(claim)
    return output
