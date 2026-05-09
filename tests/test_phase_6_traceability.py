import unittest

from src.agents.traceability_agent import TraceabilityAgent


class TraceabilityAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = TraceabilityAgent()

    def test_builds_safety_goal_to_tsr_mapping(self):
        result = self.agent.analyze(
            results=[
                self._result("3.7", "COMPLIANT"),
                self._result("4.6", "PARTIAL"),
                self._result("4.8", "NON_COMPLIANT"),
            ],
            clauses=[
                {"clause_id": "3.7", "title": "Functional Safety Concept"},
                {"clause_id": "4.6", "title": "Technical Safety Concept"},
                {"clause_id": "4.8", "title": "Safety Validation"},
            ],
        )

        mappings = result["safety_goal_to_tsr"]["mappings"]

        self.assertEqual(len(mappings), 2)
        self.assertEqual(mappings[0]["source_clause"], "3.7")
        self.assertEqual(mappings[0]["status"], "TARGET_INCOMPLETE")

    def test_dependency_validation_flags_incomplete_upstream_clause(self):
        result = self.agent.analyze(
            results=[
                self._result("3.7", "NON_COMPLIANT"),
                self._result("4.6", "PARTIAL"),
            ],
            clauses=[
                {"clause_id": "3.7", "title": "Functional Safety Concept"},
                {"clause_id": "4.6", "title": "Technical Safety Concept"},
            ],
        )

        validation = result["dependency_validation"]

        self.assertFalse(validation["valid"])
        self.assertEqual(validation["issue_count"], 1)
        self.assertEqual(validation["issues"][0]["dependency"], "3.7")

    def test_coverage_analysis_counts_expected_links(self):
        result = self.agent.analyze(
            results=[
                self._result("3.5", "COMPLIANT"),
                self._result("4.6", "PARTIAL"),
            ],
            clauses=[
                {"clause_id": "3.5", "title": "Item Definition"},
                {"clause_id": "4.6", "title": "Technical Safety Concept"},
            ],
        )

        coverage = result["coverage_analysis"]

        self.assertEqual(coverage["expected_links"], 4)
        self.assertEqual(coverage["covered_links"], 2)
        self.assertEqual(coverage["coverage_ratio"], 0.5)

    def test_traceability_graph_contains_dependency_edges(self):
        result = self.agent.analyze(
            results=[
                self._result("3.7", "COMPLIANT"),
                self._result("4.6", "COMPLIANT"),
            ],
            clauses=[
                {"clause_id": "3.7", "title": "Functional Safety Concept"},
                {"clause_id": "4.6", "title": "Technical Safety Concept"},
            ],
        )

        edge_types = {
            edge["type"]
            for edge in result["traceability_graph"]["edges"]
        }

        self.assertIn("feeds", edge_types)
        self.assertIn("expects_trace_to", edge_types)

    def _result(self, clause_id, status):
        return {
            "clause_id": clause_id,
            "status": status,
            "confidence": 1.0 if status == "COMPLIANT" else 0.4,
            "evidence_confidence": 0.8 if status == "COMPLIANT" else 0.4,
            "evaluation": {
                "presence": "YES" if status != "NON_COMPLIANT" else "NO",
                "coverage": "FULL" if status == "COMPLIANT" else "PARTIAL",
                "evidence_quality": "EXPLICIT" if status == "COMPLIANT" else "IMPLICIT",
                "correctness": "ALIGNED" if status != "NON_COMPLIANT" else "MISALIGNED",
                "traceability": "CLEAR" if status == "COMPLIANT" else "PARTIAL",
            },
            "evidence": [],
            "gaps": [],
            "recommendations": [],
        }


if __name__ == "__main__":
    unittest.main()
