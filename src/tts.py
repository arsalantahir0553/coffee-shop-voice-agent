import numpy as np
import sounddevice as sd
from piper import PiperVoice

from . import config

_voice = None


def get_voice():
    global _voice
    if _voice is None:
        if not config.PIPER_VOICE_PATH.exists():
            raise FileNotFoundError(
                f"Piper voice not found at {config.PIPER_VOICE_PATH}. "
                "Run: python -m piper.download_voices en_US-lessac-medium "
                "and move the .onnx/.onnx.json files into the voices/ folder."
            )
        _voice = PiperVoice.load(str(config.PIPER_VOICE_PATH))
    return _voice


def speak(text):
    if not text:
        return
    voice = get_voice()
    for chunk in voice.synthesize(text):
        audio = np.frombuffer(chunk.audio_int16_bytes, dtype=np.int16)
        sd.play(audio, samplerate=chunk.sample_rate, blocking=True)
