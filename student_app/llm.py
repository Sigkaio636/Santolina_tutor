"""A streaming client for the tutor model (a llama.cpp server). Standard library only.

The server runs the fine-tuned tutor (board/systemd/math-tutor.service, port 8084). Set
SANTOLINA_TUTOR_URL to point somewhere else, e.g. http://127.0.0.1:8095 on a laptop.

`THINKING` counts the tokens of the call in progress, so the LED matrix can fill its
"thinking" bar with real progress (GET /api/board-state).
"""

import json
import os
import threading
import time
import urllib.request

URL = os.environ.get("SANTOLINA_TUTOR_URL", "http://127.0.0.1:8084").rstrip("/")
SEED = 42


class Thinking:
    """The model call in progress: None, or how many tokens arrived out of how many."""

    def __init__(self):
        self._lock = threading.Lock()
        self._now = None

    def start(self, max_tokens: int):
        with self._lock:
            self._now = {"tokens": 0, "max": max_tokens}

    def token(self):
        with self._lock:
            if self._now is not None:
                self._now["tokens"] += 1

    def stop(self):
        with self._lock:
            self._now = None

    def state(self):
        with self._lock:
            return dict(self._now) if self._now else None


THINKING = Thinking()


def chat(
    messages: list, max_tokens: int = 80, timeout: float = 90, url: str | None = None
) -> dict:
    """One streamed chat completion. Returns {"text", "tokens", "prompt_tokens", "seconds",
    "first_token_seconds"}. Raises OSError or ValueError when the server is not usable."""
    payload = {
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0,
        "seed": SEED,
        "cache_prompt": True,
        "stream": True,
        # The tutor was fine-tuned to answer directly: a thinking phase only costs time
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = urllib.request.Request(
        f"{url or URL}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    start = time.monotonic()
    first = None
    parts, timings = [], {}
    THINKING.start(max_tokens)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            for raw in response:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                timings = chunk.get("timings") or timings
                for choice in chunk.get("choices") or []:
                    piece = (choice.get("delta") or {}).get("content")
                    if piece:
                        if first is None:
                            first = time.monotonic() - start
                        parts.append(piece)
                        THINKING.token()
    finally:
        THINKING.stop()
    return {
        "text": "".join(parts).strip(),
        "tokens": timings.get("predicted_n", len(parts)),
        "prompt_tokens": timings.get("prompt_n"),
        "seconds": round(time.monotonic() - start, 2),
        "first_token_seconds": round(first, 2) if first is not None else None,
    }
