import json
import threading
import urllib.request

from student_app.board_state import CONNECTED_SECONDS, BoardState, hotspot_neighbours
from student_app.server import make_server

ARP = """IP address       HW type     Flags       HW address            Mask     Device
10.42.0.233      0x1         0x2         ba:e4:56:ae:86:ed     *        wlan0
10.42.0.50       0x1         0x0         00:00:00:00:00:00     *        wlan0
192.168.9.1      0x1         0x2         aa:bb:cc:dd:ee:ff     *        wlan0
"""


def test_neighbours_are_complete_entries_on_the_hotspot_network():
    assert hotspot_neighbours(ARP) == ["10.42.0.233"]


def test_states():
    now = [1000.0]
    s = BoardState(clock=lambda: now[0])
    assert s.refresh(on=False) == "off"
    assert s.refresh(on=True, neighbours=[], ping=lambda ip: False) == "waiting"
    assert s.refresh(on=True, neighbours=["10.42.0.233"], ping=lambda ip: True) == "connected"
    now[0] += CONNECTED_SECONDS + 1  # the phone left and stopped answering
    assert s.refresh(on=True, neighbours=["10.42.0.233"], ping=lambda ip: False) == "waiting"
    s.heard_from("10.42.0.240")  # the page talked to the student app
    assert s.refresh(on=True, neighbours=[], ping=lambda ip: False) == "connected"
    s.heard_from("192.168.9.5")  # not a hotspot address: ignored
    now[0] += CONNECTED_SECONDS + 1
    assert s.refresh(on=True, neighbours=[], ping=lambda ip: False) == "waiting"


def test_endpoint_answers_any_host_despite_the_captive_portal(tmp_path):
    state = BoardState()
    state.state = "waiting"
    srv = make_server(tmp_path, "127.0.0.1", 0, public_host="10.42.0.1", board_state=state)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{srv.server_address[1]}/api/board-state",
            headers={"Host": "172.17.0.1"},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            assert json.loads(r.read()) == {"wifi": "waiting", "thinking": None}
    finally:
        srv.shutdown()
        srv.server_close()
