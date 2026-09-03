"""
Content-based file type detection.

We do NOT trust file extensions. Instead we inspect the first bytes
of the file (its "magic number" / signature) to determine the real
format. This is lightweight and requires no extra system dependencies
(unlike python-magic, which needs libmagic installed separately).
"""

import zipfile
import io

from .exceptions import UnsupportedFileTypeError

# PDF files always start with this exact byte sequence.
PDF_SIGNATURE = b"%PDF-"

# DOCX files are ZIP archives, and ZIP archives start with this signature.
ZIP_SIGNATURE = b"PK\x03\x04"

# Marker file that only exists inside a real Word .docx package.
DOCX_INTERNAL_MARKER = "word/document.xml"


def detect_file_type(file_bytes: bytes) -> str:
    """
    Inspect raw file bytes and return one of: "pdf", "docx", "txt".

    Raises:
        UnsupportedFileTypeError: if the content doesn't match any
            supported format.
    """
    if file_bytes.startswith(PDF_SIGNATURE):
        return "pdf"

    if file_bytes.startswith(ZIP_SIGNATURE):
        if _is_docx(file_bytes):
            return "docx"
        # It's a valid zip, but not a Word document (could be .xlsx, .pptx, a plain .zip, etc.)
        raise UnsupportedFileTypeError(
            "File is a ZIP-based format but not a valid Word (.docx) document."
        )

    if _looks_like_text(file_bytes):
        return "txt"

    raise UnsupportedFileTypeError(
        "File content does not match a supported format (PDF, DOCX, TXT)."
    )


def _is_docx(file_bytes: bytes) -> bool:
    """Check whether a ZIP archive is specifically a DOCX package."""
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
            return DOCX_INTERNAL_MARKER in archive.namelist()
    except zipfile.BadZipFile:
        return False


def _looks_like_text(file_bytes: bytes) -> bool:
    """
    Heuristic check for plain text: try decoding as UTF-8.

    This isn't perfect (some binary files could theoretically decode
    without error), but combined with the earlier PDF/ZIP checks it's
    a reasonable, dependency-free approach for an MVP.
    """
    try:
        file_bytes.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False