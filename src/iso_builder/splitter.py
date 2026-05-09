import re
from typing import Dict, List

from src.iso_builder.schema import attach_children, make_clause


HEADING_PATTERN = re.compile(
    r"^(?P<id>\d+(?:\.\d+)*)(?:\s+(?P<title>[A-Z][^\n]{2,160}))?$"
)


def split_into_clauses(
    text: str,
    part: str = "",
    source: str = "",
) -> List[Dict]:
    lines = _normalize_lines(text)
    heading_indexes = []

    for index, line in enumerate(lines):
        match = HEADING_PATTERN.match(line)
        if match:
            heading_indexes.append((index, match.group("id"), match.group("title") or ""))

    clauses = []

    for position, (start_index, clause_id, title) in enumerate(heading_indexes):
        end_index = (
            heading_indexes[position + 1][0]
            if position + 1 < len(heading_indexes)
            else len(lines)
        )
        body_lines = lines[start_index + 1:end_index]
        inferred_title, body_text = _infer_title(title, body_lines)

        if not body_text.strip():
            continue

        clauses.append(
            make_clause(
                clause_id=clause_id,
                title=inferred_title,
                text=body_text,
                part=part,
                source=source,
            )
        )

    return attach_children(clauses)


def _normalize_lines(text: str) -> List[str]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)

    return [
        line.strip()
        for line in normalized.split("\n")
        if line.strip()
    ]


def _infer_title(title: str, body_lines: List[str]) -> tuple[str, str]:
    if title:
        return title.strip(), "\n".join(body_lines).strip()

    if body_lines and _looks_like_title(body_lines[0]):
        return body_lines[0].strip(), "\n".join(body_lines[1:]).strip()

    return "", "\n".join(body_lines).strip()


def _looks_like_title(line: str) -> bool:
    if len(line) > 120:
        return False

    lowered = line.lower()
    if " shall " in f" {lowered} ":
        return False

    return not line.endswith(".")
