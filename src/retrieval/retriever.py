class Retriever:
    def __init__(self, embedder, vectorstore, top_k=3):
        self.embedder = embedder
        self.vectorstore = vectorstore
        self.top_k = top_k

    def get_relevant_chunks(self, query: str):
        query_embedding = self.embedder.embed_texts([query])[0]
        return self.vectorstore.search(query_embedding, self.top_k)