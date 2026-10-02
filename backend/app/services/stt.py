"""
Speech-to-text service.

Uses OpenAI's Whisper API to transcribe spoken Telugu audio into Telugu text.
Whisper supports Telugu natively and needs no extra configuration beyond the
language hint, which improves accuracy over auto-detection.

To swap in Bhashini's ASR API later (as noted in the pitch deck as a
future upgrade), replace the body of `transcribe_audio` and keep the same
function signature so the rest of the pipeline is unaffected.
"""

import io
from openai import OpenAI

client = OpenAI()  # reads OPENAI_API_KEY from environment


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """
    Transcribe recorded speech to Telugu text.

    audio_bytes: raw bytes of the recorded clip (webm/mp3/wav all work with Whisper)
    filename: original filename/extension, used by the API to detect the codec
    """
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # the SDK inspects the extension from this

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="te",  # ISO code for Telugu — improves accuracy vs. auto-detect
    )
    return transcript.text.strip()
