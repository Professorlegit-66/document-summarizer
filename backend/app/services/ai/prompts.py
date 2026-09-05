from typing import Literal

SummaryLength = Literal["short", "medium", "detailed"]
SummaryStyle = Literal["paragraph", "bullet_points", "key_takeaways"]

_LENGTH_INSTRUCTIONS: dict[SummaryLength, str] = {
    "short": "Write a very concise summary in about 2-3 sentences.",
    "medium": "Write a clear summary in about 1-2 short paragraphs.",
    "detailed": "Write a thorough, detailed summary covering all major points, "
                "using multiple paragraphs if needed.",
}

_STYLE_INSTRUCTIONS: dict[SummaryStyle, str] = {
    "paragraph": "Format the summary as flowing prose paragraphs. Do not use bullet points.",
    "bullet_points": "Format the summary as a bulleted list of the key points. "
                     "Use '-' for each bullet.",
    "key_takeaways": "Format the summary as a short list of key takeaways, "
                     "each starting with a bolded 3-5 word label followed by "
                     "a brief explanation.",
}


def build_summary_prompt(
    text: str,
    length: SummaryLength = "medium",
    style: SummaryStyle = "paragraph",
) -> str:
    """
    Build a complete prompt instructing the AI to summarize the given text.

    Args:
        text: The source text to summarize.
        length: Desired summary length (short, medium, detailed).
        style: Desired output format (paragraph, bullet_points, key_takeaways).

    Returns:
        A single prompt string ready to send to the AI model.
    """
    length_instruction = _LENGTH_INSTRUCTIONS[length]
    style_instruction = _STYLE_INSTRUCTIONS[style]

    return (
        "You are a precise summarization assistant. Summarize the text below.\n\n"
        f"Length requirement: {length_instruction}\n"
        f"Format requirement: {style_instruction}\n\n"
        "Only return the summary itself. Do not include any preamble like "
        "'Here is the summary' or any commentary about the text.\n\n"
        "Text to summarize:\n"
        "\"\"\"\n"
        f"{text}\n"
        "\"\"\"\n"
    )