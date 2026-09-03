"""
Plain text (.txt) extraction.
"""

from .exceptions import EmptyFileError, CorruptedFileError, NoTextExtractedError


def parse_txt(file_bytes: bytes) -> str:
    """
    Extract text from raw TXT file bytes.

    Raises:
        EmptyFileError: if the file has zero bytes.
        CorruptedFileError: if the bytes cannot be decoded as text.
        NoTextExtractedError: if decoding succeeds but content is blank/whitespace only.
    """
    if len(file_bytes) == 0:
        raise EmptyFileError("The uploaded TXT file is empty.")

    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CorruptedFileError("The TXT file could not be decoded as UTF-8 text.") from exc

    if not text.strip():
        raise NoTextExtractedError("The TXT file contains no readable text content.")

    return text