from faster_whisper import WhisperModel

from . import config

_model = None


def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            config.WHISPER_MODEL_SIZE,
            device=config.WHISPER_DEVICE,
            compute_type=config.WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe(audio):
    model = get_model()
    segments, _ = model.transcribe(audio, language="en", beam_size=1)
    return " ".join(seg.text.strip() for seg in segments).strip()
