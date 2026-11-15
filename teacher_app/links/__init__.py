"""Find the boards connected right now."""

from dataclasses import dataclass

from .adb import AdbLink, list_devices
from .base import BoardLink, LinkError
from .fake import FakeLink, discover

__all__ = ["AdbLink", "BoardLink", "Connected", "FakeLink", "LinkError", "connected", "find"]


@dataclass
class Connected:
    serial: str
    state: str  # "device" when usable; adb also reports "unauthorized", "offline"
    link: BoardLink | None


def connected(settings) -> list:
    boards = [
        Connected(serial, state, AdbLink(serial, settings.adb) if state == "device" else None)
        for serial, state in list_devices(settings.adb)
    ]
    boards += [Connected(f.serial, "device", f) for f in discover(settings.fake_boards)]
    return boards


def find(settings, serial: str):
    """The link of a connected, usable board, or None."""
    for board in connected(settings):
        if board.serial == serial and board.link is not None:
            return board.link
    return None
