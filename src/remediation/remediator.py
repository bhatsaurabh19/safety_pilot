from typing import Any, Dict, List


class RemediationAgent:
    CLAUSE_ARTIFACTS = {
        "3.5": [
            "Item definition",
            "System boundary diagram",
            "Interface and dependency list",
            "Operational design domain description",
        ],
        "3.6": [
            "HARA worksheet",
            "Hazard log",
            "Severity/exposure/controllability rationale",
            "ASIL classification matrix",
        ],
        "3.7": [
            "Functional safety concept",
            "Functional safety requirements",
            "Safety goal traceability matrix",
            "Safe state definition",
        ],
        "4.5": [
            "System development plan",
            "System architecture description",
            "TSR traceability matrix",
            "Integration strategy",
        ],
        "4.6": [
            "Technical safety concept",
            "Technical safety requirements",
            "Safety mechanism specification",
            "Fault detection and safe state strategy",
        ],
        "4.7": [
            "System integration test plan",
            "Hardware/software integration evidence",
            "Fault injection test results",
            "Safety mechanism verification report",
        ],
        "4.8": [
            "Safety validation plan",
            "Vehicle-level validation report",
            "Target environment validation evidence",
            "Safety goal validation matrix",
        ],
    }

    TRACEABILITY_BY_PART = {
        "3": [
            "Item definition",
            "Hazardous event",
            "Safety goal",
            "ASIL",
            "Functional safety requirement",
        ],
        "4": [
            "Functional safety requirement",
            "Technical safety requirement",
            "System architecture element",
            "Safety mechanism",
            "Integration or validation test",
        ],
    }

    def generate(
        self,
        results: List[Dict[str, Any]],
        clauses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        clause_lookup = {
            clause.get("clause_id"): clause
            for clause in clauses
        }

        plans = [
            self._build_plan(result, clause_lookup.get(result.get("clause_id"), {}))
            for result in results
            if result.get("status") in {"PARTIAL", "NON_COMPLIANT"}
        ]

        plans = sorted(
            plans,
            key=lambda plan: (
                self._priority_rank(plan["priority"]),
                -plan["evidence_confidence"],
                plan["clause_id"],
            ),
        )

        return {
            "summary": {
                "total_plans": len(plans),
                "high_priority": sum(1 for plan in plans if plan["priority"] == "HIGH"),
                "medium_priority": sum(1 for plan in plans if plan["priority"] == "MEDIUM"),
                "low_priority": sum(1 for plan in plans if plan["priority"] == "LOW"),
            },
            "plans": plans,
        }

    def _build_plan(
        self,
        result: Dict[str, Any],
        clause: Dict[str, Any],
    ) -> Dict[str, Any]:
        clause_id = result.get("clause_id", "")
        status = result.get("status", "NON_COMPLIANT")
        confidence = float(result.get("confidence", 0.0))
        evidence_confidence = float(result.get("evidence_confidence", 0.0))
        gaps = result.get("gaps", [])
        recommendations = result.get("recommendations", [])
        priority = self._priority(status, confidence, evidence_confidence)

        return {
            "clause_id": clause_id,
            "title": clause.get("title", ""),
            "status": status,
            "priority": priority,
            "confidence": round(confidence, 4),
            "evidence_confidence": round(evidence_confidence, 4),
            "gaps": gaps,
            "missing_artifacts": self._missing_artifacts(clause_id, result),
            "remediation_steps": self._remediation_steps(
                clause_id=clause_id,
                title=clause.get("title", ""),
                gaps=gaps,
                recommendations=recommendations,
            ),
            "traceability_structure": self._traceability_structure(clause_id),
        }

    def _priority(
        self,
        status: str,
        confidence: float,
        evidence_confidence: float,
    ) -> str:
        if status == "NON_COMPLIANT":
            return "HIGH"

        if evidence_confidence < 0.45 or confidence < 0.5:
            return "MEDIUM"

        return "LOW"

    def _missing_artifacts(
        self,
        clause_id: str,
        result: Dict[str, Any],
    ) -> List[str]:
        artifacts = self.CLAUSE_ARTIFACTS.get(clause_id, ["Compliance evidence package"])

        if result.get("evidence"):
            return artifacts[:2]

        return artifacts

    def _remediation_steps(
        self,
        clause_id: str,
        title: str,
        gaps: List[str],
        recommendations: List[str],
    ) -> List[str]:
        steps = []

        if recommendations:
            steps.extend(recommendations)

        if gaps:
            steps.append("Address each recorded gap with explicit, reviewable evidence.")

        steps.extend([
            f"Create or update the {title or clause_id} work product.",
            "Add clause references and stable artifact identifiers.",
            "Link each requirement to objective evidence and verification status.",
            "Re-run the compliance pipeline and review the clause audit log.",
        ])

        return self._dedupe(steps)

    def _traceability_structure(self, clause_id: str) -> List[str]:
        part = clause_id.split(".", 1)[0]
        return self.TRACEABILITY_BY_PART.get(part, [
            "Clause",
            "Requirement",
            "Evidence",
            "Verification result",
        ])

    def _priority_rank(self, priority: str) -> int:
        return {
            "HIGH": 0,
            "MEDIUM": 1,
            "LOW": 2,
        }.get(priority, 3)

    def _dedupe(self, values: List[str]) -> List[str]:
        seen = set()
        deduped = []

        for value in values:
            if value not in seen:
                seen.add(value)
                deduped.append(value)

        return deduped
