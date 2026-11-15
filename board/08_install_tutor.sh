#!/usr/bin/env bash
# Run the fine-tuned tutor model as math-tutor.service (port TUTOR_PORT), for the student
# app's chat and clues. The model is not downloadable: copy it from the laptop first:
#   adb push qwen35-tutor-Q8_0.gguf /home/arduino/models/
# Run it once per board, with sudo rights, and again whenever you change config.env.
source "$(dirname "$0")/common.sh"
TUTOR_PATH="$MODELS_DIR/$TUTOR_FILE"

[ -x "$LLAMA_SERVER" ] || die "llama-server not found. Run ./board/02_build_llama_cpp.sh first."
[ -f "$TUTOR_PATH" ] || die "$TUTOR_PATH not found. Copy it from the laptop: adb push $TUTOR_FILE $MODELS_DIR/"

service_pid="$(systemctl show -p MainPID --value math-tutor 2>/dev/null || true)"
by_hand="$(pgrep -f -- "llama-server.*--port $TUTOR_PORT" | grep -vx "${service_pid:-0}" | tr '\n' ' ' || true)"
if [ -n "${by_hand// /}" ]; then
  die "a llama-server you started by hand is using port $TUTOR_PORT. Stop it with: kill $by_hand"
fi

step "Installing math-tutor.service"
sed -e "s|@USER@|$USER|g" -e "s|@LLAMA_SERVER@|$LLAMA_SERVER|g" \
    -e "s|@TUTOR_PATH@|$TUTOR_PATH|g" -e "s|@TUTOR_PORT@|$TUTOR_PORT|g" \
    -e "s|@TUTOR_THREADS@|$TUTOR_THREADS|g" -e "s|@TUTOR_CTX@|$TUTOR_CTX|g" \
    "$REPO_DIR/board/systemd/math-tutor.service" | sudo tee /etc/systemd/system/math-tutor.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable math-tutor
sudo systemctl restart math-tutor
wait_for_health "$TUTOR_PORT" 180 || die "the tutor server didn't start. See: journalctl -u math-tutor -n 50"
ok "tutor model answers on port $TUTOR_PORT"

step "Asking it for one clue"
curl -sf "http://127.0.0.1:$TUTOR_PORT/v1/chat/completions" -H 'Content-Type: application/json' -d '{
  "messages": [{"role": "system", "content": "You are a Socratic math tutor. Reply in Catalan."},
               {"role": "user", "content": "Un llapis costa 3 euros. En compro 4 i pago amb 20 euros. Quant em tornen?\nNo sé com començar."}],
  "max_tokens": 60, "temperature": 0, "chat_template_kwargs": {"enable_thinking": false}}' \
  | python3 -c '
import json, sys
r = json.load(sys.stdin)
t = r["timings"]
print("  ", r["choices"][0]["message"]["content"])
print("   %d prompt tokens in %.1f s, %d tokens in %.1f s"
      % (t["prompt_n"], t["prompt_ms"] / 1000, t["predicted_n"], t["predicted_ms"] / 1000))' \
  || die "the tutor server did not answer a chat request"
