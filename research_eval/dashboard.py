from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Iterable

from .benchmark import RunRecord
from .metrics import Score, bootstrap_interval


def overview(records: Iterable[RunRecord], scores: Iterable[Score]) -> dict:
    records, scores = list(records), list(scores)
    values = [score.value for score in scores]
    low, high = bootstrap_interval(values) if values else (0.0, 0.0)
    return {
        "cases": len(records),
        "failures": sum(record.failed for record in records),
        "mean_score": sum(values) / len(values) if values else 0.0,
        "confidence_interval": [low, high],
    }


def failure_drilldown(records: Iterable[RunRecord], scores: Iterable[Score]) -> list[dict]:
    by_case = defaultdict(list)
    for score in scores:
        if not score.passed:
            by_case[score.case_id].append(score.metric)
    return [{"case_id": record.case_id, "error": record.error, "failed_metrics": by_case[record.case_id]} for record in records if record.failed or by_case[record.case_id]]


def markdown_report(summary: dict) -> str:
    return "\n".join(["# Evaluation Report", "", *[f"- **{key.replace('_', ' ').title()}:** {value}" for key, value in summary.items()]])
