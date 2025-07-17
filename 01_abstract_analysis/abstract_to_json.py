import json
from abstract_parser import load_examples
from structured_summary import summarize_abstract


def convert_examples(output_path: str = "outputs/abstract_summaries.jsonl"):
    import os
    os.makedirs("outputs", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for record in load_examples():
            summary = summarize_abstract(record.title, record.abstract)
            row = {
                "paper_id": record.paper_id,
                "title": record.title,
                "summary": summary.model_dump(),
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    convert_examples()
    print("Wrote outputs/abstract_summaries.jsonl")
