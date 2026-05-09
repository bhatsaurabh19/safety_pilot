import unittest

from src.agents.audit_agent import AuditAgent
from src.agents.report_agent import ReportAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.risk_agent import RiskAgent
from src.agents.traceability_agent import TraceabilityAgent
from src.aggregation.aggregator import Aggregator
from src.remediation.remediator import RemediationAgent


class MultiAgentSystemTests(unittest.TestCase):
    def test_retrieval_agent_returns_attempt_trace(self):
        class FakeRetriever:
            def get_relevant_chunks(self, query):
                return {
                    "chunks": [
                        {
                            "id": "chunk_1",
                            "text": "safety validation target environment safety goals",
                            "score": 0.9,
                            "metadata": {},
                        }
                    ],
                    "avg_score": 0.9,
                    "retrieval_confidence": "HIGH",
                }

        agent = RetrievalAgent(
            retriever=FakeRetriever(),
            max_evidence_retries=1,
            weak_evidence_threshold=0.45,
        )

        result = agent.retrieve(
            clause_title="Safety Validation",
            clause_text="Validation shall confirm safety goals.",
        )

        self.assertEqual(result["chunks"][0]["id"], "chunk_1")
        self.assertEqual(len(result["retrieval_attempts"]), 1)
        self.assertIn("evidence_analysis", result)

    def test_audit_agent_wraps_evaluator_results(self):
        class FakeEvaluator:
            def evaluate(self, clauses):
                return [{"clause_id": clauses[0]["clause_id"], "status": "COMPLIANT"}]

        result = AuditAgent(FakeEvaluator()).evaluate([
            {"clause_id": "3.5"}
        ])

        self.assertEqual(result["agent"], "audit_agent")
        self.assertEqual(result["clauses_evaluated"], 1)
        self.assertEqual(result["results"][0]["clause_id"], "3.5")

    def test_risk_agent_prioritizes_non_compliant_results(self):
        risk = RiskAgent().assess([
            {
                "clause_id": "4.6",
                "status": "NON_COMPLIANT",
                "confidence": 0.2,
                "evidence_confidence": 0.3,
                "gaps": ["Low evidence confidence"],
            },
            {
                "clause_id": "4.7",
                "status": "PARTIAL",
                "confidence": 0.4,
                "evidence_confidence": 0.4,
                "gaps": [],
            },
        ])

        self.assertEqual(risk["summary"]["high"], 1)
        self.assertEqual(risk["summary"]["medium"], 1)
        self.assertEqual(risk["risk_items"][0]["clause_id"], "4.6")

    def test_report_agent_builds_final_agent_sections(self):
        results = [
            {
                "clause_id": "4.8",
                "status": "NON_COMPLIANT",
                "confidence": 0.2,
                "evidence_confidence": 0.3,
                "evaluation": {
                    "presence": "NO",
                    "coverage": "NONE",
                    "evidence_quality": "NONE",
                    "correctness": "MISALIGNED",
                    "traceability": "MISSING",
                },
                "evidence": [],
                "gaps": ["Low evidence confidence"],
                "recommendations": [],
            }
        ]

        report = ReportAgent(
            aggregator=Aggregator(),
            risk_agent=RiskAgent(),
            remediation_agent=RemediationAgent(),
            traceability_agent=TraceabilityAgent(),
        ).build(
            results=results,
            clauses=[{"clause_id": "4.8", "title": "Safety Validation"}],
            agent_trace=[{"agent": "audit_agent", "status": "completed"}],
        )

        self.assertIn("risk", report)
        self.assertIn("remediation", report)
        self.assertIn("traceability", report)
        self.assertIn("agent_trace", report)
        self.assertEqual(report["agent_trace"][-1]["agent"], "report_agent")


if __name__ == "__main__":
    unittest.main()
