from typing import Dict, Any, List


class Retriever:
    def __init__(
        self,
        embedder,
        vectorstore,
        top_k=5,
        similarity_threshold=0.35,
    ):
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

    def get_relevant_chunks(self, query: str) -> Dict[str, Any]:
        if not query or not query.strip():
            return self._empty_result()

        # -----------------------------------------
        # Step 1: Embed query
        # -----------------------------------------
        query_embedding = self.embedder.embed_texts([query])[0]

        # -----------------------------------------
        # Step 2: Raw retrieval
        # -----------------------------------------
        raw_results = self.vectorstore.search(
            query_embedding=query_embedding,
            top_k=self.top_k
        )

        if not raw_results:
            return self._empty_result()

        # -----------------------------------------
        # Step 3: Threshold filtering
        # -----------------------------------------
        filtered = [
            r for r in raw_results
            if r["score"] >= self.similarity_threshold
        ]

        if not filtered:
            return self._empty_result()

        # -----------------------------------------
        # Step 4: Compute retrieval confidence
        # -----------------------------------------
        avg_score = sum(r["score"] for r in filtered) / len(filtered)

        if avg_score >= 0.75:
            confidence = "HIGH"
        elif avg_score >= 0.55:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # -----------------------------------------
        # Step 5: Build response
        # -----------------------------------------
        return {
            "chunks": filtered,
            "avg_score": round(avg_score, 4),
            "retrieval_confidence": confidence
        }

    def _empty_result(self):
        return {
            "chunks": [],
            "avg_score": 0.0,
            "retrieval_confidence": "LOW"
        }