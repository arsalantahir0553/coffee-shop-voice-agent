import numpy as np
import sounddevice as sd

from . import config


def record_until_silence():
    """Records from the mic until the customer pauses, with a hard time cap."""
    print("Listening... (speak now)")
    chunk_duration = 0.25
    chunk_samples = int(config.SAMPLE_RATE * chunk_duration)
    silence_chunks_needed = int(config.SILENCE_DURATION / chunk_duration)
    max_chunks = int(config.MAX_RECORD_SECONDS / chunk_duration)

    frames = []
    silence_run = 0
    speech_started = False

    with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, dtype="float32") as stream:
        for _ in range(max_chunks):
            data, _ = stream.read(chunk_samples)
            data = data[:, 0]
            frames.append(data)
            rms = float(np.sqrt(np.mean(np.square(data))))
            if rms > config.SILENCE_THRESHOLD:
                speech_started = True
                silence_run = 0
            elif speech_started:
                silence_run += 1
                if silence_run >= silence_chunks_needed:
                    break

    if not frames:
        return np.array([], dtype=np.float32)
    return np.concatenate(frames)
