#!/usr/bin/env bash
# Run the student interface at boot, and make phones open it when they join the board's Wi-Fi.
# Run it once per board, with sudo rights. The teacher app creates the Wi-Fi itself (setup) and
# updates the student app's code every time the board is plugged in.
source "$(dirname "$0")/common.sh"

SANTOLINA="$HOME/santolina"
LIB="$SANTOLINA/lib"
CAPTIVE_CONF=/etc/NetworkManager/dnsmasq-shared.d/santolina-captive.conf

step "Checking the student app code"
if [ ! -f "$LIB/student_app/server.py" ]; then
  # Not set up by the teacher app yet: start from this repository's copy
  mkdir -p "$LIB"
  cp -r "$REPO_DIR/classroom" "$REPO_DIR/student_app" "$LIB/"
  find "$LIB" -name __pycache__ -prune -exec rm -rf {} +
  warn "copied from $REPO_DIR; the teacher app replaces it at setup"
fi
ok "$LIB/student_app"
python3 -c "import sys; sys.path.insert(0, '$LIB'); import student_app.server" \
  || die "the student app doesn't import with this Python"

step "Captive portal: every web address on the board's Wi-Fi leads to the board"
# NetworkManager reads this only for shared connections (the hotspot), not for normal Wi-Fi
echo "address=/#/10.42.0.1" | sudo tee "$CAPTIVE_CONF" >/dev/null
ok "$CAPTIVE_CONF"

step "Installing santolina-student.service"
sed -e "s|@USER@|$USER|g" -e "s|@HOME@|$HOME|g" "$REPO_DIR/board/systemd/santolina-student.service" \
  | sudo tee /etc/systemd/system/santolina-student.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable santolina-student
sudo systemctl restart santolina-student

for _ in $(seq 20); do
  if curl -sf http://127.0.0.1/api/info >/dev/null 2>&1; then break; fi
  sleep 1
done
curl -sf http://127.0.0.1/api/info >/dev/null || die "the student app didn't start. See: journalctl -u santolina-student -n 50"
ok "student app answers on port 80"

if nmcli -t -f NAME connection show | grep -qx santolina-hotspot; then
  ok "the board's Wi-Fi is configured; it starts at the next boot"
else
  warn "no Wi-Fi hotspot yet: set the board up in the teacher app, then restart the board"
fi
