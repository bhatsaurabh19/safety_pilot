from typing import List, Dict, Any
from collections import Counter


class Aggregator:

    STATUS_WEIGHTS = {
        "COMPLIANT": 1.0,
        "PARTIAL": 0.5,
        "NON_COMPLIANT": 0.0,
        "NOT_APPLICABLE": None
    }

    def aggregate(self, results: List[Dict[str, Any]]):

        if not results:
            raise ValueError("No evaluation results provided")

        status_counts = Counter(
            r["status"]
            for r in results
        )

        compliant = status_counts.get("COMPLIANT", 0)
        partial = status_counts.get("PARTIAL", 0)
        non_compliant = status_counts.get("NON_COMPLIANT", 0)
        not_applicable = status_counts.get("NOT_APPLICABLE", 0)

        # -----------------------------------------
        # Weighted scoring
        # -----------------------------------------
        scored_results = [
            r for r in results
            if r["status"] != "NOT_APPLICABLE"
        ]

        total_scored = len(scored_results)

        if total_scored == 0:
            overall_score = 0.0

        else:
            total_weight = sum(
                self.STATUS_WEIGHTS[r["status"]]
                for r in scored_results
            )

            overall_score = round(
                total_weight / total_scored,
                4
            )

        # -----------------------------------------
        # Extract top gaps
        # -----------------------------------------
        all_gaps = []

        for result in results:
            all_gaps.extend(result.get("gaps", []))

        gap_counts = Counter(all_gaps)

        top_gaps = [
            {
                "gap": gap,
                "count": count
            }
            for gap, count in gap_counts.most_common(10)
        ]

        # -----------------------------------------
        # Extract recommendations
        # -----------------------------------------
        all_recommendations = []

        for result in results:
            all_recommendations.extend(
                result.get("recommendations", [])
            )

        recommendation_counts = Counter(all_recommendations)

        top_recommendations = [
            {
                "recommendation": rec,
                "count": count
            }
            for rec, count in recommendation_counts.most_common(10)
        ]

        # -----------------------------------------
        # Determine overall status
        # -----------------------------------------
        if non_compliant > 0:
            overall_status = "NON_COMPLIANT"

        elif partial > 0:
            overall_status = "PARTIAL"

        else:
            overall_status = "COMPLIANT"

        # -----------------------------------------
        # Final report
        # -----------------------------------------
        return {
            "summary": {
                "overall_status": overall_status,
                "overall_score": overall_score,
                "total_clauses": len(results),
                "compliant": compliant,
                "partial": partial,
                "non_compliant": non_compliant,
                "not_applicable": not_applicable
            },
            "top_gaps": top_gaps,
            "top_recommendations": top_recommendations,
            "clause_results": results
        }