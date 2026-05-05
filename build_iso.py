from src.iso_builder.builder import build_iso_json

if __name__ == "__main__":
    build_iso_json(
        pdf_path="standards/iso26262_part3.pdf",
        output_path="generated/iso_part3.json",
        part="3"
    )