from typing import Any, Dict, List


def make_clause(
    clause_id: str,
    title: str,
    text: str,
    part: str = "",
    source: str = "",
) -> Dict[str, Any]:
    parent_id = ".".join(clause_id.split(".")[:-1]) or None

    return {
        "clause_id": clause_id,
        "title": title.strip(),
        "text": text.strip(),
        "part": part,
        "source": source,
        "level": len(clause_id.split(".")),
        "parent_id": parent_id,
        "children": [],
        "requirements": [],
        "keywords": [],
    }


def attach_children(clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_id = {clause["clause_id"]: clause for clause in clauses}

    for clause in clauses:
        clause["children"] = []

    for clause in clauses:
        parent_id = clause.get("parent_id")
        if parent_id in by_id:
            by_id[parent_id]["children"].append(clause["clause_id"])

    return clauses
