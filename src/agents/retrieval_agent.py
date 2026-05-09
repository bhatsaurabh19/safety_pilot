from typing import Any, Dict, List

from src.evaluation.evidence import EvidenceAnalyzer


class RetrievalAgent:
    def __init__(
        self,
        retriever,
        max_evidence_retries=1,
        weak_evidence_threshold=0.45,
    ):
        self.retriever = retriever
        self.max_evidence_retries = max_evidence_retries
        self.evidence_analyzer = EvidenceAnalyzer(
            weak_threshold=weak_evidence_threshold
        )

    def retrieve(
        self,
        clause_title: str,
        clause_text: str,
    ) -> Dict[str, Any]:
        best_result = None
        best_analysis = None
        attempts = []

        queries = self._build_queries(clause_title, clause_text)
        max_attempts = min(len(queries), self.max_evidence_retries + 1)

        for query in queries[:max_attempts]:
            retrieval_result = self.retriever.get_relevant_chunks(query)
            retrieval_result = self.evidence_analyzer.rerank(
                clause_title=clause_title,
                clause_text=clause_text,
                retrieval_result=retrieval_result,
            )
            analysis = self.evidence_analyzer.analyze(
                clause_title=clause_title,
                clause_text=clause_text,
                retrieval_result=retrieval_result,
            )

            attempts.append({
                "query": query,
                "avg_score": retrieval_result.get("avg_score", 0.0),
                "retrieval_confidence": retrieval_result.get(
                    "retrieval_confidence",
                    "LOW",
                ),
                "evidence_confidence": analysis["evidence_confidence"],
                "weak_evidence": analysis["weak_evidence"],
                "reasons": analysis["reasons"],
            })

            if (
                best_analysis is None
                or analysis["evidence_confidence"]
                > best_analysis["evidence_confidence"]
            ):
                best_result = retrieval_result
                best_analysis = analysis

            if not analysis["weak_evidence"]:
                break

        if best_result is None:
            best_result = self._empty_result()
            best_analysis = self.evidence_analyzer.analyze(
                clause_title=clause_title,
                clause_text=clause_text,
                retrieval_result=best_result,
            )

        best_result["evidence_analysis"] = best_analysis
        best_result["retrieval_attempts"] = attempts

        return best_result

    def _build_queries(
        self,
        clause_title: str,
        clause_text: str,
    ) -> List[str]:
        return [
            f"{clause_title}. {clause_text}",
            clause_text,
            clause_title,
        ]

    def _empty_result(self) -> Dict[str, Any]:
        return {
            "chunks": [],
            "avg_score": 0.0,
            "retrieval_confidence": "LOW",
        }
