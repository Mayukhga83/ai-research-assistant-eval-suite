from __future__ import annotations

import concurrent.futures
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping

from .contracts import EvalCase, Prediction


@dataclass(frozen=True)
class BenchmarkSpec:
    name: str
    model: str
    prompt_version: str
    seed: int = 42
    max_workers: int = 4

    @property
    def id(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:12]


@dataclass(frozen=True)
class RunRecord:
    case_id: str
    prediction: Prediction
    latency_ms: float
    failed: bool = False
    error: str = ""


def run_case(case: EvalCase, predict: Callable[[EvalCase], Prediction]) -> RunRecord:
    start = time.perf_counter()
    try:
        prediction = predict(case)
        return RunRecord(case.id, prediction, (time.perf_counter() - start) * 1000)
    except Exception as error:
        return RunRecord(case.id, Prediction(case.id, ""), (time.perf_counter() - start) * 1000, True, type(error).__name__)


def run_benchmark(cases: Iterable[EvalCase], predict: Callable[[EvalCase], Prediction], max_workers: int = 4) -> list[RunRecord]:
    cases = list(cases)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        records = list(pool.map(lambda case: run_case(case, predict), cases))
    return sorted(records, key=lambda record: record.case_id)


def save_records(records: Iterable[RunRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(asdict(record), default=str, sort_keys=True) for record in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def summarize(records: Iterable[RunRecord]) -> dict[str, float]:
    records = list(records)
    return {
        "cases": len(records),
        "failure_rate": sum(record.failed for record in records) / len(records) if records else 0,
        "mean_latency_ms": sum(record.latency_ms for record in records) / len(records) if records else 0,
    }
