from typing import Dict, Any, List


class SchemaValidationError(Exception):
    pass


class SchemaValidator:
    REQUIRED_TOP_LEVEL_FIELDS = {
        "clause_id": str,
        "status": str,
        "confidence": (int, float),
        "evaluation": dict,
        "evidence": list,
        "gaps": list,
        "recommendations": list,
    }

    REQUIRED_EVALUATION_FIELDS = {
        "presence": str,
        "coverage": str,
        "evidence_quality": str,
        "correctness": str,
        "traceability": str,
    }

    VALID_STATUS = {
        "COMPLIANT",
        "PARTIAL",
        "NON_COMPLIANT",
        "NOT_APPLICABLE",
    }

    VALID_PRESENCE = {"YES", "NO"}
    VALID_COVERAGE = {"FULL", "PARTIAL", "NONE"}
    VALID_EVIDENCE_QUALITY = {"EXPLICIT", "IMPLICIT", "WEAK", "NONE"}
    VALID_CORRECTNESS = {"ALIGNED", "PARTIAL", "MISALIGNED"}
    VALID_TRACEABILITY = {"CLEAR", "PARTIAL", "MISSING"}

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strict validation:
        - No missing fields
        - No extra fields
        - Exact enum values
        - Type enforcement
        """

        self._validate_top_level(data)
        self._validate_status(data["status"])
        self._validate_confidence(data["confidence"])
        self._validate_evaluation(data["evaluation"])
        self._validate_string_list(data["evidence"], "evidence")
        self._validate_string_list(data["gaps"], "gaps")
        self._validate_string_list(data["recommendations"], "recommendations")

        return data  # validated, no modification

    # -----------------------------
    # Top-level validation
    # -----------------------------
    def _validate_top_level(self, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise SchemaValidationError("Output must be a JSON object")

        # Missing fields
        for field, expected_type in self.REQUIRED_TOP_LEVEL_FIELDS.items():
            if field not in data:
                raise SchemaValidationError(f"Missing field: {field}")

            if not isinstance(data[field], expected_type):
                raise SchemaValidationError(
                    f"Invalid type for '{field}', expected {expected_type}, got {type(data[field])}"
                )

        # Extra fields
        extra_fields = set(data.keys()) - set(self.REQUIRED_TOP_LEVEL_FIELDS.keys())
        if extra_fields:
            raise SchemaValidationError(f"Unexpected fields: {extra_fields}")

    # -----------------------------
    # Field validators
    # -----------------------------
    def _validate_status(self, status: str):
        if status not in self.VALID_STATUS:
            raise SchemaValidationError(f"Invalid status: {status}")

    def _validate_confidence(self, confidence: float):
        if not (0.0 <= confidence <= 1.0):
            raise SchemaValidationError("Confidence must be between 0.0 and 1.0")

    def _validate_evaluation(self, evaluation: Dict[str, Any]):
        if not isinstance(evaluation, dict):
            raise SchemaValidationError("Evaluation must be an object")

        # Missing fields
        for field, expected_type in self.REQUIRED_EVALUATION_FIELDS.items():
            if field not in evaluation:
                raise SchemaValidationError(f"Missing evaluation field: {field}")

            if not isinstance(evaluation[field], expected_type):
                raise SchemaValidationError(
                    f"Invalid type for evaluation.{field}"
                )

        # Extra fields
        extra_fields = set(evaluation.keys()) - set(self.REQUIRED_EVALUATION_FIELDS.keys())
        if extra_fields:
            raise SchemaValidationError(f"Unexpected evaluation fields: {extra_fields}")

        # Enum checks
        if evaluation["presence"] not in self.VALID_PRESENCE:
            raise SchemaValidationError("Invalid presence value")

        if evaluation["coverage"] not in self.VALID_COVERAGE:
            raise SchemaValidationError("Invalid coverage value")

        if evaluation["evidence_quality"] not in self.VALID_EVIDENCE_QUALITY:
            raise SchemaValidationError("Invalid evidence_quality value")

        if evaluation["correctness"] not in self.VALID_CORRECTNESS:
            raise SchemaValidationError("Invalid correctness value")

        if evaluation["traceability"] not in self.VALID_TRACEABILITY:
            raise SchemaValidationError("Invalid traceability value")

    def _validate_string_list(self, value: List[Any], field_name: str):
        if not isinstance(value, list):
            raise SchemaValidationError(f"{field_name} must be a list")

        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise SchemaValidationError(
                    f"{field_name}[{i}] must be a string"
                )