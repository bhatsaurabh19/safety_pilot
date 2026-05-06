import faiss
import numpy as np
from typing import List, Dict, Any


class FAISSStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)

        # Full audit-grade storage
        self.records: List[Dict[str, Any]] = []

    def add(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None,
    ):
        if not embeddings:
            raise ValueError("No embeddings provided")

        if len(embeddings) != len(texts):
            raise ValueError("Embeddings/text count mismatch")

        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Metadata/text count mismatch")

        self.index.add(np.array(embeddings).astype("float32"))

        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas else {}

            self.records.append({
                "id": metadata.get("chunk_id", f"chunk_{len(self.records)}"),
                "text": text,
                "metadata": metadata
            })

    def search(self, query_embedding, top_k=5):
        if len(self.records) == 0:
            return []

        query_embedding = np.array([query_embedding]).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        results = []

        for idx, distance in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.records):
                continue

            record = self.records[idx]

            # Convert L2 distance → similarity-like score
            score = 1 / (1 + float(distance))

            results.append({
                "id": record["id"],
                "text": record["text"],
                "score": round(score, 4),
                "metadata": record["metadata"]
            })

        return results