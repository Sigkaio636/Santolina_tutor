"""The board's own Wi-Fi, which the students' phones join, and its printable sticker."""

import io
import json
import re
import secrets
import unicodedata

from classroom import paths
from classroom.schemas import Hotspot, from_dict, to_dict

# Easy to read on a sticker and to type on a laptop: no 0/o, 1/l/i.
PASSWORD_ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"
PASSWORD_LENGTH = 10
ADDRESS = "http://10.42.0.1"


def make_ssid(board_name: str) -> str:
    plain = unicodedata.normalize("NFKD", board_name).encode("ascii", "ignore").decode()
    plain = re.sub(r"[^A-Za-z0-9]+", "-", plain).strip("-") or "Board"
    return ("Santolina-" + plain)[:32]


def new_password() -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))


def read(link) -> Hotspot | None:
    try:
        text = link.read_text(paths.HOTSPOT)
        return from_dict(Hotspot, json.loads(text)) if text else None
    except (ValueError, TypeError):
        return None


def ensure(link, board_name: str) -> tuple:
    """Create or update the hotspot. Keeps the old password, so a printed sticker stays valid.

    Returns (Hotspot, message).
    """
    old = read(link)
    hotspot = Hotspot(ssid=make_ssid(board_name), password=old.password if old else new_password())
    hotspot.check()
    message = link.configure_hotspot(hotspot.ssid, hotspot.password)
    link.write_text(paths.HOTSPOT, json.dumps(to_dict(hotspot), indent=2))
    return hotspot, message


def wifi_qr_payload(ssid: str, password: str) -> str:
    """The text phones read to join a Wi-Fi network from a QR code."""

    def esc(value):
        return re.sub(r'([\\;,:"])', r"\\\1", value)

    return f"WIFI:T:WPA;S:{esc(ssid)};P:{esc(password)};;"


def qr_svg(data: str, scale: int = 6) -> str:
    import segno  # teacher group only; the board never needs it

    out = io.BytesIO()
    segno.make(data, error="m").save(out, kind="svg", scale=scale, border=2, xmldecl=False)
    return out.getvalue().decode()
