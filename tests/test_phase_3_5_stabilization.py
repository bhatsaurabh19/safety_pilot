import unittest

from src.evaluation.prompt_builder import PromptBuilder
from src.evaluation.schema import SchemaValidationError, SchemaValidator
from src.retrieval.retriever import Retriever


class PromptBuilderTests(unittest.TestCase):
    def test_string_evidence_is_not_split_character_by_character(self):
        prompt = PromptBuilder().build(
            clause_id="3.5",
            clause_title="Item Definition",
            clause_text="Define item boundaries.",
            retrieved_chunks="HARA evidence",
        )

        self.assertIn("HARA evidence", prompt)
        self.assertNotIn("H\nA\nR\nA", prompt)

    def test_list_evidence_is_joined_by_chunk(self):
        prompt = PromptBuilder().build(
            clause_id="3.5",
            clause_title="Item Definition",
            clause_text="Define item boundaries.",
            retrieved_chunks=["first evidence", "second evidence"],
        )

        self.assertIn("first evidence\n\nsecond evidence", prompt)


class SchemaConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.validator = SchemaValidator()

    def _result(self, status, evaluation):
        return {
            "clause_id": "3.5",
            "status": status,
            "confidence": 0.5,
            "evidence_confidence": 0.5,
            "evaluation": evaluation,
            "evidence": [],
            "gaps": [],
            "recommendations": [],
        }

    def test_partial_with_missing_evidence_is_rejected(self):
        result = self._result(
            "PARTIAL",
            {
                "presence": "NO",
                "coverage": "NONE",
                "evidence_quality": "NONE",
                "correctness": "MISALIGNED",
                "traceability": "MISSING",
            },
        )

        with self.assertRaises(SchemaValidationError):
            self.validator.validate(result)

    def test_compliant_requires_full_strict_evaluation(self):
        result = self._result(
            "COMPLIANT",
            {
                "presence": "YES",
                "coverage": "PARTIAL",
                "evidence_quality": "EXPLICIT",
                "correctness": "ALIGNED",
                "traceability": "CLEAR",
            },
        )

        with self.assertRaises(SchemaValidationError):
            self.validator.validate(result)


class RetrievalConfigTests(unittest.TestCase):
    def test_configured_similarity_threshold_filters_results(self):
        class FakeEmbedder:
            def embed_texts(self, texts):
                return [[1.0]]

        class FakeVectorStore:
            def search(self, query_embedding, top_k):
                return [
                    {"id": "high", "text": "strong", "score": 0.8, "metadata": {}},
                    {"id": "low", "text": "weak", "score": 0.4, "metadata": {}},
                ]

        retriever = Retriever(
            embedder=FakeEmbedder(),
            vectorstore=FakeVectorStore(),
            top_k=2,
            similarity_threshold=0.5,
        )

        result = retriever.get_relevant_chunks("query")

        self.assertEqual([chunk["id"] for chunk in result["chunks"]], ["high"])


if __name__ == "__main__":
    unittest.main()
