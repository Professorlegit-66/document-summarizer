"""
Document parser facade.

This is the ONLY module the rest of the application should import from.
It hides which library or detection strategy is used for any given
format, exposing a single consistent function: extract_text().
"""

from .detector import detect_file_type
from .txt_parser import parse_txt
from .pdf_parser import parse_pdf
from .docx_parser import parse_docx
from .exceptions import (
    DocumentParserError,
    UnsupportedFileTypeError,
    EmptyFileError,
    CorruptedFileError,
    NoTextExtractedError,
)

# Maps a detected file type to its parser function.
_PARSERS = {
    "pdf": parse_pdf,
    "docx": parse_docx,
    "txt": parse_txt,
}


def extract_text(file_bytes: bytes) -> str:
    """
    Detect a document's type from its content and extract its text.

    Args:
        file_bytes: Raw bytes of the uploaded file.

    Returns:
        The extracted, unprocessed text content.

    Raises:
        UnsupportedFileTypeError: if the file content doesn't match
            PDF, DOCX, or TXT.
        EmptyFileError: if the file has zero bytes.
        CorruptedFileError: if the file is the right format but unreadable.
        NoTextExtractedError: if parsing succeeds but yields no usable text.
    """
    file_type = detect_file_type(file_bytes)
    parser = _PARSERS[file_type]
    return parser(file_bytes)


__all__ = [
    "extract_text",
    "DocumentParserError",
    "UnsupportedFileTypeError",
    "EmptyFileError",
    "CorruptedFileError",
    "NoTextExtractedError",
]