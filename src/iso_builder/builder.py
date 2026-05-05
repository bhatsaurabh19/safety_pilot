import json
from src.iso_builder.parser import extract_text_from_pdf
from src.iso_builder.splitter import split_into_clauses
from src.iso_builder.structurer import structure_clause
import os

def build_iso_json(pdf_path: str, output_path: str, part: str):
    print("📄 Extracting text...")
    text = extract_text_from_pdf(pdf_path)
    print("\n🔍 RAW TEXT SAMPLE:\n")
    print(text[:1000])


    print("✂️ Splitting into clauses...")
    clauses = split_into_clauses(text)

    print(f"\n🔍 Found {len(clauses)} clauses\n")

    if clauses:
        print("Sample clause:\n")
        print(clauses[0]["text"][:500])
        
    results = []

    print(f"🧠 Processing {len(clauses)} clauses...")

    for clause in clauses[:10]:  # limit for V1
        print(f"Processing clause {clause['clause_id']}")

        structured = structure_clause(clause["text"])

        result = {
            "id": f"ISO26262-{part}:{clause['clause_id']}",
            "clause": clause["clause_id"],
            "part": part,
            **structured
        }

        results.append(result)

    print("💾 Saving JSON...")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print("✅ Done!")