"""
Text extraction logic for uploaded resumes.
Supports PDF (via PyMuPDF) and DOCX (via python-docx).
This module has no FastAPI dependency — it's pure logic, easy to test on its own.
"""

import io
import fitz  # PyMuPDF
import docx


class UnsupportedFileTypeError(Exception):
    """Raised when a file extension isn't supported."""
    pass


class EmptyResumeError(Exception):
    """Raised when no extractable text is found."""
    pass


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from a PDF's bytes using PyMuPDF."""
    text_parts = []

    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text_parts.append(page.get_text())

    return "\n".join(text_parts).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract raw text from a DOCX's bytes using python-docx."""
    document = docx.Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs]

    return "\n".join(paragraphs).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    """

    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)

    elif lower_name.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)

    else:
        raise UnsupportedFileTypeError(
            f"Unsupported file type: {filename}. "
            "Only .pdf and .docx are supported."
        )

    if not text:
        raise EmptyResumeError(
            "No readable text found in the file. "
            "It may be a scanned image or corrupted."
        )

    return text