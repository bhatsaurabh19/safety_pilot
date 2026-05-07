# ISO Compliance Agent - Roadmap

## Phase 1 - Core Pipeline
- [x] Ingestion pipeline
- [x] Chunking
- [x] Embeddings
- [x] Vector store
- [x] Retriever
- [x] Evaluator
- [x] Strict schema validation
- [x] Aggregator
- [x] Audit logging

---

## Phase 2 - Retrieval Hardening
- [x] Metadata support
- [x] Retrieval scoring
- [x] Similarity thresholds
- [x] Retrieval confidence
- [x] Evidence normalization

---

## Phase 3 - Structure Improvements
- [x] Better cleaner
- [x] Better chunker
- [x] Section-aware chunking
- [x] Metadata-aware chunks

---

## Phase 3.5 - Stabilization Before Agentic Phase
- [x] Fix evidence formatting before LLM evaluation
- [x] Wire `retrieval.min_score` from `config/config.yaml` into `Retriever`
- [x] Add result consistency checks between `status` and evaluation fields
- [x] Add tests for prompt evidence formatting
- [x] Add tests for schema/status consistency
- [x] Add tests for retrieval threshold configuration
- [x] Verify prompt output no longer contains character-split evidence
- [x] Clean up roadmap/README encoding issues

---

## Phase 4 - Agentic Compliance System

### Phase 4A - Evidence-Aware Agent
- [x] Evidence retry loop
- [x] Weak evidence detection
- [x] Retrieval reranking
- [x] Evidence confidence propagation
- [x] Multi-pass evaluation

### Phase 4B - Remediation Agent
- [ ] Generate remediation plans
- [ ] Suggest missing artifacts
- [ ] Recommend traceability structure
- [ ] Gap prioritization

### Phase 4C - Multi-Agent System
- [ ] Retrieval agent
- [ ] Audit agent
- [ ] Risk agent
- [ ] Remediation agent
- [ ] Report agent

---

## Phase 5 - Real ISO Knowledge Base
- [ ] Real ISO parser
- [ ] Clause hierarchy extraction
- [ ] Requirement structuring
- [ ] ISO knowledge graph

---

## Phase 6 - Traceability Intelligence
- [ ] Safety Goal <-> TSR mapping
- [ ] Traceability graph
- [ ] Coverage analysis
- [ ] Dependency validation

---

## Phase 7 - Human Audit Platform
- [ ] Upload UI
- [ ] Evidence explorer
- [ ] Audit dashboard
- [ ] Export reports
- [ ] Review workflow
