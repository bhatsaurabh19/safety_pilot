import re


def split_into_clauses(text: str):
    """
    More robust clause splitter for ISO-like documents
    """

    # Normalize text first
    text = text.replace("\n", " ")

    # Match clause numbers like:
    # 6.4
    # 6.4.2
    # 7.1.3.1
    pattern = r"(\d+\.\d+(?:\.\d+)*)"

    matches = list(re.finditer(pattern, text))

    clauses = []

    for i in range(len(matches)):
        start = matches[i].start()
        clause_id = matches[i].group()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        clause_text = text[start:end].strip()

        # Filter tiny garbage clauses
        if len(clause_text) > 100:
            clauses.append({
                "clause_id": clause_id,
                "text": clause_text
            })

    return clauses