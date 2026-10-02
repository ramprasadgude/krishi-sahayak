from pydantic import BaseModel
from typing import Optional


class TextQueryRequest(BaseModel):
    """Used by the text-input path (and for local testing without a microphone)."""
    telugu_text: str


class QueryResponse(BaseModel):
    telugu_question: str
    english_question: str
    english_answer: str
    telugu_answer: str
    matched_source_id: Optional[str] = None
    audio_base64: Optional[str] = None  # base64-encoded MP3 of the spoken Telugu answer


class HealthResponse(BaseModel):
    status: str
    knowledge_base_size: int
