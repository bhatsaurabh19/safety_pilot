# ISO 26262 Compliance Agent

A local, modular RAG-based compliance evaluation system for ISO 26262.

## Features

- Clause-based evaluation (ISO Part 3 & 4)
- Local embeddings (Ollama)
- Local LLM reasoning (Ollama)
- Strict audit-mode evaluation (no hallucination)
- Deterministic aggregation (no LLM)

## Pipeline

ISO Clauses (JSON)
→ Document Chunks
→ Embeddings (Ollama)
→ FAISS Retrieval
→ Clause Loop Evaluation (LLM)
→ Aggregation
→ Final Report

## Setup

1. Install dependencies: 
```bash
pip install -r requirements.txt
```
2. Start Ollama:
```bash
ollama serve
```
3. Pull models:
```bash
ollama pull mxbai-embed-large
ollama pull llama3
```
## Run
```bash
python run_pipeline.py
```

## Notes

- Uses strict audit mode (ISO “shall” enforcement)
- JSON-based ISO input (no PDF parsing required)

📁 FULL PROJECT STRUCTURE

iso-compliance-agent/
│
├── README.md
├── requirements.txt
├── run_pipeline.py
│
├── config/
│   └── config.yaml
│
├── data/
│   ├── iso/
│   │   ├── iso_part3.json
│   │   └── iso_part4.json
│   │
│   └── documents/
│       └── sample_doc_chunks.json
│
├── src/
│
│   ├── config/
│   │   └── loader.py
│
│   ├── embeddings/
│   │   ├── base.py
│   │   └── ollama_embeddings.py
│
│   ├── llm/
│   │   ├── base.py
│   │   └── ollama_llm.py
│
│   ├── ingestion/
│   │   ├── extractor.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│
│   ├── vectorstore/
│   │   └── faiss_store.py
│
│   ├── retrieval/
│   │   └── retriever.py
│
│   ├── evaluation/
│   │   ├── evaluator.py
│   │   ├── prompt_builder.py
│   │   └── schema.py
│
│   ├── aggregation/
│   │   └── aggregator.py
│
│   └── utils/
│       └── logger.py