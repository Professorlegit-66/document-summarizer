"""
PDF text extraction using PyMuPDF (pymupdf).
"""

import pymupdf

from .exceptions import EmptyFileError, CorruptedFileError, NoTextExtractedError


def parse_pdf(file_bytes: bytes) -> str:
    """
    Extract text from raw PDF file bytes.

    Raises:
        EmptyFileError: if the file has zero bytes.
        CorruptedFileError: if the PDF structure cannot be opened.
        NoTextExtractedError: if the PDF opens but contains no extractable
            text (e.g. a scanned/image-only PDF with no embedded text layer).
    """
    if len(file_bytes) == 0:
        raise EmptyFileError("The uploaded PDF file is empty.")

    try:
        document = pymupdf.open(stream=file_bytes, filetype="pdf")
    except pymupdf.FileDataError as exc:
        raise CorruptedFileError("The PDF file is corrupted or not a valid PDF.") from exc

    try:
        if document.page_count == 0:
            raise NoTextExtractedError("The PDF contains no pages.")

        pages_text = []
        for page in document:
            pages_text.append(page.get_text())

        full_text = "\n\n".join(pages_text)

        if not full_text.strip():
            raise NoTextExtractedError(
                "The PDF contains no extractable text. "
                "It may be a scanned document without a text layer."
            )

        return full_text
    finally:
        document.close()