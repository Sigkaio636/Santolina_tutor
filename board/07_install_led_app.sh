#!/usr/bin/env bash
# Show the board's Wi-Fi status on the LED matrix: Wi-Fi waves while it waits for a phone,
# a bouncing check mark once a phone is connected. Installs the App Lab app
# board/app-lab/santolina-leds and makes it start at every boot. No sudo needed.
# The first start downloads App Lab's Python image, so run it while the board has internet
# (on a normal Wi-Fi, not its own hotspot). Needs the student app (06) to report the state.
source "$(dirname "$0")/common.sh"

APP_DIR="$HOME/ArduinoApps/santolina-leds"

step "Copying the LED app to $APP_DIR"
mkdir -p "$APP_DIR"
cp -r "$REPO_DIR/board/app-lab/santolina-leds/." "$APP_DIR/"
ok "copied"

step "Starting it (compiles the sketch and loads it on the microcontroller; minutes the first time)"
arduino-app-cli app start user:santolina-leds || die "the app didn't start. See: arduino-app-cli app logs $APP_DIR --all"
ok "running"

step "Starting it at every boot"
arduino-app-cli properties set default user:santolina-leds
ok "$(arduino-app-cli properties get default)"
