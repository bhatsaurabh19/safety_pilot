import unittest

from src.remediation.remediator import RemediationAgent


class RemediationAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = RemediationAgent()

    def test_generates_plan_for_non_compliant_clause(self):
        report = self.agent.generate(
            results=[
                {
                    "clause_id": "4.8",
                    "status": "NON_COMPLIANT",
                    "confidence": 0.2,
                    "evidence_confidence": 0.3,
                    "evidence": [],
                    "gaps": ["Low evidence confidence"],
                    "recommendations": ["Provide validation evidence"],
                }
            ],
            clauses=[
                {
                    "clause_id": "4.8",
                    "title": "Safety Validation",
                }
            ],
        )

        self.assertEqual(report["summary"]["total_plans"], 1)
        plan = report["plans"][0]
        self.assertEqual(plan["priority"], "HIGH")
        self.assertIn("Safety validation plan", plan["missing_artifacts"])
        self.assertIn("Technical safety requirement", plan["traceability_structure"])
        self.assertIn("Provide validation evidence", plan["remediation_steps"])

    def test_skips_compliant_clauses(self):
        report = self.agent.generate(
            results=[
                {
                    "clause_id": "3.6",
                    "status": "COMPLIANT",
                    "confidence": 1.0,
                    "evidence_confidence": 0.8,
                    "evidence": ["HARA evidence"],
                    "gaps": [],
                    "recommendations": [],
                }
            ],
            clauses=[
                {
                    "clause_id": "3.6",
                    "title": "HARA",
                }
            ],
        )

        self.assertEqual(report["summary"]["total_plans"], 0)
        self.assertEqual(report["plans"], [])

    def test_prioritizes_non_compliant_before_partial(self):
        report = self.agent.generate(
            results=[
                {
                    "clause_id": "4.7",
                    "status": "PARTIAL",
                    "confidence": 0.45,
                    "evidence_confidence": 0.4,
                    "evidence": [],
                    "gaps": [],
                    "recommendations": [],
                },
                {
                    "clause_id": "3.7",
                    "status": "NON_COMPLIANT",
                    "confidence": 0.2,
                    "evidence_confidence": 0.3,
                    "evidence": [],
                    "gaps": [],
                    "recommendations": [],
                },
            ],
            clauses=[
                {"clause_id": "4.7", "title": "System Integration and Testing"},
                {"clause_id": "3.7", "title": "Functional Safety Concept"},
            ],
        )

        self.assertEqual(report["plans"][0]["clause_id"], "3.7")
        self.assertEqual(report["plans"][0]["priority"], "HIGH")
        self.assertEqual(report["plans"][1]["priority"], "MEDIUM")


if __name__ == "__main__":
    unittest.main()
