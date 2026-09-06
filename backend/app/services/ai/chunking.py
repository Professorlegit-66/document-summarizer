import re

from app.core.config import settings
from app.services.ai.prompts import SummaryLength, SummaryStyle
from app.services.ai.summarizer import summarize

_PARAGRAPH_SPLIT_PATTERN = re.compile(r"\n\s*\n")
_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?])\s+")
_CHUNK_SIZE_CHARS = 12000  # matches chunk_threshold_chars; keeps per-chunk calls within a safe token budget


def generate_summary(
    text: str,
    length: SummaryLength = "medium",
    style: SummaryStyle = "paragraph",
) -> str:
    """
    Generate a summary for text of any length, chunking automatically if needed.

    Text at or under settings.chunk_threshold_chars is summarized directly in
    a single AI call, identical to pre-chunking behavior. Longer text is split
    into chunks, each summarized individually at fixed detailed/paragraph
    settings to preserve information, then combined and re-summarized once
    more using the caller's requested length and style.

    Args:
        text: The cleaned source text to summarize.
        length: Desired final summary length (short, medium, detailed).
        style: Desired final output format (paragraph, bullet_points, key_takeaways).

    Returns:
        The generated summary as plain text.

    Raises:
        AIServiceUnavailableError: If Ollama cannot be reached.
        AIModelNotFoundError: If the configured model is not available.
        AIRequestTimeoutError: If any chunk's request takes too long.
        AIResponseError: If Ollama responds but the response is unusable.
    """
    if len(text) <= settings.chunk_threshold_chars:
        return summarize(text, length=length, style=style)

    chunks = split_into_chunks(text, max_chunk_chars=_CHUNK_SIZE_CHARS)
    print(f"Document split into {len(chunks)} chunks. Starting per-chunk summarization...")

    chunk_summaries = []
    for i, chunk in enumerate(chunks, start=1):
        print(f"Summarizing chunk {i}/{len(chunks)} ({len(chunk)} chars)...")
        chunk_summaries.append(summarize(chunk, length="detailed", style="paragraph"))
        print(f"Chunk {i}/{len(chunks)} done.")

    combined_text = "\n\n".join(chunk_summaries)
    print(f"All chunks summarized. Running final synthesis ({len(combined_text)} chars combined)...")

    final_summary = summarize(combined_text, length=length, style=style)
    print("Final synthesis complete.")

    return final_summary


def split_into_chunks(text: str, max_chunk_chars: int) -> list[str]:
    """
    Split text into a list of chunks, each no longer than max_chunk_chars.

    Splitting prefers paragraph boundaries so related content stays together.
    Falls back to sentence boundaries for any single paragraph that alone
    exceeds the limit, and to a hard character cut as a last resort for any
    single sentence that alone still exceeds the limit.

    Args:
        text: The cleaned source text to split.
        max_chunk_chars: Maximum number of characters allowed per chunk.

    Returns:
        A list of text chunks. Returns a single-item list containing the
        original text unchanged if it already fits within max_chunk_chars.
    """
    if len(text) <= max_chunk_chars:
        return [text]

    paragraphs = _PARAGRAPH_SPLIT_PATTERN.split(text)

    chunks: list[str] = []
    current_chunk = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(paragraph) > max_chunk_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            chunks.extend(_split_long_paragraph(paragraph, max_chunk_chars))
            continue

        candidate = f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph

        if len(candidate) > max_chunk_chars:
            chunks.append(current_chunk)
            current_chunk = paragraph
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _split_long_paragraph(paragraph: str, max_chunk_chars: int) -> list[str]:
    """
    Split a single oversized paragraph on sentence boundaries.

    Falls back to a hard character cut for any single sentence that alone
    still exceeds max_chunk_chars.
    """
    sentences = _SENTENCE_SPLIT_PATTERN.split(paragraph)

    chunks: list[str] = []
    current_chunk = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_chunk_chars:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
            chunks.extend(_hard_split(sentence, max_chunk_chars))
            continue

        candidate = f"{current_chunk} {sentence}" if current_chunk else sentence

        if len(candidate) > max_chunk_chars:
            chunks.append(current_chunk)
            current_chunk = sentence
        else:
            current_chunk = candidate

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def _hard_split(text: str, max_chunk_chars: int) -> list[str]:
    """Split text into fixed-size pieces with no regard for word boundaries."""
    return [
        text[i : i + max_chunk_chars] for i in range(0, len(text), max_chunk_chars)
    ]