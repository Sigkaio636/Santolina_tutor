# Santolina: ask the student app whether the board's Wi-Fi is on and a phone is connected,
# and whether the tutor model is writing, and tell the sketch what to show. Standard library only.
import json
import time
import urllib.request

from arduino.app_utils import App, Bridge

MODES = {"off": 0, "waiting": 1, "connected": 2}
LEDS = 104  # 8 x 13
# The student app runs on the board itself, outside this app's container: try each way in.
URLS = ["http://127.0.0.1/api/board-state", "http://172.17.0.1/api/board-state"]

state = {"mode": None, "sent_at": 0.0, "url": URLS[0], "leds": -1, "full_until": 0.0}


def read_state():
    """(mode, thinking): thinking is None, or {"tokens", "max"} while the tutor writes."""
    for url in [state["url"]] + [u for u in URLS if u != state["url"]]:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                data = json.loads(response.read())
                if url != state["url"]:
                    print("Reading the board state from", url)
                state["url"] = url
                return MODES.get(data.get("wifi", "off"), 0), data.get("thinking")
        except (OSError, ValueError):
            continue
    return 0, None  # student app not reachable yet (still starting): keep the matrix dark


def thinking_leds(thinking):
    """One LED per token; with more than 104 tokens expected, one LED per max/104 tokens."""
    tokens, most = thinking.get("tokens", 0), max(thinking.get("max", LEDS), 1)
    return min(LEDS, tokens if most <= LEDS else tokens * LEDS // most)


def loop():
    mode, thinking = read_state()
    now = time.monotonic()
    if thinking is not None:
        leds = thinking_leds(thinking)
        state["full_until"] = now + 0.5
    elif state["leds"] >= 0 and now < state["full_until"]:
        leds = LEDS  # the reply is done: fill the bar for a moment, then back
    else:
        leds = -1
    if leds != state["leds"]:
        Bridge.call("set_thinking", leds)
        state["leds"] = leds
    # Send on every change, and again every 10 s in case the microcontroller restarted.
    if mode != state["mode"] or now - state["sent_at"] > 10:
        Bridge.call("set_mode", mode)
        Bridge.call("set_thinking", state["leds"])
        if mode != state["mode"]:
            print("LED mode", mode)
        state["mode"], state["sent_at"] = mode, now
    time.sleep(0.25 if leds >= 0 else 1)  # at most every 250 ms, as the design asks


App.run(user_loop=loop)
