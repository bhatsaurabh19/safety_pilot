import requests


class OllamaLLM:
    def __init__(self, model: str, temperature=0.1, top_p=0.9, top_k=40):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                },
            },
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise ValueError(f"Invalid response from Ollama: {data}")

        return data["response"]