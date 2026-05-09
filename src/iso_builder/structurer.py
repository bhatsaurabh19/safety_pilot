import re
from typing import Any, Dict, List


STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "shall",
    "should",
    "the",
    "this",
    "that",
    "with",
}

EVIDENCE_HINTS = {
    "item": "Item definition and boundary evidence",
    "hazard": "Hazard log or HARA worksheet",
    "risk": "Risk assessment rationale",
    "safety goal": "Safety goal traceability matrix",
    "functional safety": "Functional safety concept",
    "technical safety": "Technical safety concept",
    "requirement": "Requirements traceability matrix",
    "architecture": "System architecture description",
    "integration": "Integration test evidence",
    "validation": "Safety validation report",
    "verification": "Verification report",
}


def structure_clause(clause: Dict[str, Any]) -> Dict[str, Any]:
    text = clause.get("text", "")
    requirements = extract_requirements(clause.get("clause_id", ""), text)

    structured = dict(clause)
    structured["requirements"] = requirements
    structured["keywords"] = extract_keywords(
        " ".join([
            clause.get("title", ""),
            text,
        ])
    )

    return structured


def extract_requirements(clause_id: str, text: str) -> List[Dict[str, Any]]:
    requirements = []
    sentences = _sentences(text)

    for sentence in sentences:
        modal = _requirement_modal(sentence)
        if not modal:
            continue

        requirement_index = len(requirements) + 1
        requirements.append({
            "requirement_id": f"{clause_id}-R{requirement_index:03d}",
            "clause_id": clause_id,
            "modal": modal,
            "text": sentence,
            "expected_evidence": infer_expected_evidence(sentence),
            "keywords": extract_keywords(sentence),
        })

    return requirements


def infer_expected_evidence(text: str) -> List[str]:
    lowered = text.lower()
    hints = [
        evidence
        for keyword, evidence in EVIDENCE_HINTS.items()
        if keyword in lowered
    ]

    if hints:
        return _dedupe(hints)

    return ["Objective work product evidence"]


def extract_keywords(text: str, limit: int = 12) -> List[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower())
    keywords = []

    for token in tokens:
        if token in STOPWORDS or len(token) < 3:
            continue
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= limit:
            break

    return keywords


def _sentences(text: str) -> List[str]:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if not collapsed:
        return []

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", collapsed)
        if sentence.strip()
    ]


def _requirement_modal(sentence: str) -> str | None:
    lowered = sentence.lower()

    if re.search(r"\bshall\b", lowered):
        return "shall"

    if re.search(r"\bshould\b", lowered):
        return "should"

    return None


def _dedupe(values: List[str]) -> List[str]:
    deduped = []

    for value in values:
        if value not in deduped:
            deduped.append(value)

    return deduped
