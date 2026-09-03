"""
Shared exception types for the document parsing system.

Every parser (PDF, DOCX, TXT) raises one of these instead of a raw
library-specific exception. This lets the rest of the application
(e.g. the API layer) handle document errors consistently, without
knowing which underlying library or format caused the failure.
"""


class DocumentParserError(Exception):
    """Base class for all document parsing errors."""


class UnsupportedFileTypeError(DocumentParserError):
    """Raised when the file's actual content does not match a supported format."""


class EmptyFileError(DocumentParserError):
    """Raised when the uploaded file has zero bytes."""


class CorruptedFileError(DocumentParserError):
    """Raised when a file appears to be the right format but cannot be opened/parsed."""


class NoTextExtractedError(DocumentParserError):
    """Raised when parsing succeeds but yields no meaningful text (e.g. blank pages, scanned images)."""