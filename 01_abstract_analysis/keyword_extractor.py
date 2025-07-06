from collections import Counter
import re


STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
    "by", "we", "this", "that", "is", "are", "as", "from"
}


def extract_keywords(text: str, top_k: int = 8):
    words = re.findall(r"[A-Za-z][A-Za-z\-]+", text.lower())
    words = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return [word for word, _ in Counter(words).most_common(top_k)]


if __name__ == "__main__":
    sample = "Retrieval augmented generation improves factual grounding with external documents."
    print(extract_keywords(sample))
