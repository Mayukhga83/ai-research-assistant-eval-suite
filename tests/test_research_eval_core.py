import unittest

from research_eval.claims import Claim, ClaimGraph, classify_claim, segment_claims
from research_eval.contracts import Citation, GroundedAnswer, PaperDocument, deterministic_split
from research_eval.ingestion import chunk_document, locate_quote, segment_sections
from research_eval.retrieval import BM25Retriever, reciprocal_rank_fusion, verify_quote


class CoreTests(unittest.TestCase):
    def test_contracts_and_split_are_deterministic(self):
        self.assertEqual(deterministic_split("paper-1"), deterministic_split("paper-1"))
        self.assertEqual(GroundedAnswer("answer", (Citation("p", "evidence"),), 0.8).confidence, 0.8)

    def test_ingestion_preserves_coordinates(self):
        paper = PaperDocument("p", "Title", "Methods\nWe use a benchmark.\nResults\nThe system improves recall.")
        self.assertEqual(len(segment_sections(paper.text)), 2)
        self.assertTrue(chunk_document(paper, size=30, overlap=5))
        self.assertEqual(locate_quote(paper, "improves recall").document_id, "p")

    def test_retrieval_and_fusion(self):
        paper = PaperDocument("p", "Title", "Hybrid retrieval combines lexical and semantic evidence.")
        chunks = chunk_document(paper)
        retriever = BM25Retriever(chunks)
        results = retriever.search("hybrid lexical")
        self.assertTrue(verify_quote(results[0], "lexical and semantic"))
        self.assertEqual(reciprocal_rank_fusion([results, results])[0].chunk.id, chunks[0].id)

    def test_claim_graph(self):
        self.assertEqual(classify_claim("The model outperforms the baseline."), "finding")
        self.assertEqual(len(segment_claims("The model improves recall. It uses a public dataset.")), 2)
        graph = ClaimGraph()
        graph.add(Claim("a", "A finding improves recall.", "finding"))
        graph.add(Claim("b", "A method uses data.", "method"))
        graph.relate("b", "supports", "a")
        self.assertEqual(len(graph.edges), 1)


if __name__ == "__main__":
    unittest.main()
