from fastapi import UploadFile
import fitz  # PyMuPDF
from typing import Tuple, List


def extract_text_from_pdf_doc(doc) -> str:
    """Extract plain text from PDF while preserving line breaks."""
    text = "\n".join([page.get_text() for page in doc])
    return text


def extract_pdf_content(data: bytes) -> Tuple[str, List[str]]:
    """Open PDF and return (text, links).

    NOTE: This keeps the low-level behavior isolated so service layer can be tested.
    """
    with fitz.open(stream=data, filetype="pdf") as doc:
        text = extract_text_from_pdf_doc(doc)
        # Optionally: extract links using fitz.Page.get_links or custom util
        links: List[str] = []
        return text, links


def is_pdf_file(file: UploadFile) -> bool:
    if file.content_type not in (
        "application/pdf",
        "application/octet-stream",
    ) and not file.filename.lower().endswith(".pdf"):
        return False
    return True
