import json
from pathlib import Path
from typing import List
from schema import AbstractRecord


def load_examples(path: str = "01_abstract_analysis/examples.jsonl") -> List[AbstractRecord]:
    records = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(AbstractRecord(**json.loads(line)))
    return records


def simple_sentence_split(text: str):
    return [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]


def parse_abstract(record: AbstractRecord):
    sentences = simple_sentence_split(record.abstract)
    return {
        "paper_id": record.paper_id,
        "title": record.title,
        "num_sentences": len(sentences),
        "sentences": sentences,
    }


if __name__ == "__main__":
    for item in load_examples():
        print(parse_abstract(item))
