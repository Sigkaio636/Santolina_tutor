"""Is the board's Wi-Fi on, and is a phone connected to it? Read by the LED matrix app.

- "off":       the board is not running its hotspot (it holds no HOTSPOT_IP)
- "waiting":   the hotspot is on and no device is connected
- "connected": a device joined the hotspot: it answered a ping, or the student app heard
               from it, in the last CONNECTED_SECONDS

Standard library only. A background thread refreshes the state every few seconds; the
server answers GET /api/board-state with the last result.
"""

import ipaddress
from pathlib import Path
import subprocess
import threading
import time

HOTSPOT_IP = "10.42.0.1"
HOTSPOT_NET = ipaddress.ip_network("10.42.0.0/24")
CONNECTED_SECONDS = 30
REFRESH_SECONDS = 3
ARP = Path("/proc/net/arp")


def hotspot_on() -> bool:
    try:
        out = subprocess.run(
            ["ip", "-o", "-4", "addr", "show"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return False
    return f" {HOTSPOT_IP}/" in out


def hotspot_neighbours(arp_text: str) -> list:
    """IP addresses of devices on the hotspot network, from /proc/net/arp."""
    ips = []
    for line in arp_text.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 4 or parts[2] == "0x0":  # 0x0: incomplete, nobody answered
            continue
        try:
            if ipaddress.ip_address(parts[0]) in HOTSPOT_NET and parts[0] != HOTSPOT_IP:
                ips.append(parts[0])
        except ValueError:
            continue
    return ips


def answers_ping(ip: str) -> bool:
    try:
        return (
            subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip], capture_output=True, timeout=3, check=False
            ).returncode
            == 0
        )
    except (OSError, subprocess.TimeoutExpired):
        return False


class BoardState:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.last_seen: dict = {}  # ip -> monotonic time the device was last heard
        self.state = "off"
        self._lock = threading.Lock()

    def heard_from(self, ip: str) -> None:
        """The student app got a request from this address."""
        try:
            if ipaddress.ip_address(ip) in HOTSPOT_NET:
                with self._lock:
                    self.last_seen[ip] = self.clock()
        except ValueError:
            pass

    def refresh(self, on=None, neighbours=None, ping=answers_ping) -> str:
        on = hotspot_on() if on is None else on
        if not on:
            self.state = "off"
            return self.state
        if neighbours is None:
            neighbours = hotspot_neighbours(ARP.read_text()) if ARP.exists() else []
        now = self.clock()
        for ip in neighbours:
            if ping(ip):
                with self._lock:
                    self.last_seen[ip] = now
        with self._lock:
            recent = any(now - t <= CONNECTED_SECONDS for t in self.last_seen.values())
        self.state = "connected" if recent else "waiting"
        return self.state

    def run_forever(self) -> None:
        while True:
            try:
                self.refresh()
            except Exception:  # noqa: BLE001  (never let the LED status stop the server)
                self.state = "off"
            time.sleep(REFRESH_SECONDS)

    def start(self) -> "BoardState":
        threading.Thread(target=self.run_forever, daemon=True, name="board-state").start()
        return self
