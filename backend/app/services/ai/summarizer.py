import re

import httpx

from app.core.config import settings
from app.services.ai.exceptions import (
    AIModelNotFoundError,
    AIRateLimitError,
    AIRequestTimeoutError,
    AIResponseError,
    AIServiceUnavailableError,
)
from app.services.ai.prompts import SummaryLength, SummaryStyle, build_summary_prompt

_OLLAMA_GENERATE_ENDPOINT = "/api/generate"
_GROQ_CHAT_COMPLETIONS_URL = "https://api.groq.com/openai/v1/chat/completions"


def _strip_markdown(text: str) -> str:
    """
    Remove common Markdown formatting artifacts from AI output.

    Both local and hosted models sometimes emit Markdown syntax (bold,
    headers) even when instructed not to. This is a defensive backstop,
    not the primary fix — the prompt itself asks for plain text — but we
    don't rely on either provider following instructions perfectly.
    """
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"\1", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    return text


def summarize(
    text: str,
    length: SummaryLength = "medium",
    style: SummaryStyle = "paragraph",
) -> str:
    """
    Generate an AI summary of the given text using the configured provider.

    Dispatches to a local Ollama instance or the Groq hosted API based on
    settings.ai_provider ("ollama" by default for local development, "groq"
    in production). Callers never need to know which provider is active —
    both paths raise the same set of custom exceptions on failure.

    Args:
        text: The source text to summarize.
        length: Desired summary length (short, medium, detailed).
        style: Desired output format (paragraph, bullet_points, key_takeaways).

    Returns:
        The generated summary as plain text.

    Raises:
        AIServiceUnavailableError: If the AI service cannot be reached.
        AIModelNotFoundError: If the configured model is not available.
        AIRequestTimeoutError: If the request takes too long.
        AIRateLimitError: If the provider's rate limit has been exceeded.
        AIResponseError: If the provider responds but the response is unusable.
    """
    prompt = build_summary_prompt(text, length=length, style=style)

    if settings.ai_provider == "groq":
        summary = _call_groq(prompt)
    else:
        summary = _call_ollama(prompt)

    return _strip_markdown(summary)


def _call_ollama(prompt: str) -> str:
    """Send a prompt to a local Ollama instance and return the raw summary text."""
    url = f"{settings.ollama_base_url}{_OLLAMA_GENERATE_ENDPOINT}"

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

    return summary


def _call_groq(prompt: str) -> str:
    """Send a prompt to the Groq hosted API and return the raw summary text."""
    if not settings.groq_api_key:
        raise AIServiceUnavailableError(
            "Groq is configured as the AI provider but no API key is set."
        )

    payload = {
        "model": settings.groq_model,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}

    try:
        response = httpx.post(
            _GROQ_CHAT_COMPLETIONS_URL,
            json=payload,
            headers=headers,
            timeout=settings.groq_timeout_seconds,
        )
    except httpx.ConnectError as exc:
        raise AIServiceUnavailableError(
            "Could not connect to the AI service."
        ) from exc
    except httpx.TimeoutException as exc:
        raise AIRequestTimeoutError(
            "The AI service took too long to respond."
        ) from exc

    if response.status_code == 401:
        raise AIServiceUnavailableError(
            "The AI service rejected our credentials."
        )

    if response.status_code == 404:
        raise AIModelNotFoundError(
            f"Model '{settings.groq_model}' was not found."
        )

    if response.status_code == 429:
        raise AIRateLimitError(
            "The AI service's usage limit has been reached. Please try again shortly."
        )

    if response.status_code != 200:
        raise AIResponseError(
            f"AI service returned an unexpected status code: {response.status_code}"
        )

    try:
        data = response.json()
        summary = data["choices"][0]["message"]["content"].strip()
    except (ValueError, KeyError, IndexError) as exc:
        raise AIResponseError("AI service returned an invalid response.") from exc

    if not summary:
        raise AIResponseError("AI service returned an empty summary.")

    return summary