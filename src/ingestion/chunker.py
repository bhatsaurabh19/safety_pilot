import re
from typing import List, Dict


def split_into_sections(text: str) -> List[str]:
    """
    Better section-aware splitting for technical/compliance documents.
    Preserves semantic structure better than naive sentence splitting.
    """

    # Normalize line breaks
    text = text.replace("\r", "\n")

    # Split by:
    # - double newlines
    # - numbered sections
    # - bullet structures
    raw_sections = re.split(
        r"\n\s*\n|(?=\n\d+\.)|(?=\n•)|(?=\n- )",
        text
    )

    sections = []

    for section in raw_sections:
        cleaned = section.strip()

        # Skip tiny fragments
        if len(cleaned) < 40:
            continue

        sections.append(cleaned)

    return sections


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[Dict]:

    sections = split_into_sections(text)

    chunks = []

    current_chunk = ""

    for section in sections:

        # If section fits
        if len(current_chunk) + len(section) <= chunk_size:
            current_chunk += "\n\n" + section

        else:
            # Save previous chunk
            chunk_text_val = current_chunk.strip()

            if chunk_text_val:
                chunks.append({
                    "text": chunk_text_val,
                    "metadata": {
                        "chunk_size": len(chunk_text_val)
                    }
                })

            # Overlap preservation
            overlap_text = (
                chunk_text_val[-overlap:]
                if overlap > 0 and chunk_text_val
                else ""
            )

            current_chunk = overlap_text + "\n\n" + section

    # Final chunk
    final_chunk = current_chunk.strip()

    if final_chunk:
        chunks.append({
            "text": final_chunk,
            "metadata": {
                "chunk_size": len(final_chunk)
            }
        })

    return chunks