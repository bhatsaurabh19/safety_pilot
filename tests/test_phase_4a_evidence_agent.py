import unittest

from src.evaluation.evaluator import Evaluator
from src.evaluation.evidence import EvidenceAnalyzer
from src.evaluation.schema import SchemaValidator


class EvidenceAnalyzerTests(unittest.TestCase):
    def test_rerank_prefers_clause_term_overlap(self):
        retrieval_result = {
            "chunks": [
                {"id": "generic", "text": "general process notes", "score": 0.7},
                {
                    "id": "specific",
                    "text": "technical safety concept and safety mechanisms",
                    "score": 0.65,
                },
            ],
            "avg_score": 0.675,
            "retrieval_confidence": "MEDIUM",
        }

        reranked = EvidenceAnalyzer().rerank(
            clause_title="Technical Safety Concept",
            clause_text="The concept shall define safety mechanisms.",
            retrieval_result=retrieval_result,
        )

        self.assertEqual(reranked["chunks"][0]["id"], "specific")

    def test_weak_evidence_is_detected_when_no_chunks_are_available(self):
        analysis = EvidenceAnalyzer().analyze(
            clause_title="Safety Validation",
            clause_text="Validation shall confirm safety goals.",
            retrieval_result={
                "chunks": [],
                "avg_score": 0.0,
                "retrieval_confidence": "LOW",
            },
        )

        self.assertTrue(analysis["weak_evidence"])
        self.assertEqual(analysis["evidence_confidence"], 0.0)


class EvidenceAwareEvaluatorTests(unittest.TestCase):
    def test_retry_loop_uses_better_second_attempt(self):
        class FakeRetriever:
            def __init__(self):
                self.calls = []

            def get_relevant_chunks(self, query):
                self.calls.append(query)
                if len(self.calls) == 1:
                    return {
                        "chunks": [],
                        "avg_score": 0.0,
                        "retrieval_confidence": "LOW",
                    }
                return {
                    "chunks": [
                        {
                            "id": "chunk_1",
                            "text": "functional safety concept safety goals traceability",
                            "score": 0.9,
                            "metadata": {},
                        }
                    ],
                    "avg_score": 0.9,
                    "retrieval_confidence": "HIGH",
                }

        evaluator = Evaluator(
            retriever=FakeRetriever(),
            llm=None,
            schema_validator=SchemaValidator(),
            max_evidence_retries=2,
            weak_evidence_threshold=0.45,
        )

        result = evaluator._retrieve_evidence(
            clause_title="Functional Safety Concept",
            clause_text="Safety goals shall be traceable.",
        )

        self.assertEqual(len(result["retrieval_attempts"]), 2)
        self.assertFalse(result["evidence_analysis"]["weak_evidence"])
        self.assertEqual(result["chunks"][0]["id"], "chunk_1")

    def test_unsafe_compliant_result_is_downgraded_without_evidence(self):
        evaluator = Evaluator(
            retriever=None,
            llm=None,
            schema_validator=SchemaValidator(),
        )
        parsed = {
            "clause_id": "4.5",
            "status": "COMPLIANT",
            "confidence": 1.0,
            "evaluation": {
                "presence": "YES",
                "coverage": "FULL",
                "evidence_quality": "EXPLICIT",
                "correctness": "ALIGNED",
                "traceability": "CLEAR",
            },
            "evidence": [],
            "gaps": [],
            "recommendations": [],
        }

        constrained = evaluator._apply_evidence_constraints(
            parsed=parsed,
            retrieval_result={
                "retrieval_confidence": "HIGH",
                "evidence_analysis": {
                    "evidence_confidence": 0.8,
                    "weak_evidence": False,
                    "reasons": [],
                },
            },
        )

        self.assertEqual(constrained["status"], "NON_COMPLIANT")
        self.assertEqual(constrained["evidence_confidence"], 0.8)


if __name__ == "__main__":
    unittest.main()
