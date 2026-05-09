from typing import Any, Dict, List


class AuditAgent:
    def __init__(self, evaluator):
        self.evaluator = evaluator

    def evaluate(self, clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = self.evaluator.evaluate(clauses)

        return {
            "agent": "audit_agent",
            "status": "completed",
            "clauses_evaluated": len(results),
            "results": results,
        }
