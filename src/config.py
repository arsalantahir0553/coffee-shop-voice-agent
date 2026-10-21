from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MENU_PATH = BASE_DIR / "menu.json"
ORDERS_LOG_PATH = BASE_DIR / "orders" / "orders_log.jsonl"

# Local Ollama server - no cloud calls, must be running via `ollama serve`.
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"

# faster-whisper model size. "base.en" balances accuracy and CPU speed for a
# regular (non-GPU) machine. Use "tiny.en" if responses feel too slow.
WHISPER_MODEL_SIZE = "base.en"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# Local Piper voice model file, downloaded once via `python -m piper.download_voices`.
PIPER_VOICE_PATH = BASE_DIR / "voices" / "en_US-lessac-medium.onnx"

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 0.01
SILENCE_DURATION = 1.2
MAX_RECORD_SECONDS = 15
