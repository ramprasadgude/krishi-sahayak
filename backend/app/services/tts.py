"""
Text-to-speech service.

Uses gTTS (Google Text-to-Speech), which is free, needs no API key, and
supports Telugu ("te") out of the box — a pragmatic MVP choice given the
challenge timeline. The pitch deck lists Bhashini TTS as the intended
production upgrade for a more natural Telugu voice; swap the body of
`synthesize_speech` to call it and keep the same signature.
"""

import base64
import io
from gtts import gTTS


def synthesize_speech(telugu_text: str) -> str:
    """
    Returns base64-encoded MP3 audio of the given Telugu text spoken aloud.
    """
    if not telugu_text.strip():
        return ""

    buffer = io.BytesIO()
    tts = gTTS(text=telugu_text, lang="te")
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
