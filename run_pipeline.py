import json
from typing import List, Dict, Any

# -----------------------------
# Imports (your modules)
# -----------------------------
from src.config.loader import load_config
from src.embeddings.ollama_embeddings import OllamaEmbeddingModel
from src.llm.ollama_llm import OllamaLLM
from src.vectorstore.faiss_store import FAISSStore
from src.retrieval.retriever import Retriever

from src.evaluation.evaluator import Evaluator
from src.evaluation.schema import SchemaValidator
from src.aggregation.aggregator import Aggregator


# -----------------------------
# Load ISO clauses
# -----------------------------
def load_iso_clauses(path: str) -> List[Dict[str, Any]]:
    with open(path, "r") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get("clauses", [])
    elif isinstance(data, list):
        return data
    else:
        raise ValueError("Invalid ISO JSON format")


# -----------------------------
# Load document chunks
# -----------------------------
def load_document_chunks(path: str) -> List[str]:
    """
    Assumes pre-processed document chunks (strings).
    Replace later with full ingestion pipeline.
    """
    with open(path, "r") as f:
        return json.load(f)


# -----------------------------
# Main Pipeline
# -----------------------------
def main():
    print("\n🚀 Starting ISO Compliance Pipeline...\n")

    # -----------------------------
    # 1. Load config
    # -----------------------------
    config = load_config("config/config.yaml")

    # -----------------------------
    # 2. Load ISO clauses
    # -----------------------------
    iso_clauses = load_iso_clauses("data/iso/iso_part4.json")
    print(f"📘 Loaded {len(iso_clauses)} ISO clauses")

    # -----------------------------
    # 3. Load document (chunks)
    # -----------------------------
    doc_chunks = load_document_chunks("data/documents/input_chunks.json")
    print(f"📄 Loaded {len(doc_chunks)} document chunks")

    # -----------------------------
    # 4. Initialize Embedding Model
    # -----------------------------
    embedder = OllamaEmbeddingModel(
        model=config["embedding"]["model"]
    )

    # Embed document
    print("🔗 Embedding document...")
    embeddings = embedder.embed_texts(doc_chunks)

    # -----------------------------
    # 5. Vector Store (FAISS)
    # -----------------------------
    dim = len(embeddings[0])
    store = FAISSStore(dim)

    store.add(embeddings, doc_chunks)

    # -----------------------------
    # 6. Retriever
    # -----------------------------
    retriever = Retriever(
        vectorstore=store,
        embedder=embedder,
        top_k=config["retrieval"]["top_k"]
    )

    # -----------------------------
    # 7. LLM
    # -----------------------------
    llm = OllamaLLM(
        model=config["llm"]["model"],
        temperature=config["llm"]["generation"]["temperature"],
        top_p=config["llm"]["generation"]["top_p"],
        top_k=config["llm"]["generation"]["top_k"],
    )

    # -----------------------------
    # 8. Schema Validator
    # -----------------------------
    schema_validator = SchemaValidator()

    # -----------------------------
    # 9. Evaluator (CORE ENGINE)
    # -----------------------------
    evaluator = Evaluator(
        retriever=retriever,
        llm=llm,
        schema_validator=schema_validator
    )

    print("\n🧠 Running clause-by-clause evaluation...\n")
    results = evaluator.evaluate(iso_clauses)

    # -----------------------------
    # 10. Aggregation (NO LLM)
    # -----------------------------
    aggregator = Aggregator()

    # final_report = aggregator.aggregate(
    #     results=results,
    #     document_name="input_document"
    # )
    final_report = aggregator.aggregate(results)

    # -----------------------------
    # 11. Save Output
    # -----------------------------
    with open("output/compliance_report.json", "w") as f:
        json.dump(final_report, f, indent=2)

    print("\n✅ Compliance report generated: output/compliance_report.json\n")


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    main()