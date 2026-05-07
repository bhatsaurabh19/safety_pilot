import re
from typing import Any, Dict, List


class EvidenceAnalyzer:
    STOPWORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "or",
        "shall",
        "that",
        "the",
        "to",
        "under",
        "with",
    }

    def __init__(self, weak_threshold: float = 0.45):
        self.weak_threshold = weak_threshold

    def analyze(
        self,
        clause_title: str,
        clause_text: str,
        retrieval_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        chunks = retrieval_result.get("chunks", [])

        if not chunks:
            return {
                "evidence_confidence": 0.0,
                "weak_evidence": True,
                "reasons": ["No evidence retrieved"],
            }

        clause_terms = self._terms(f"{clause_title} {clause_text}")
        chunk_scores = []

        for chunk in chunks:
            text = chunk.get("text", "")
            overlap = self._overlap_ratio(clause_terms, self._terms(text))
            retrieval_score = float(chunk.get("score", 0.0))
            chunk_scores.append((retrieval_score * 0.7) + (overlap * 0.3))

        evidence_confidence = round(sum(chunk_scores) / len(chunk_scores), 4)
        reasons = []

        if retrieval_result.get("retrieval_confidence") == "LOW":
            reasons.append("Low retrieval confidence")

        if evidence_confidence < self.weak_threshold:
            reasons.append("Low evidence confidence")

        return {
            "evidence_confidence": evidence_confidence,
            "weak_evidence": bool(reasons),
            "reasons": reasons,
        }

    def rerank(
        self,
        clause_title: str,
        clause_text: str,
        retrieval_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        chunks = retrieval_result.get("chunks", [])
        clause_terms = self._terms(f"{clause_title} {clause_text}")

        ranked = []
        for chunk in chunks:
            overlap = self._overlap_ratio(clause_terms, self._terms(chunk.get("text", "")))
            combined_score = (float(chunk.get("score", 0.0)) * 0.7) + (overlap * 0.3)

            enriched = dict(chunk)
            enriched["rerank_score"] = round(combined_score, 4)
            ranked.append(enriched)

        reranked = sorted(
            ranked,
            key=lambda chunk: (chunk["rerank_score"], chunk.get("score", 0.0)),
            reverse=True,
        )

        updated = dict(retrieval_result)
        updated["chunks"] = reranked
        return updated

    def _terms(self, text: str) -> set[str]:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_]+", text.lower())
        return {token for token in tokens if token not in self.STOPWORDS and len(token) > 2}

    def _overlap_ratio(self, source_terms: set[str], target_terms: set[str]) -> float:
        if not source_terms or not target_terms:
            return 0.0

        return len(source_terms & target_terms) / len(source_terms)
