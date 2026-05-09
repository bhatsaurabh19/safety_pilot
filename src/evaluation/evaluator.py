import json
import time
from typing import List, Dict, Any

from src.agents.retrieval_agent import RetrievalAgent
from src.evaluation.prompt_builder import PromptBuilder


class Evaluator:
    def __init__(
        self,
        retriever,
        llm,
        schema_validator,
        max_evidence_retries=1,
        weak_evidence_threshold=0.45,
        retrieval_agent=None,
    ):
        self.retriever = retriever
        self.llm = llm
        self.schema_validator = schema_validator
        self.prompt_builder = PromptBuilder()
        self.retrieval_agent = retrieval_agent or RetrievalAgent(
            retriever=retriever,
            max_evidence_retries=max_evidence_retries,
            weak_evidence_threshold=weak_evidence_threshold,
        )

    # -------------------------------------------------
    # Normalize inconsistent LLM outputs
    # -------------------------------------------------
    def _normalize_output(self, data):

        def normalize_list(lst):
            if not isinstance(lst, list):
                return []

            normalized = []

            for item in lst:
                if isinstance(item, str):
                    normalized.append(item)

                elif isinstance(item, dict):
                    for key in ["text", "value", "content"]:
                        if key in item and isinstance(item[key], str):
                            normalized.append(item[key])
                            break

                elif isinstance(item, list):
                    normalized.extend([str(x) for x in item])

                else:
                    normalized.append(str(item))

            return normalized

        evaluation_defaults = {
            "presence": "NO",
            "coverage": "NONE",
            "evidence_quality": "NONE",
            "correctness": "MISALIGNED",
            "traceability": "MISSING",
        }

        evaluation = data.get("evaluation", {})

        if not isinstance(evaluation, dict):
            evaluation = {}

        for field, fallback in evaluation_defaults.items():
            raw = evaluation.get(field, "")

            if not isinstance(raw, str) or raw.strip() == "":
                evaluation[field] = fallback
            else:
                evaluation[field] = raw.strip().upper()

        data["evaluation"] = evaluation

        data["evidence"] = normalize_list(data.get("evidence", []))
        data["gaps"] = normalize_list(data.get("gaps", []))
        data["recommendations"] = normalize_list(
            data.get("recommendations", [])
        )

        return data

    # -------------------------------------------------
    # Safe JSON parsing
    # -------------------------------------------------
    def _safe_parse_json(self, response: str, clause_id: str):

        try:
            return json.loads(response)

        except Exception:
            return {
                "clause_id": clause_id,
                "status": "NON_COMPLIANT",
                "confidence": 0.0,
                "evidence_confidence": 0.0,
                "evaluation": {
                    "presence": "NO",
                    "coverage": "NONE",
                    "evidence_quality": "NONE",
                    "correctness": "MISALIGNED",
                    "traceability": "MISSING"
                },
                "evidence": [],
                "gaps": [
                    "LLM returned invalid JSON"
                ],
                "recommendations": [
                    "Review prompt and model behavior"
                ]
            }

    def _retrieve_evidence(
        self,
        clause_title: str,
        clause_text: str,
    ) -> Dict[str, Any]:
        return self.retrieval_agent.retrieve(
            clause_title=clause_title,
            clause_text=clause_text,
        )

    def _apply_evidence_constraints(
        self,
        parsed: Dict[str, Any],
        retrieval_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        analysis = retrieval_result.get("evidence_analysis", {})
        evidence_confidence = float(analysis.get("evidence_confidence", 0.0))
        parsed["evidence_confidence"] = evidence_confidence

        if retrieval_result.get("retrieval_confidence") == "LOW":
            parsed["confidence"] = min(parsed["confidence"], 0.4)

        if analysis.get("weak_evidence"):
            parsed["confidence"] = min(parsed["confidence"], evidence_confidence)

            if parsed.get("status") == "COMPLIANT":
                parsed["status"] = "PARTIAL"

            reasons = analysis.get("reasons", [])
            parsed["gaps"].extend(
                reason for reason in reasons if reason not in parsed["gaps"]
            )

        evaluation = parsed.get("evaluation", {})
        missing_or_misaligned = (
            evaluation.get("presence") == "NO"
            or evaluation.get("coverage") == "NONE"
            or evaluation.get("evidence_quality") == "NONE"
            or evaluation.get("correctness") == "MISALIGNED"
            or evaluation.get("traceability") == "MISSING"
        )

        if missing_or_misaligned and parsed.get("status") in {
            "COMPLIANT",
            "PARTIAL",
        }:
            parsed["status"] = "NON_COMPLIANT"
            parsed["confidence"] = min(parsed["confidence"], 0.2)
            gap = "Status downgraded because evaluation fields show missing or misaligned evidence"
            if gap not in parsed["gaps"]:
                parsed["gaps"].append(gap)

        if parsed.get("status") == "COMPLIANT" and not parsed.get("evidence"):
            parsed["status"] = "NON_COMPLIANT"
            parsed["confidence"] = min(parsed["confidence"], 0.2)
            gap = "Status downgraded because no supporting evidence was returned"
            if gap not in parsed["gaps"]:
                parsed["gaps"].append(gap)

        return parsed

    # -------------------------------------------------
    # Audit logging
    # -------------------------------------------------
    def _log_clause_run(
        self,
        clause_id,
        prompt,
        retrieval_result,
        raw_response,
        validated_result
    ):
        import os
        import json

        os.makedirs("logs", exist_ok=True)

        log_data = {
            "clause_id": clause_id,
            "retrieval": retrieval_result,
            "prompt": prompt,
            "raw_response": raw_response,
            "validated_result": validated_result
        }

        with open(
            f"logs/{clause_id.replace('.', '_')}.json",
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(log_data, f, indent=2)

    # -------------------------------------------------
    # Main evaluation loop
    # -------------------------------------------------
    def evaluate(self, clauses: List[Dict[str, Any]]):

        results = []

        for clause in clauses:

            clause_id = clause.get("clause_id")
            clause_title = clause.get("title", "")
            clause_text = clause.get("text", "")

            print(f"\nEvaluating Clause: {clause_id}")

            try:
                # -----------------------------------------
                # Step 1: Retrieval
                # -----------------------------------------
                retrieval_result = self._retrieve_evidence(
                    clause_title=clause_title,
                    clause_text=clause_text,
                )

                retrieved_chunks = retrieval_result["chunks"]

                if not retrieved_chunks:
                    print("No evidence retrieved")

                # Convert chunks to a text block.
                evidence_texts = [
                    chunk["text"]
                    for chunk in retrieved_chunks
                ]

                # -----------------------------------------
                # Step 2: Build prompt
                # -----------------------------------------
                prompt = self.prompt_builder.build(
                    clause_id=clause_id,
                    clause_title=clause_title,
                    clause_text=clause_text,
                    retrieved_chunks=evidence_texts
                )

                # -----------------------------------------
                # Step 3: LLM evaluation
                # -----------------------------------------
                start = time.time()

                response = self.llm.generate(prompt)

                elapsed = round(time.time() - start, 2)

                print(f"LLM response time: {elapsed}s")

                # -----------------------------------------
                # Step 4: Parse JSON
                # -----------------------------------------
                parsed = self._safe_parse_json(
                    response,
                    clause_id
                )

                # -----------------------------------------
                # Step 5: Normalize output
                # -----------------------------------------
                parsed = self._normalize_output(parsed)

                # -----------------------------------------
                # Step 6: Evidence-aware confidence adjustment
                # -----------------------------------------
                parsed = self._apply_evidence_constraints(
                    parsed=parsed,
                    retrieval_result=retrieval_result,
                )

                # -----------------------------------------
                # Step 7: Validate schema
                # -----------------------------------------
                validated = self.schema_validator.validate(parsed)

                # -----------------------------------------
                # Step 8: Audit logging
                # -----------------------------------------
                self._log_clause_run(
                    clause_id=clause_id,
                    prompt=prompt,
                    retrieval_result=retrieval_result,
                    raw_response=response,
                    validated_result=validated
                )

                results.append(validated)

            except Exception as e:

                print(f"Clause failed: {clause_id}")

                fallback = {
                    "clause_id": clause_id,
                    "status": "NON_COMPLIANT",
                    "confidence": 0.0,
                    "evidence_confidence": 0.0,
                    "evaluation": {
                        "presence": "NO",
                        "coverage": "NONE",
                        "evidence_quality": "NONE",
                        "correctness": "MISALIGNED",
                        "traceability": "MISSING"
                    },
                    "evidence": [],
                    "gaps": [
                        f"Evaluation failed: {str(e)}"
                    ],
                    "recommendations": [
                        "Review pipeline logs"
                    ]
                }

                results.append(fallback)

        return results
