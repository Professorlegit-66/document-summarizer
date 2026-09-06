import re

import httpx

from app.core.config import settings
from app.services.ai.exceptions import (
    AIModelNotFoundError,
    AIRequestTimeoutError,
    AIResponseError,
    AIServiceUnavailableError,
)
from app.services.ai.prompts import SummaryLength, SummaryStyle, build_summary_prompt

_GENERATE_ENDPOINT = "/api/generate"


def _strip_markdown(text: str) -> str:
    """
    Remove common Markdown formatting artifacts from AI output.

    Local models sometimes emit Markdown syntax (bold, headers) even when
    instructed not to. This is a defensive backstop, not the primary fix —
    the prompt itself asks for plain text — but we don't rely on the model
    following instructions perfectly.
    """
    # Bold/italic: **text** or *text* or __text__ or _text_
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)

    # Markdown headers: "# Heading", "## Heading", etc. -> "Heading"
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    return text


def summarize(
    text: str,
    length: SummaryLength = "medium",
    style: SummaryStyle = "paragraph",
) -> str:
    """
    Generate an AI summary of the given text using the configured Ollama model.

    Args:
        text: The source text to summarize.
        length: Desired summary length (short, medium, detailed).
        style: Desired output format (paragraph, bullet_points, key_takeaways).

    Returns:
        The generated summary as plain text.

    Raises:
        AIServiceUnavailableError: If Ollama cannot be reached.
        AIModelNotFoundError: If the configured model is not available.
        AIRequestTimeoutError: If the request takes too long.
        AIResponseError: If Ollama responds but the response is unusable.
    """
    prompt = build_summary_prompt(text, length=length, style=style)
    url = f"{settings.ollama_base_url}{_GENERATE_ENDPOINT}"

    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": settings.ollama_num_ctx,
        },
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            timeout=settings.ollama_timeout_seconds,
        )
    except httpx.ConnectError as exc:
        raise AIServiceUnavailableError(
            "Could not connect to the AI service. Is Ollama running?"
        ) from exc
    except httpx.TimeoutException as exc:
        raise AIRequestTimeoutError(
            "The AI service took too long to respond."
        ) from exc

    if response.status_code == 404:
        raise AIModelNotFoundError(
            f"Model '{settings.ollama_model}' was not found. "
            f"Try running: ollama pull {settings.ollama_model}"
        )

    if response.status_code != 200:
        raise AIResponseError(
            f"AI service returned an unexpected status code: {response.status_code}"
        )

    try:
        data = response.json()
        summary = data["response"].strip()
    except (ValueError, KeyError) as exc:
        raise AIResponseError("AI service returned an invalid response.") from exc

    if not summary:
        raise AIResponseError("AI service returned an empty summary.")

    return _strip_markdown(summary)