# System Design

## Inputs

The system accepts:

- Paper title
- Abstract
- Optional PDF text
- Question
- Model output
- Retrieved evidence chunks

## Outputs

The system produces:

- Structured summary
- Extracted claims
- Citation-grounded answer
- Evaluation scores
- Benchmark CSV files
- Dashboard views

## Design principles

- Keep modules independent.
- Prefer transparent heuristics for the MVP.
- Make outputs inspectable.
- Store results in simple formats such as JSONL and CSV.
