class Aggregator:
    def aggregate(self, results):
        total = len(results)

        compliant = sum(1 for r in results if r["status"] == "COMPLIANT")
        partial = sum(1 for r in results if r["status"] == "PARTIAL")
        non_compliant = sum(1 for r in results if r["status"] == "NON_COMPLIANT")
        not_applicable = sum(1 for r in results if r["status"] == "NOT_APPLICABLE")

        score = compliant / total if total > 0 else 0

        return {
            "total_clauses": total,
            "compliant": compliant,
            "partial": partial,
            "non_compliant": non_compliant,
            "not_applicable": not_applicable,
            "overall_score": round(score, 2)
        }