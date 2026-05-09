from typing import Any, Dict, List


class ReportAgent:
    def __init__(
        self,
        aggregator,
        risk_agent,
        remediation_agent,
        traceability_agent=None,
    ):
        self.aggregator = aggregator
        self.risk_agent = risk_agent
        self.remediation_agent = remediation_agent
        self.traceability_agent = traceability_agent

    def build(
        self,
        results: List[Dict[str, Any]],
        clauses: List[Dict[str, Any]],
        agent_trace: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        report = self.aggregator.aggregate(results)
        report["risk"] = self.risk_agent.assess(results)
        report["remediation"] = self.remediation_agent.generate(
            results=results,
            clauses=clauses,
        )

        if self.traceability_agent:
            report["traceability"] = self.traceability_agent.analyze(
                results=results,
                clauses=clauses,
            )

        trace_entries = []
        if self.traceability_agent:
            trace_entries.append({
                "agent": "traceability_agent",
                "status": "completed",
                "dependency_issues": report["traceability"][
                    "dependency_validation"
                ]["issue_count"],
            })

        report["agent_trace"] = agent_trace + [
            {
                "agent": "risk_agent",
                "status": "completed",
                "risks_found": report["risk"]["summary"]["total_risks"],
            },
            {
                "agent": "remediation_agent",
                "status": "completed",
                "plans_generated": report["remediation"]["summary"]["total_plans"],
            },
            *trace_entries,
            {
                "agent": "report_agent",
                "status": "completed",
                "sections": self._sections(report),
            },
        ]

        return report

    def _sections(self, report: Dict[str, Any]) -> List[str]:
        sections = [
            "summary",
            "top_gaps",
            "top_recommendations",
            "clause_results",
            "risk",
            "remediation",
        ]

        if "traceability" in report:
            sections.append("traceability")

        sections.append("agent_trace")

        return sections
