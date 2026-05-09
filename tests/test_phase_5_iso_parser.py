import unittest

from src.iso_builder.knowledge_graph import build_knowledge_graph
from src.iso_builder.splitter import split_into_clauses
from src.iso_builder.structurer import structure_clause


SAMPLE_ISO_LIKE_TEXT = """
4 Product development at the system level
This section introduces system level development.

4.6 Technical safety concept
The technical safety concept shall define technical safety requirements.
The concept should describe safety mechanisms.

4.6.1 General
The system architecture shall support fault detection and safe state handling.

4.7 System integration and testing
Integration testing shall verify implemented safety mechanisms.
"""


class IsoParserTests(unittest.TestCase):
    def test_splitter_extracts_clause_hierarchy(self):
        clauses = split_into_clauses(
            SAMPLE_ISO_LIKE_TEXT,
            part="ISO 26262-4",
            source="synthetic",
        )

        by_id = {clause["clause_id"]: clause for clause in clauses}

        self.assertIn("4.6", by_id)
        self.assertIn("4.6.1", by_id)
        self.assertEqual(by_id["4.6.1"]["parent_id"], "4.6")
        self.assertEqual(by_id["4.6"]["children"], ["4.6.1"])
        self.assertEqual(by_id["4.6"]["title"], "Technical safety concept")

    def test_structurer_extracts_requirements(self):
        clause = {
            clause["clause_id"]: clause
            for clause in split_into_clauses(SAMPLE_ISO_LIKE_TEXT)
        }["4.6"]
        structured = structure_clause(clause)

        self.assertEqual(structured["requirements"][0]["modal"], "shall")
        self.assertIn(
            "Technical safety concept",
            structured["requirements"][0]["expected_evidence"],
        )
        self.assertIn("technical", structured["keywords"])

    def test_knowledge_graph_links_clauses_requirements_and_artifacts(self):
        clauses = [
            structure_clause(clause)
            for clause in split_into_clauses(SAMPLE_ISO_LIKE_TEXT)
        ]
        graph = build_knowledge_graph(clauses)

        edge_types = {edge["type"] for edge in graph["edges"]}
        node_types = {node["type"] for node in graph["nodes"]}

        self.assertIn("clause", node_types)
        self.assertIn("requirement", node_types)
        self.assertIn("artifact", node_types)
        self.assertIn("has_child", edge_types)
        self.assertIn("contains_requirement", edge_types)
        self.assertIn("expects_evidence", edge_types)


if __name__ == "__main__":
    unittest.main()
