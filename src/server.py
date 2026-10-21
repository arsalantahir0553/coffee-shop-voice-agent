import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import audio_io, config, llm_client, menu, order_session, stt, tts
from .main import apply_agent_actions, build_system_prompt

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_lock = threading.Lock()
_session = order_session.OrderSession()
_history = []
_state = {
    "shop_name": menu.MENU["shop_name"],
    "status": "idle",
    "busy": False,
    "transcript": [],
    "order": [],
    "total": 0.0,
}


def _append_locked(speaker, text):
    _state["transcript"].append({"speaker": speaker, "text": text})


def _sync_order_locked():
    _state["order"] = [i.describe() for i in _session.items]
    _state["total"] = _session.total()


def _run_turn():
    audio = audio_io.record_until_silence()
    if audio.size == 0:
        with _lock:
            _append_locked("Agent", "Didn't catch anything - try again.")
            _state["status"] = "idle"
            _state["busy"] = False
        return

    with _lock:
        _state["status"] = "thinking"

    user_text = stt.transcribe(audio)
    if not user_text:
        with _lock:
            _append_locked("Agent", "Didn't catch anything - try again.")
            _state["status"] = "idle"
            _state["busy"] = False
        return

    with _lock:
        system_prompt = build_system_prompt(_session)

    action, raw = llm_client.get_agent_turn(system_prompt, _history, user_text)

    with _lock:
        apply_agent_actions(_session, action)
        _history.append({"role": "user", "content": user_text})
        _history.append({"role": "assistant", "content": raw})
        _append_locked("You", user_text)
        reply = action.get("reply", "")
        _append_locked("Agent", reply)
        _sync_order_locked()
        _state["status"] = "speaking"

    tts.speak(reply)

    if action.get("order_complete"):
        with _lock:
            record = _session.log()
            _append_locked("Agent", f"Order placed! Total ${record['total']:.2f}. Thank you!")

    with _lock:
        _state["status"] = "idle"
        _state["busy"] = False


@app.get("/api/state")
def get_state():
    with _lock:
        return dict(_state)


@app.post("/api/turn")
def start_turn():
    with _lock:
        if _state["busy"]:
            return JSONResponse({"error": "busy"}, status_code=409)
        _state["busy"] = True
        _state["status"] = "listening"
    threading.Thread(target=_run_turn, daemon=True).start()
    return {"ok": True}


@app.post("/api/reset")
def reset_order():
    global _session, _history
    with _lock:
        if _state["busy"]:
            return JSONResponse({"error": "busy"}, status_code=409)
        _session = order_session.OrderSession()
        _history = []
        _state["transcript"] = []
        _sync_order_locked()
        _state["status"] = "idle"
    return {"ok": True}


_frontend_dist = config.BASE_DIR / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
