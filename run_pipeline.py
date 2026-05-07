import argparse
import json
import os
from typing import List, Dict, Any

# -----------------------------
# Config
# -----------------------------
from src.config.loader import load_config

# -----------------------------
# Ingestion
# -----------------------------
from src.ingestion.extractor import extract_text
from src.ingestion.cleaner import clean_text
from src.ingestion.chunker import chunk_text

# -----------------------------
# Embeddings / LLM
# -----------------------------
from src.embeddings.ollama_embeddings import OllamaEmbeddingModel
from src.llm.ollama_llm import OllamaLLM

# -----------------------------
# Retrieval
# -----------------------------
from src.vectorstore.faiss_store import FAISSStore
from src.retrieval.retriever import Retriever

# -----------------------------
# Evaluation
# -----------------------------
from src.evaluation.evaluator import Evaluator
from src.evaluation.schema import SchemaValidator

# -----------------------------
# Aggregation
# -----------------------------
from src.aggregation.aggregator import Aggregator


# ---------------------------------------------------------
# Load ISO clauses
# ---------------------------------------------------------
def load_iso_clauses(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("clauses", [])

    if isinstance(data, list):
        return data

    raise ValueError(f"Invalid ISO JSON format: {path}")


# ---------------------------------------------------------
# Save debug chunks (optional)
# ---------------------------------------------------------
def save_debug_chunks(chunks, output_path="debug/chunks.json"):

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)


# ---------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------
def main():

    parser = argparse.ArgumentParser(
        description="ISO 26262 Compliance Pipeline"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Input PDF/DOCX/TXT document"
    )

    parser.add_argument(
        "--chunk_size",
        type=int,
        default=400
    )

    parser.add_argument(
        "--overlap",
        type=int,
        default=50
    )

    parser.add_argument(
        "--save_chunks",
        action="store_true",
        help="Save generated chunks for debugging"
    )

    args = parser.parse_args()

    print("\nStarting ISO Compliance Pipeline...\n")

    # ---------------------------------------------------------
    # 1. Load config
    # ---------------------------------------------------------
    config = load_config("config/config.yaml")

    # ---------------------------------------------------------
    # 2. Load ISO clauses (Part 3 + Part 4)
    # ---------------------------------------------------------
    iso_part3 = load_iso_clauses("data/iso/iso_part3.json")
    iso_part4 = load_iso_clauses("data/iso/iso_part4.json")

    iso_clauses = iso_part3 + iso_part4

    print(
        f"Loaded {len(iso_clauses)} ISO clauses "
        f"(Part 3: {len(iso_part3)}, "
        f"Part 4: {len(iso_part4)})"
    )

    # ---------------------------------------------------------
    # 3. Extract document
    # ---------------------------------------------------------
    print(f"\nReading: {args.input}")

    raw_text = extract_text(args.input)

    # ---------------------------------------------------------
    # 4. Clean text
    # ---------------------------------------------------------
    print("Cleaning text...")

    cleaned_text = clean_text(raw_text)

    # ---------------------------------------------------------
    # 5. Chunk text
    # ---------------------------------------------------------
    print(
        f"Chunking "
        f"(size={args.chunk_size}, overlap={args.overlap})..."
    )

    chunks = chunk_text(
        cleaned_text,
        chunk_size=args.chunk_size,
        overlap=args.overlap
    )

    print(f"Generated {len(chunks)} chunks")

    # ---------------------------------------------------------
    # 6. Optional debug save
    # ---------------------------------------------------------
    if args.save_chunks:
        save_debug_chunks(chunks)
        print("Saved debug chunks to debug/chunks.json")

    # ---------------------------------------------------------
    # 7. Prepare chunk texts + metadata
    # ---------------------------------------------------------
    chunk_texts = [c["text"] for c in chunks]

    chunk_metadata = []

    for i, chunk in enumerate(chunks):

        metadata = chunk.get("metadata", {})

        metadata.update({
            "chunk_id": f"chunk_{i}",
            "source_file": os.path.basename(args.input)
        })

        chunk_metadata.append(metadata)

    # ---------------------------------------------------------
    # 8. Initialize embedding model
    # ---------------------------------------------------------
    embedder = OllamaEmbeddingModel(
        model=config["embedding"]["model"]
    )

    # ---------------------------------------------------------
    # 9. Embed chunks
    # ---------------------------------------------------------
    print("\nEmbedding document...")

    embeddings = embedder.embed_texts(chunk_texts)

    # ---------------------------------------------------------
    # 10. Build vector store
    # ---------------------------------------------------------
    vectorstore = FAISSStore(
        dim=len(embeddings[0])
    )

    vectorstore.add(
        embeddings=embeddings,
        texts=chunk_texts,
        metadatas=chunk_metadata
    )

    # ---------------------------------------------------------
    # 11. Retriever
    # ---------------------------------------------------------
    retriever = Retriever(
        embedder=embedder,
        vectorstore=vectorstore,
        top_k=config["retrieval"]["top_k"],
        similarity_threshold=config["retrieval"].get("min_score", 0.35)
    )

    # ---------------------------------------------------------
    # 12. LLM
    # ---------------------------------------------------------
    llm = OllamaLLM(
        model=config["llm"]["model"],
        temperature=config["llm"]["generation"]["temperature"],
        top_p=config["llm"]["generation"]["top_p"],
        top_k=config["llm"]["generation"]["top_k"],
    )

    # ---------------------------------------------------------
    # 13. Evaluator
    # ---------------------------------------------------------
    evaluator = Evaluator(
        retriever=retriever,
        llm=llm,
        schema_validator=SchemaValidator(),
        max_evidence_retries=config["evaluation"].get("evidence_retries", 1),
        weak_evidence_threshold=config["evaluation"].get(
            "weak_evidence_threshold",
            0.45
        )
    )

    print("\nRunning clause-by-clause evaluation...\n")

    results = evaluator.evaluate(iso_clauses)

    # ---------------------------------------------------------
    # 14. Aggregate results
    # ---------------------------------------------------------
    aggregator = Aggregator()

    final_report = aggregator.aggregate(results)

    # ---------------------------------------------------------
    # 15. Save report
    # ---------------------------------------------------------
    os.makedirs("output", exist_ok=True)

    output_path = "output/compliance_report.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    print(f"\nCompliance report generated: {output_path}")


# ---------------------------------------------------------
# Entry
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
