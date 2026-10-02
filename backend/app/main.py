"""
Krishi Sahayak backend — FastAPI app.

Pipeline for POST /api/voice-query:
  1. Speech-to-text: Telugu audio -> Telugu text            (services/stt.py)
  2. Translate:      Telugu text  -> English text            (services/translate.py)
  3. Retrieve:       English text -> top matching KB entries (services/retrieve.py)
  4. Answer:         KB entries   -> grounded English answer (services/answer.py)
  5. Translate back:  English answer -> Telugu answer         (services/translate.py)
  6. Text-to-speech: Telugu answer -> spoken audio            (services/tts.py)

POST /api/text-query runs the same pipeline starting from typed Telugu text
instead of audio — useful for testing without a microphone, and as a
fallback input mode in the UI.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from app.models import TextQueryRequest, QueryResponse, HealthResponse
from app.services import stt, translate, retrieve, answer, tts

app = FastAPI(title="Krishi Sahayak API")

# In production, replace "*" with your deployed frontend's exact origin.
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _run_pipeline(telugu_question: str) -> QueryResponse:
    english_question = translate.telugu_to_english(telugu_question)
    retrieved = retrieve.retrieve(english_question)
    english_answer, matched_source_id = answer.generate_answer(english_question, retrieved)
    telugu_answer = translate.english_to_telugu(english_answer)
    audio_base64 = tts.synthesize_speech(telugu_answer)

    return QueryResponse(
        telugu_question=telugu_question,
        english_question=english_question,
        english_answer=english_answer,
        telugu_answer=telugu_answer,
        matched_source_id=matched_source_id,
        audio_base64=audio_base64,
    )


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", knowledge_base_size=retrieve.knowledge_base_size())


@app.post("/api/text-query", response_model=QueryResponse)
def text_query(payload: TextQueryRequest):
    if not payload.telugu_text.strip():
        raise HTTPException(status_code=400, detail="telugu_text must not be empty")
    return _run_pipeline(payload.telugu_text)


@app.post("/api/voice-query", response_model=QueryResponse)
async def voice_query(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    telugu_question = stt.transcribe_audio(audio_bytes, filename=audio.filename or "audio.webm")
    if not telugu_question:
        raise HTTPException(status_code=422, detail="Could not transcribe any speech from the audio")

    return _run_pipeline(telugu_question)
