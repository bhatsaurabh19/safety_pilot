from typing import Any, Dict, List


def build_knowledge_graph(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    nodes = []
    edges = []

    for clause in clauses:
        clause_node_id = f"clause:{clause['clause_id']}"
        nodes.append({
            "id": clause_node_id,
            "type": "clause",
            "label": clause.get("title") or clause["clause_id"],
            "clause_id": clause["clause_id"],
        })

        parent_id = clause.get("parent_id")
        if parent_id:
            edges.append({
                "source": f"clause:{parent_id}",
                "target": clause_node_id,
                "type": "has_child",
            })

        for requirement in clause.get("requirements", []):
            requirement_node_id = f"requirement:{requirement['requirement_id']}"
            nodes.append({
                "id": requirement_node_id,
                "type": "requirement",
                "label": requirement["requirement_id"],
                "modal": requirement["modal"],
            })
            edges.append({
                "source": clause_node_id,
                "target": requirement_node_id,
                "type": "contains_requirement",
            })

            for evidence in requirement.get("expected_evidence", []):
                evidence_node_id = f"artifact:{_slug(evidence)}"
                nodes.append({
                    "id": evidence_node_id,
                    "type": "artifact",
                    "label": evidence,
                })
                edges.append({
                    "source": requirement_node_id,
                    "target": evidence_node_id,
                    "type": "expects_evidence",
                })

    return {
        "nodes": _dedupe_nodes(nodes),
        "edges": edges,
    }


def _slug(value: str) -> str:
    return (
        value.lower()
        .replace("/", " ")
        .replace("-", " ")
        .replace("_", " ")
        .strip()
        .replace(" ", "_")
    )


def _dedupe_nodes(nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id = {}

    for node in nodes:
        by_id[node["id"]] = node

    return list(by_id.values())
