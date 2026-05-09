from typing import Any, Dict, List


class TraceabilityAgent:
    DEPENDENCIES = {
        "3.6": ["3.5"],
        "3.7": ["3.5", "3.6"],
        "4.5": ["3.7"],
        "4.6": ["3.7", "4.5"],
        "4.7": ["4.6"],
        "4.8": ["3.7", "4.6", "4.7"],
    }

    TRACE_TARGETS = {
        "3.5": ["item_definition"],
        "3.6": ["hazardous_event", "asil", "safety_goal"],
        "3.7": ["safety_goal", "functional_safety_requirement"],
        "4.5": ["functional_safety_requirement", "technical_safety_requirement"],
        "4.6": ["technical_safety_requirement", "system_architecture", "safety_mechanism"],
        "4.7": ["technical_safety_requirement", "integration_test"],
        "4.8": ["safety_goal", "validation_test"],
    }

    def analyze(
        self,
        results: List[Dict[str, Any]],
        clauses: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        result_lookup = {
            result.get("clause_id"): result
            for result in results
        }
        clause_lookup = {
            clause.get("clause_id"): clause
            for clause in clauses
        }

        graph = self._build_graph(result_lookup, clause_lookup)
        coverage = self._coverage(result_lookup)
        dependency_validation = self._validate_dependencies(result_lookup)
        safety_goal_to_tsr = self._safety_goal_to_tsr_mapping(result_lookup)

        return {
            "safety_goal_to_tsr": safety_goal_to_tsr,
            "traceability_graph": graph,
            "coverage_analysis": coverage,
            "dependency_validation": dependency_validation,
        }

    def _build_graph(
        self,
        result_lookup: Dict[str, Dict[str, Any]],
        clause_lookup: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        nodes = []
        edges = []

        for clause_id, result in result_lookup.items():
            nodes.append({
                "id": f"clause:{clause_id}",
                "type": "clause",
                "label": clause_lookup.get(clause_id, {}).get("title", clause_id),
                "status": result.get("status", "NON_COMPLIANT"),
                "coverage": result.get("evaluation", {}).get("coverage", "NONE"),
            })

            for target in self.TRACE_TARGETS.get(clause_id, []):
                artifact_id = f"trace_target:{target}"
                nodes.append({
                    "id": artifact_id,
                    "type": "trace_target",
                    "label": target,
                })
                edges.append({
                    "source": f"clause:{clause_id}",
                    "target": artifact_id,
                    "type": "expects_trace_to",
                })

        for clause_id, dependencies in self.DEPENDENCIES.items():
            if clause_id not in result_lookup:
                continue

            for dependency in dependencies:
                if dependency in result_lookup:
                    edges.append({
                        "source": f"clause:{dependency}",
                        "target": f"clause:{clause_id}",
                        "type": "feeds",
                    })

        return {
            "nodes": self._dedupe_nodes(nodes),
            "edges": edges,
        }

    def _coverage(self, result_lookup: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        total_links = 0
        covered_links = 0
        by_clause = []

        for clause_id, targets in self.TRACE_TARGETS.items():
            if clause_id not in result_lookup:
                continue

            result = result_lookup[clause_id]
            clause_total = len(targets)
            clause_covered = self._covered_target_count(result, clause_total)
            total_links += clause_total
            covered_links += clause_covered

            by_clause.append({
                "clause_id": clause_id,
                "expected_links": clause_total,
                "covered_links": clause_covered,
                "coverage_ratio": self._ratio(clause_covered, clause_total),
                "status": result.get("status", "NON_COMPLIANT"),
            })

        return {
            "expected_links": total_links,
            "covered_links": covered_links,
            "coverage_ratio": self._ratio(covered_links, total_links),
            "by_clause": by_clause,
        }

    def _validate_dependencies(
        self,
        result_lookup: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        issues = []

        for clause_id, dependencies in self.DEPENDENCIES.items():
            if clause_id not in result_lookup:
                continue

            for dependency in dependencies:
                dependency_result = result_lookup.get(dependency)
                if dependency_result is None:
                    continue

                if dependency_result.get("status") != "COMPLIANT":
                    issues.append({
                        "clause_id": clause_id,
                        "dependency": dependency,
                        "issue": f"Dependency is {dependency_result.get('status')}",
                        "severity": self._severity_for_status(
                            dependency_result.get("status")
                        ),
                    })

        return {
            "valid": len(issues) == 0,
            "issue_count": len(issues),
            "issues": issues,
        }

    def _safety_goal_to_tsr_mapping(
        self,
        result_lookup: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        safety_goal_clause = result_lookup.get("3.7")
        tsr_clauses = [
            result_lookup[clause_id]
            for clause_id in ["4.5", "4.6", "4.7", "4.8"]
            if clause_id in result_lookup
        ]

        mappings = []

        if safety_goal_clause:
            for tsr_result in tsr_clauses:
                mappings.append({
                    "source_clause": "3.7",
                    "target_clause": tsr_result.get("clause_id"),
                    "status": self._mapping_status(safety_goal_clause, tsr_result),
                    "source_status": safety_goal_clause.get("status"),
                    "target_status": tsr_result.get("status"),
                })

        return {
            "mapping_count": len(mappings),
            "mappings": mappings,
        }

    def _mapping_status(
        self,
        safety_goal_result: Dict[str, Any],
        tsr_result: Dict[str, Any],
    ) -> str:
        if safety_goal_result.get("status") != "COMPLIANT":
            return "BLOCKED_BY_SAFETY_GOAL"

        if tsr_result.get("status") != "COMPLIANT":
            return "TARGET_INCOMPLETE"

        return "LINKED"

    def _covered_target_count(
        self,
        result: Dict[str, Any],
        total_targets: int,
    ) -> int:
        evaluation = result.get("evaluation", {})

        if result.get("status") == "COMPLIANT" and evaluation.get("traceability") == "CLEAR":
            return total_targets

        if result.get("status") == "PARTIAL" or evaluation.get("traceability") == "PARTIAL":
            return max(1, total_targets // 2)

        return 0

    def _severity_for_status(self, status: str) -> str:
        if status == "NON_COMPLIANT":
            return "HIGH"

        if status == "PARTIAL":
            return "MEDIUM"

        return "LOW"

    def _ratio(self, numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0

        return round(numerator / denominator, 4)

    def _dedupe_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        by_id = {}

        for node in nodes:
            by_id[node["id"]] = node

        return list(by_id.values())
