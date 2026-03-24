from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .contracts import EvalCase, Prediction


@dataclass(frozen=True)
class Score:
    case_id: str
    metric: str
    value: float
    passed: bool
    details: dict


def normalize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def exact_match(case: EvalCase, prediction: Prediction) -> Score:
    value = float(normalize(case.reference) == normalize(prediction.output))
    return Score(case.id, "exact_match", value, bool(value), {})


def token_f1(case: EvalCase, prediction: Prediction, threshold: float = 0.7) -> Score:
    expected, actual = set(normalize(case.reference)), set(normalize(prediction.output))
    precision = len(expected & actual) / len(actual) if actual else 0
    recall = len(expected & actual) / len(expected) if expected else 0
    value = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return Score(case.id, "token_f1", value, value >= threshold, {"precision": precision, "recall": recall})


def retrieval_metrics(case: EvalCase, prediction: Prediction, k: int = 5) -> dict[str, float]:
    relevant, retrieved = set(case.relevant_ids), prediction.retrieved_ids[:k]
    recall = len(relevant & set(retrieved)) / len(relevant) if relevant else 0
    rank = next((i for i, item in enumerate(retrieved, 1) if item in relevant), None)
    dcg = sum((1 if item in relevant else 0) / math.log2(i + 1) for i, item in enumerate(retrieved, 1))
    ideal = sum(1 / math.log2(i + 1) for i in range(1, min(k, len(relevant)) + 1))
    return {f"recall@{k}": recall, "mrr": 1 / rank if rank else 0, f"ndcg@{k}": dcg / ideal if ideal else 0}


def citation_metrics(case: EvalCase, prediction: Prediction, sources: dict[str, str]) -> dict[str, float]:
    valid = [citation for citation in prediction.citations if citation.quote.casefold() in sources.get(citation.source_id, "").casefold()]
    precision = len(valid) / len(prediction.citations) if prediction.citations else 0
    coverage = len({citation.source_id for citation in valid} & set(case.relevant_ids)) / len(case.relevant_ids) if case.relevant_ids else precision
    return {"citation_precision": precision, "citation_coverage": coverage}


def bootstrap_interval(values: Sequence[float], samples: int = 500, seed: int = 42) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    rng, means = random.Random(seed), []
    for _ in range(samples):
        means.append(sum(rng.choice(values) for _ in values) / len(values))
    means.sort()
    return means[int(samples * 0.025)], means[min(samples - 1, int(samples * 0.975))]


def slice_report(cases: Iterable[EvalCase], values: dict[str, float]) -> dict[str, float]:
    groups: dict[str, list[float]] = {}
    for case in cases:
        groups.setdefault(case.slice, []).append(values[case.id])
    return {name: sum(group) / len(group) for name, group in groups.items()}
