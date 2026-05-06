import argparse
import json
import os

from src.ingestion.extractor import extract_text
from src.ingestion.cleaner import clean_text
from src.ingestion.chunker import chunk_text

OUTPUT_PATH = "data/documents/input_chunks.json"


def ingest(input_path: str, chunk_size: int = 400, overlap: int = 50) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    print(f"📂 Reading: {input_path}")
    raw_text = extract_text(input_path)

    print("🧹 Cleaning text...")
    cleaned = clean_text(raw_text)

    print(f"✂️  Chunking (size={chunk_size}, overlap={overlap})...")
    chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)

    chunk_strings = [c["text"] for c in chunks]

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(chunk_strings, f, indent=2)

    print(f"✅ Saved {len(chunk_strings)} chunks → {OUTPUT_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a document into input_chunks.json")
    parser.add_argument("--input", required=True, help="Path to input PDF, DOCX, or TXT file")
    parser.add_argument("--chunk_size", type=int, default=400, help="Characters per chunk")
    parser.add_argument("--overlap", type=int, default=50, help="Overlap between chunks")
    args = parser.parse_args()

    ingest(args.input, args.chunk_size, args.overlap)