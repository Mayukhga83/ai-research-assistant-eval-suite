from schema import StructuredSummary
from keyword_extractor import extract_keywords


METHOD_HINTS = ["propose", "introduce", "use", "combine", "adapt", "train", "evaluate"]
RESULT_HINTS = ["improve", "outperform", "increase", "reduce", "achieve", "preserve"]
LIMITATION_HINTS = ["limitation", "however", "although", "fail", "challenge"]


def summarize_abstract(title: str, abstract: str) -> StructuredSummary:
    lowered = abstract.lower()
    sentences = [s.strip() for s in abstract.split(".") if s.strip()]

    method = ""
    result = ""
    limitation = ""

    for sentence in sentences:
        s_low = sentence.lower()
        if not method and any(h in s_low for h in METHOD_HINTS):
            method = sentence
        if not result and any(h in s_low for h in RESULT_HINTS):
            result = sentence
        if not limitation and any(h in s_low for h in LIMITATION_HINTS):
            limitation = sentence

    return StructuredSummary(
        task=title,
        method=method,
        result=result,
        limitation=limitation,
        keywords=extract_keywords(abstract),
    )


if __name__ == "__main__":
    title = "Evaluating Faithfulness in Long-Form Question Answering"
    abstract = "Faithfulness evaluation measures whether generated answers are supported by source documents. We introduce automatic checks for identifying unsupported claims."
    print(summarize_abstract(title, abstract).model_dump())
