import re


def clean_text(raw_text: str) -> str:
    """
    Normalize extracted document text before it is sent to the AI.

    This performs light, format-preserving cleanup only:
    - Collapses runs of 3+ blank lines down to a single blank line
      (preserves paragraph breaks without excessive gaps).
    - Collapses repeated horizontal whitespace (spaces/tabs) into one space.
    - Strips trailing whitespace from each line.
    - Strips leading/trailing whitespace from the whole text.

    This is intentionally conservative: it does not attempt to fix
    hyphenation, reflow paragraphs, or otherwise rewrite content.

    Args:
        raw_text: The unprocessed text returned by document_parser.extract_text().

    Returns:
        Cleaned text, ready for length checks and summarization.
    """
    # Strip trailing whitespace on each line first.
    lines = [line.rstrip() for line in raw_text.split("\n")]
    text = "\n".join(lines)

    # Collapse 3+ consecutive newlines (2+ blank lines) into a single blank line.
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse repeated spaces/tabs within lines into a single space.
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


def is_effectively_empty(text: str) -> bool:
    """
    Check whether cleaned text contains no meaningful content.

    Used after clean_text() to catch documents that technically parsed
    but yielded only whitespace or trivial content (e.g. a page with
    just a single stray character or numeral).

    Args:
        text: Text that has already been through clean_text().

    Returns:
        True if the text has no usable content.
    """
    return len(text.strip()) < 10