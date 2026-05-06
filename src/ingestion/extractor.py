import fitz  # PyMuPDF
import pdfplumber
from docx import Document


def extract_with_pymupdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


def extract_with_pdfplumber(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def is_text_usable(text: str) -> bool:
    if not text:
        return False
    if len(text.strip()) < 200:
        return False
    return True


def extract_text(file_path: str) -> str:
    if file_path.endswith(".pdf"):
        print("🔍 Trying PyMuPDF...")
        text = extract_with_pymupdf(file_path)

        if is_text_usable(text):
            print("✅ PyMuPDF extraction successful")
            return text

        print("⚠️ PyMuPDF weak, switching to pdfplumber...")
        text = extract_with_pdfplumber(file_path)

        if is_text_usable(text):
            print("✅ pdfplumber extraction successful")
            return text

        print("❌ Extraction failed (no OCR fallback yet)")
        return text

    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)

    elif file_path.endswith(".txt"):
        print("📄 Reading TXT file...")
        return extract_text_from_txt(file_path)

    else:
        raise ValueError(f"Unsupported file format: {file_path}")