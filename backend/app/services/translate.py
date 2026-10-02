"""
Translation service: Telugu <-> English.

MVP implementation uses deep-translator's GoogleTranslator, which is free
and needs no API key — good for a hackathon build with a tight timeline.

The pitch deck lists AI4Bharat IndicTrans2 / Bhashini as the intended
production-grade translation layer, since they're tuned specifically for
Indian languages and can run without depending on Google's service. To
upgrade, swap the two functions below to call IndicTrans2 (self-hosted or
via Bhashini's API) and keep the same function signatures.
"""

from deep_translator import GoogleTranslator


def telugu_to_english(text: str) -> str:
    if not text.strip():
        return ""
    return GoogleTranslator(source="te", target="en").translate(text)


def english_to_telugu(text: str) -> str:
    if not text.strip():
        return ""
    return GoogleTranslator(source="en", target="te").translate(text)
