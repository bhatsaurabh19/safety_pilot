import argparse
import json
import os
from typing import Any, Dict

from src.iso_builder.knowledge_graph import build_knowledge_graph
from src.iso_builder.parser import extract_iso_source_text
from src.iso_builder.splitter import split_into_clauses
from src.iso_builder.structurer import structure_clause


def build_iso_knowledge_base(
    input_path: str,
    output_path: str,
    part: str,
    source_name: str = "",
) -> Dict[str, Any]:
    text = extract_iso_source_text(input_path)
    clauses = split_into_clauses(
        text=text,
        part=part,
        source=source_name or os.path.basename(input_path),
    )
    structured_clauses = [
        structure_clause(clause)
        for clause in clauses
    ]

    knowledge_base = {
        "part": part,
        "source": source_name or os.path.basename(input_path),
        "clauses": structured_clauses,
        "knowledge_graph": build_knowledge_graph(structured_clauses),
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2)

    return knowledge_base


def build_iso_json(pdf_path: str, output_path: str, part: str):
    return build_iso_knowledge_base(
        input_path=pdf_path,
        output_path=output_path,
        part=part,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build an ISO clause knowledge base from a local source file."
    )
    parser.add_argument("--input", required=True, help="Input PDF/DOCX/TXT file")
    parser.add_argument("--output", required=True, help="Output JSON file")
    parser.add_argument("--part", required=True, help="ISO part label, e.g. ISO 26262-3")
    parser.add_argument("--source", default="", help="Optional source name")

    args = parser.parse_args()

    result = build_iso_knowledge_base(
        input_path=args.input,
        output_path=args.output,
        part=args.part,
        source_name=args.source,
    )

    print(
        "Built ISO knowledge base: "
        f"{len(result['clauses'])} clauses, "
        f"{len(result['knowledge_graph']['nodes'])} graph nodes"
    )


if __name__ == "__main__":
    main()
