import fitz  # PyMuPDF
import pdfplumber
from docx import Document


# ---------------------------
# PyMuPDF extraction
# ---------------------------
def extract_with_pymupdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text() + "\n"

    return text


# ---------------------------
# pdfplumber extraction
# ---------------------------
def extract_with_pdfplumber(file_path: str) -> str:
    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# ---------------------------
# DOCX extraction
# ---------------------------
def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


# ---------------------------
# QUALITY CHECK
# ---------------------------
def is_text_usable(text: str) -> bool:
    if not text:
        return False

    # basic heuristic
    if len(text.strip()) < 200:
        return False

    return True


# ---------------------------
# MAIN EXTRACTOR
# ---------------------------
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

    else:
        raise ValueError("Unsupported file format")