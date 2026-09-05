from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.models.summarize import SummarizeResponse
from app.services import document_parser
from app.services.ai import summarize as ai_summarize
from app.services.ai.exceptions import (
    AIModelNotFoundError,
    AIRequestTimeoutError,
    AIResponseError,
    AIServiceUnavailableError,
)
from app.services.ai.prompts import SummaryLength, SummaryStyle
from app.services.document_parser import (
    CorruptedFileError,
    EmptyFileError,
    NoTextExtractedError,
    UnsupportedFileTypeError,
)
from app.services.text_processing import clean_text, is_effectively_empty

router = APIRouter()

_BYTES_PER_MB = 1024 * 1024


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(
    file: UploadFile = File(...),
    length: SummaryLength = Form("medium"),
    style: SummaryStyle = Form("paragraph"),
) -> SummarizeResponse:
    """
    Accept an uploaded document and return an AI-generated summary.

    Pipeline: validate size -> extract text -> clean text -> summarize.
    Each stage's errors are mapped to an appropriate HTTP status code.
    """
    file_bytes = await file.read()

    max_bytes = settings.max_upload_size_mb * _BYTES_PER_MB
    if len(file_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the maximum allowed size of "
                   f"{settings.max_upload_size_mb} MB.",
        )

    try:
        raw_text = document_parser.extract_text(file_bytes)
    except UnsupportedFileTypeError:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Please upload a PDF, DOCX, or TXT file.",
        )
    except EmptyFileError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    except CorruptedFileError:
        raise HTTPException(
            status_code=422,
            detail="The file appears to be corrupted or unreadable.",
        )
    except NoTextExtractedError:
        raise HTTPException(
            status_code=422,
            detail="No readable text could be extracted from this document.",
        )

    cleaned_text = clean_text(raw_text)

    if is_effectively_empty(cleaned_text):
        raise HTTPException(
            status_code=422,
            detail="No readable text could be extracted from this document.",
        )

    if len(cleaned_text) > settings.max_extracted_chars:
        raise HTTPException(
            status_code=413,
            detail="This document is too long to summarize right now. "
                   "Support for long documents is coming soon.",
        )

    try:
        summary = ai_summarize(cleaned_text, length=length, style=style)
    except AIServiceUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="The AI service is currently unavailable. "
                   "Please make sure Ollama is running.",
        )
    except AIModelNotFoundError:
        raise HTTPException(status_code=503, detail="The AI model is not available.")
    except AIRequestTimeoutError:
        raise HTTPException(
            status_code=504,
            detail="The AI service took too long to respond.",
        )
    except AIResponseError:
        raise HTTPException(
            status_code=502,
            detail="The AI service returned an unusable response.",
        )

    return SummarizeResponse(
        filename=file.filename,
        summary=summary,
        summary_length=length,
        summary_style=style,
    )