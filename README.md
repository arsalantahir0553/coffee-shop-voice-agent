# Coffee Shop Voice Ordering Agent

A fully offline, local voice ordering agent for a coffee shop kiosk. No cloud
APIs, no third-party accounts, no subscriptions — everything runs on your own
Windows PC:

- **Speech-to-text:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (local Whisper model, runs on CPU)
- **Conversation brain:** [Ollama](https://ollama.com) running a small local LLM
- **Text-to-speech:** [Piper](https://github.com/OHF-Voice/piper1-gpl) (local neural TTS)

The customer presses Enter, speaks their order into the mic, and the agent
talks back through the speakers, confirms the order, and logs it to a local
file for staff to see.

## One-time internet requirement

Nothing here calls a cloud API while running. But the *first* setup does need
internet once, to download the open-source model files (a few GB total) to
your machine. After that, the whole thing works with no internet connection.

## Setup (Windows)

1. **Install Ollama** (the local LLM runtime): download and install from
   https://ollama.com/download/windows. After installing, it runs a local
   server automatically on `http://localhost:11434`.

2. **Pull a small local model** (good balance of speed/quality on a CPU-only
   machine):
   ```bash
   ollama pull llama3.2:3b
   ```
   If replies are too slow on your PC, try an even smaller model like
   `qwen2.5:1.5b-instruct` and update `OLLAMA_MODEL` in `src/config.py`.

3. **Create a Python virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Download a Piper voice** (local text-to-speech model):
   ```bash
   python -m piper.download_voices en_US-lessac-medium
   ```
   Move the downloaded `en_US-lessac-medium.onnx` and
   `en_US-lessac-medium.onnx.json` files into the `voices/` folder in this
   project (create it if it doesn't exist).

5. **Edit `menu.json`** to replace the placeholder menu with your shop's
   actual drinks, sizes, milk options, add-ons, and prices.

6. **Run the agent** from the project root:
   ```bash
   python -m src.main
   ```
   Press Enter, speak an order (e.g. "I'd like a large iced oat milk latte
   with vanilla, for here"), and the agent will respond out loud and build up
   the order. Confirmed orders are appended to `orders/orders_log.jsonl`.

## How it works

### Web kiosk

The React kiosk is in `frontend/` and uses the same voice ordering service.
With Ollama and the Python dependencies running, start the API from the
repository root:

```powershell
uvicorn src.server:app --host 127.0.0.1 --port 8000
```

In another terminal, start the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Vite forwards `/api` requests to port 8000.
The downloaded Piper `.onnx` model, local orders, virtual environment, and
frontend build output are intentionally excluded from Git.


- `audio_io.py` records from the microphone and auto-stops when it detects
  the customer has paused (simple volume-based silence detection, no
  external library needed).
- `stt.py` transcribes the recording locally with faster-whisper.
- `llm_client.py` sends the transcript plus the menu and current order to the
  local Ollama model, and asks it to reply with a small JSON object: what to
  say out loud, and any items to add/remove.
- `menu.py` / `order_session.py` validate whatever the model proposes against
  the real menu (`menu.json`) before adding it to the order — this keeps the
  order accurate even if the small local model misunderstands something.
- `tts.py` speaks the agent's reply out loud with Piper.
- Once the customer confirms, the order and total are appended to
  `orders/orders_log.jsonl` as one JSON line per order.

## Known limitations

- **Model quality:** a small local model (3B parameters) is noticeably less
  capable than a large cloud model at handling ambiguous or unusual orders.
  It may occasionally misparse an item; that's why every item is re-validated
  against `menu.json` before being added.
- **Latency:** on a CPU-only PC, expect roughly a few seconds between the
  customer finishing speaking and the agent replying. A GPU (or a smaller
  model) will make this feel more real-time.
- **No wake word / hands-free listening:** to keep this simple and fully
  local (avoiding third-party wake-word engines), the customer presses Enter
  to start each turn rather than the kiosk always listening.
- **No payment or POS integration:** this only takes and logs the order, as
  scoped. Staff read `orders/orders_log.jsonl` (or you can extend `log()` in
  `order_session.py` to print a ticket, write to a shared folder, etc.).
