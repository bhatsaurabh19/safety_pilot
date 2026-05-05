from typing import List, Dict, Any

from src.evaluation.prompt_builder import PromptBuilder


class Evaluator:
    def __init__(self, retriever, llm, schema_validator):
        """
        retriever: must implement get_relevant_chunks(query: str) -> List[str]
        llm: must implement generate(prompt: str) -> str
        schema_validator: must implement validate(json_obj: dict) -> dict
        """
        self.retriever = retriever
        self.llm = llm
        self.schema_validator = schema_validator
        self.prompt_builder = PromptBuilder()
    
    def _normalize_output(self, data):
        """
        Fix common LLM inconsistencies before strict validation
        """

        def normalize_list(lst):
            if not isinstance(lst, list):
                return []

            normalized = []
            for item in lst:
                if isinstance(item, str):
                    normalized.append(item)

                elif isinstance(item, dict):
                    # extract any text-like field
                    for key in ["text", "value", "content"]:
                        if key in item and isinstance(item[key], str):
                            normalized.append(item[key])
                            break

                elif isinstance(item, list):
                    # flatten nested list
                    normalized.extend([str(x) for x in item])

                else:
                    normalized.append(str(item))

            return normalized

        data["evidence"] = normalize_list(data.get("evidence", []))
        data["gaps"] = normalize_list(data.get("gaps", []))
        data["recommendations"] = normalize_list(data.get("recommendations", []))

        return data

    def evaluate(self, clauses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Main evaluation loop

        Input:
            clauses = [
                {
                    "clause_id": "...",
                    "title": "...",
                    "text": "..."
                }
            ]

        Output:
            List of validated evaluation results (one per clause)
        """

        results = []

        for clause in clauses:
            clause_id = clause.get("clause_id")
            clause_title = clause.get("title", "")
            clause_text = clause.get("text", "")

            print(f"\n🔍 Evaluating Clause: {clause_id}")

            # -----------------------------
            # Step 1: Retrieve evidence
            # -----------------------------
            query = f"{clause_title}. {clause_text}"
            retrieved_chunks = self.retriever.get_relevant_chunks(query)

            if not retrieved_chunks:
                print("⚠️ No evidence retrieved")

            # -----------------------------
            # Step 2: Build prompt
            # -----------------------------
            prompt = self.prompt_builder.build(
                clause_id=clause_id,
                clause_title=clause_title,
                clause_text=clause_text,
                retrieved_chunks=retrieved_chunks,
            )

            # -----------------------------
            # Step 3: LLM evaluation
            # -----------------------------
            response = self.llm.generate(prompt)

            # -----------------------------
            # Step 4: Parse JSON safely
            # -----------------------------
            parsed = self._safe_parse_json(response, clause_id)

            # -----------------------------
            # Step 4: # 🔧 NORMALIZE LLM OUTPUT
            # -----------------------------
            parsed = self._normalize_output(parsed)

            # -----------------------------
            # Step 5: Validate schema
            # -----------------------------
            validated = self.schema_validator.validate(parsed)

            results.append(validated)

        return results

    # -----------------------------------------
    # INTERNAL: Safe JSON parsing
    # -----------------------------------------
    def _safe_parse_json(self, response: str, clause_id: str) -> Dict[str, Any]:
        import json

        try:
            return json.loads(response)
        except Exception:
            print(f"❌ JSON parsing failed for clause {clause_id}")

            # Hard fallback (strict mode)
            return {
                "clause_id": clause_id,
                "status": "NON_COMPLIANT",
                "confidence": 0.0,
                "evaluation": {
                    "presence": "NO",
                    "coverage": "NONE",
                    "evidence_quality": "NONE",
                    "correctness": "MISALIGNED",
                    "traceability": "MISSING",
                },
                "evidence": [],
                "gaps": ["LLM response was invalid JSON"],
                "recommendations": ["Fix LLM output formatting"],
            }