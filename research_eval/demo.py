"""Dependency-light end-to-end evaluation demonstration."""

from __future__ import annotations

import json

from .benchmark import BenchmarkSpec, run_benchmark, summarize
from .contracts import Citation, EvalCase, PaperDocument, Prediction
from .ingestion import chunk_document
from .metrics import citation_metrics, retrieval_metrics, token_f1
from .retrieval import BM25Retriever


def run_demo() -> dict:
    paper = PaperDocument("paper-1", "Hybrid Retrieval", "Hybrid retrieval combines lexical and semantic evidence to improve recall.", 2026)
    retriever = BM25Retriever(chunk_document(paper))
    case = EvalCase("case-1", "What does hybrid retrieval combine?", "lexical and semantic evidence", ("paper-1:0",), "grounded_qa")

    def predict(item: EvalCase) -> Prediction:
        result = retriever.search(item.input, 1)[0]
        quote = "lexical and semantic evidence"
        return Prediction(item.id, quote, (result.chunk.id,), (Citation(result.chunk.id, quote),))

    records = run_benchmark([case], predict)
    prediction = records[0].prediction
    return {
        "benchmark": BenchmarkSpec("offline-demo", "deterministic-baseline", "v1").id,
        "run": summarize(records),
        "answer": token_f1(case, prediction).value,
        "retrieval": retrieval_metrics(case, prediction),
        "citations": citation_metrics(case, prediction, {chunk.id: chunk.text for chunk in chunk_document(paper)}),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2))
