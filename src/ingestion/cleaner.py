import re


def clean_text(text: str) -> str:
    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Fix broken lines
    text = text.replace("\n", " ")

    # Remove page numbers (simple heuristic)
    text = re.sub(r"\bPage \d+\b", "", text)

    # Remove repeated headers (basic)
    text = re.sub(r"ISO\s*26262.*?\d{4}", "", text)

    return text.strip()