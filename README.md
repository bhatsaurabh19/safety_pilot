# ISO 26262 Compliance Agent

A local, modular RAG-based compliance evaluation system for ISO 26262.

## Features

- Clause-based evaluation for ISO 26262 Part 3 and Part 4 inputs
- Local embeddings through Ollama
- Local LLM reasoning through Ollama
- Strict audit-mode evaluation
- Deterministic aggregation without LLM summarization
- Per-clause audit logs

## Pipeline

1. Load ISO clauses from JSON.
2. Extract input document text.
3. Clean and chunk the document.
4. Generate embeddings with Ollama.
5. Build an in-memory FAISS vector store.
6. Retrieve evidence per ISO clause.
7. Evaluate each clause with the local LLM.
8. Validate schema and status consistency.
9. Aggregate results into `output/compliance_report.json`.

## Setup

```bash
pip install -r requirements.txt
ollama serve
ollama pull mxbai-embed-large
ollama pull llama3.2
```

## Run

```bash
python run_pipeline.py --input input/your_document.pdf
```

Optional chunking controls:

```bash
python run_pipeline.py --input input/your_document.pdf --chunk_size 400 --overlap 50 --save_chunks
```

## Project Structure

```text
.
|-- config/
|   `-- config.yaml
|-- data/
|   |-- iso/
|   |   |-- iso_part3.json
|   |   `-- iso_part4.json
|   `-- documents/
|-- input/
|-- logs/
|-- output/
|   `-- compliance_report.json
|-- src/
|   |-- aggregation/
|   |-- config/
|   |-- embeddings/
|   |-- evaluation/
|   |-- ingestion/
|   |-- iso_builder/
|   |-- llm/
|   |-- retrieval/
|   |-- utils/
|   `-- vectorstore/
|-- tests/
|-- README.md
|-- requirements.txt
|-- run_pipeline.py
`-- steps.md
```

## Notes

- The pipeline is strict by default: missing, unclear, or weak evidence should not be treated as compliant.
- `config/config.yaml` controls Ollama models and retrieval thresholds.
- Generated reports and logs should be reviewed before using results in an audit workflow.
