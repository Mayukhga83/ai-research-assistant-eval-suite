from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class SourceSpan:
    document_id: str
    page: int
    start: int
    end: int
    quote: str

    def __post_init__(self) -> None:
        if self.page < 1 or self.start < 0 or self.end <= self.start:
            raise ValueError("invalid source coordinates")


@dataclass(frozen=True)
class PaperDocument:
    id: str
    title: str
    text: str
    year: int | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"

    def checksum(self) -> str:
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Citation:
    source_id: str
    quote: str
    page: int | None = None


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: tuple[Citation, ...]
    confidence: float
    abstained: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between zero and one")
        if not self.abstained and not self.citations:
            raise ValueError("non-abstaining answers require citations")


@dataclass(frozen=True)
class EvalCase:
    id: str
    input: str
    reference: str = ""
    relevant_ids: tuple[str, ...] = ()
    slice: str = "default"
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Prediction:
    case_id: str
    output: str
    retrieved_ids: tuple[str, ...] = ()
    citations: tuple[Citation, ...] = ()
    trace: Sequence[Mapping[str, Any]] = field(default_factory=tuple)


def deterministic_split(identifier: str, eval_fraction: float = 0.2) -> str:
    if not 0 < eval_fraction < 1:
        raise ValueError("eval_fraction must be between zero and one")
    bucket = int(hashlib.sha256(identifier.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "evaluation" if bucket < eval_fraction else "train"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def manifest(records: Sequence[PaperDocument]) -> dict[str, Any]:
    items = [{"id": record.id, "checksum": record.checksum(), "schema_version": record.schema_version} for record in records]
    return {"count": len(items), "records": items}
