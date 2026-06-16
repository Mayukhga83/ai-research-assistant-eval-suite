# AI Research Assistant Evaluation Suite

This repository is an educational project for building and evaluating AI research assistants.

The project focuses on:

- Scientific abstract analysis
- Structured paper summarization
- Claim extraction
- Citation-grounded question answering
- Faithfulness evaluation
- Relevance evaluation
- Hallucination-risk checks
- Citation coverage metrics
- Benchmark execution
- Streamlit dashboard prototypes


## Project goals

The goal is to build a practical framework that can test whether an AI research assistant can:

1. Read a paper abstract and extract structured information.
2. Identify research claims, methods, datasets, metrics, results, and limitations.
3. Answer questions using retrieved document context.
4. Cite the evidence used for each answer.
5. Evaluate output quality with clear rubrics and simple automated checks.
6. Run repeatable benchmarks across prompts and models.
7. Display results in a simple dashboard.

## Repository structure

```text
01_abstract_analysis/
02_research_qa/
03_claim_extraction/
04_evaluation_metrics/
05_benchmark_runner/
06_streamlit_dashboard/
07_experiments/
docs/
tests/
```

## Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Example commands

Analyze an abstract:

```bash
python 01_abstract_analysis/abstract_parser.py
```

Run claim extraction:

```bash
python 03_claim_extraction/claim_extractor.py
```

Run benchmark:

```bash
python 05_benchmark_runner/run_benchmark.py
```

Run dashboard:

```bash
streamlit run 06_streamlit_dashboard/dashboard.py
```

