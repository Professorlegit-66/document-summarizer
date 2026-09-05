from pydantic import BaseModel, Field

from app.services.ai.prompts import SummaryLength, SummaryStyle


class SummarizeResponse(BaseModel):
    """
    Response body returned by POST /summarize on success.
    """

    filename: str = Field(..., description="Original name of the uploaded file.")
    summary: str = Field(..., description="The AI-generated summary text.")
    summary_length: SummaryLength = Field(..., description="Length setting used for this summary.")
    summary_style: SummaryStyle = Field(..., description="Style setting used for this summary.")