from typing import List, Dict


def split_into_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in text.split(". ") if len(p.strip()) > 50]


def chunk_text(text: str, chunk_size: int = 400) -> List[Dict]:
    paragraphs = split_into_paragraphs(text)

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += " " + para
        else:
            chunks.append({
                "text": current_chunk.strip(),
                "metadata": {}
            })
            current_chunk = para

    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "metadata": {}
        })

    return chunks