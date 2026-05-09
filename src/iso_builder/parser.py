import os

from src.ingestion.extractor import extract_text


def extract_text_from_pdf(file_path: str) -> str:
    return extract_text(file_path)


def extract_iso_source_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ISO source file not found: {file_path}")

    return extract_text(file_path)
