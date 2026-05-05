import requests


class OllamaEmbeddingModel:
    def __init__(self, model: str):
        self.model = model
        self.url = "http://localhost:11434/api/embeddings"

    def embed_texts(self, texts):
        if not texts:
            return []

        embeddings = []

        for text in texts:
            response = requests.post(
                self.url,
                json={"model": self.model, "prompt": text}
            )

            response.raise_for_status()

            data = response.json()

            if "embedding" not in data:
                raise ValueError(f"Invalid response from Ollama: {data}")

            embeddings.append(data["embedding"])

        return embeddings