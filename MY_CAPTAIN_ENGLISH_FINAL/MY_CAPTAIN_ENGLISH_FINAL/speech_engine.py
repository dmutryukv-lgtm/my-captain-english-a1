"""
Озвучення для MY CAPTAIN ENGLISH.
У вебверсії використовується браузерний speechSynthesis,
тому окремий серверний TTS для HTML не потрібен.
"""

VOICE_LANGUAGE = "en-US"

def pronunciation_text(word):
    return str(word or "").strip()
