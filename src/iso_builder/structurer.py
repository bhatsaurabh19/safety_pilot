import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def build_prompt(clause_text: str) -> str:
    return f"""
Given the following ISO 26262 clause:

{clause_text}

Extract and return JSON with:
- requirement
- intent
- keywords
- expected_evidence
- evaluation_logic:
    - must_have
    - good_to_have
- red_flags

Return ONLY valid JSON.
"""


def call_ollama(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]


def structure_clause(clause_text: str):
    prompt = build_prompt(clause_text)

    raw_output = call_ollama(prompt)

    try:
        structured = json.loads(raw_output)
    except Exception:
        structured = {
            "error": "Failed to parse",
            "raw_output": raw_output
        }

    return structured