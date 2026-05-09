from typing import Any, Dict, List


class RiskAgent:
    def assess(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        risk_items = [
            self._risk_item(result)
            for result in results
            if result.get("status") != "COMPLIANT"
        ]

        risk_items = sorted(
            risk_items,
            key=lambda item: (
                self._risk_rank(item["risk_level"]),
                item["evidence_confidence"],
                item["clause_id"],
            ),
        )

        return {
            "summary": {
                "total_risks": len(risk_items),
                "high": sum(1 for item in risk_items if item["risk_level"] == "HIGH"),
                "medium": sum(1 for item in risk_items if item["risk_level"] == "MEDIUM"),
                "low": sum(1 for item in risk_items if item["risk_level"] == "LOW"),
            },
            "risk_items": risk_items,
        }

    def _risk_item(self, result: Dict[str, Any]) -> Dict[str, Any]:
        status = result.get("status", "NON_COMPLIANT")
        confidence = float(result.get("confidence", 0.0))
        evidence_confidence = float(result.get("evidence_confidence", 0.0))

        return {
            "clause_id": result.get("clause_id", ""),
            "status": status,
            "risk_level": self._risk_level(status, confidence, evidence_confidence),
            "confidence": round(confidence, 4),
            "evidence_confidence": round(evidence_confidence, 4),
            "drivers": self._drivers(result),
        }

    def _risk_level(
        self,
        status: str,
        confidence: float,
        evidence_confidence: float,
    ) -> str:
        if status == "NON_COMPLIANT":
            return "HIGH"

        if status == "PARTIAL" or confidence < 0.5 or evidence_confidence < 0.45:
            return "MEDIUM"

        return "LOW"

    def _drivers(self, result: Dict[str, Any]) -> List[str]:
        drivers = list(result.get("gaps", []))

        if float(result.get("evidence_confidence", 0.0)) < 0.45:
            drivers.append("Evidence confidence below audit threshold")

        if not drivers:
            drivers.append("Clause is not fully compliant")

        return self._dedupe(drivers)

    def _risk_rank(self, risk_level: str) -> int:
        return {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }.get(risk_level, 3)

    def _dedupe(self, values: List[str]) -> List[str]:
        seen = set()
        deduped = []

        for value in values:
            if value not in seen:
                seen.add(value)
                deduped.append(value)

        return deduped
