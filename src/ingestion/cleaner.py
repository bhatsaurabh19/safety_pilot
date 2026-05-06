import re


def clean_text(text: str) -> str:

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces but preserve line structure
    text = re.sub(r"[ \t]+", " ", text)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove simple page markers
    text = re.sub(r"\bPage \d+\b", "", text)

    return text.strip()