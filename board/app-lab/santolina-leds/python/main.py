# Santolina: ask the student app whether the board's Wi-Fi is on and a phone is connected,
# and tell the sketch which animation to show. Standard library only.
import json
import time
import urllib.request

from arduino.app_utils import App, Bridge

MODES = {"off": 0, "waiting": 1, "connected": 2}
# The student app runs on the board itself, outside this app's container: try each way in.
URLS = ["http://127.0.0.1/api/board-state", "http://172.17.0.1/api/board-state"]

state = {"mode": None, "sent_at": 0.0, "url": URLS[0]}


def read_state():
    for url in [state["url"]] + [u for u in URLS if u != state["url"]]:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                wifi = json.loads(response.read()).get("wifi", "off")
                if url != state["url"]:
                    print("Reading the board state from", url)
                state["url"] = url
                return MODES.get(wifi, 0)
        except (OSError, ValueError):
            continue
    return 0  # student app not reachable yet (still starting): keep the matrix dark


def loop():
    mode = read_state()
    now = time.monotonic()
    # Send on every change, and again every 10 s in case the microcontroller restarted.
    if mode != state["mode"] or now - state["sent_at"] > 10:
        Bridge.call("set_mode", mode)
        if mode != state["mode"]:
            print("LED mode", mode)
        state["mode"], state["sent_at"] = mode, now
    time.sleep(1)


App.run(user_loop=loop)
