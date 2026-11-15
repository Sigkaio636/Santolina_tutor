#!/usr/bin/env bash
# Time the OCR engines (PP-OCRv4, PP-OCRv5, Tesseract) on the board's CPU, with the
# model services running as in real use. Run on the board, from ~/Santolina_tutor:
#     bash board/ocr_speed.sh --check-only   # list what is missing, run nothing
#     bash board/ocr_speed.sh                # check, then time 3 engines x 1 and 4 threads
# Setup and what to copy: docs/experiments/2026-11-tesseract-text-only.md, section Speed.
# The test images are M3Kang (research use only): delete data/interim/speed/images afterwards.
source "$(dirname "$0")/common.sh"
set +e +o pipefail

OCR_PY="${OCR_PY:-$HOME/venvs/ocr-speed/bin/python}"   # venv with rapidocr 3.10 and rapidocr_onnxruntime 1.4.4
TESS_PY="${TESS_PY:-$OCR_PY}"                           # any Python with Pillow
TESSDATA="${TESSDATA:-data/external/tessdata}"
OUT="data/interim/speed"
missing=0

step "What the test needs"
if command -v tesseract >/dev/null; then ok "$(tesseract --version 2>&1 | head -1)"
else fail "tesseract is not installed (sudo apt install tesseract-ocr)"; missing=$((missing+1)); fi
for l in eng cat spa; do
  if [ -s "$TESSDATA/$l.traineddata" ]; then ok "$TESSDATA/$l.traineddata"
  else fail "$TESSDATA/$l.traineddata is missing (copy it from the laptop)"; missing=$((missing+1)); fi
done
if [ -x "$OCR_PY" ]; then
  for m in rapidocr rapidocr_onnxruntime PIL; do
    if "$OCR_PY" -c "import $m" 2>/dev/null; then ok "$OCR_PY can import $m"
    else fail "$OCR_PY cannot import $m"; missing=$((missing+1)); fi
  done
else fail "no Python at $OCR_PY (set OCR_PY, or create the venv)"; missing=$((missing+1)); fi
n_img=$(ls "$OUT/images" 2>/dev/null | wc -l)
if [ "$n_img" -eq 100 ] && [ -s "$OUT/keys.txt" ]; then ok "100 test images and keys.txt in $OUT"
else fail "$OUT/images has $n_img files, keys.txt $( [ -s "$OUT/keys.txt" ] && echo present || echo missing ) (copy them from the laptop)"
     missing=$((missing+1)); fi

if [ "$missing" -gt 0 ]; then die "$missing item(s) missing. Nothing was timed."; fi
if [ "${1:-}" = "--check-only" ]; then echo; echo "All present. Run again without --check-only to time the engines."; exit 0; fi

step "Board state before"
start="$(date '+%Y-%m-%d %H:%M:%S')"
uname -a
systemctl is-active math-llm math-embed | paste -sd ' ' | sed 's/^/  services math-llm math-embed: /'
free -m | tee "$OUT/board-free-before.txt"

step "Timing (2 runs per engine and thread count)"
for r in 1 2; do
  for t in 1 4; do
    for e in v4 v5 tess; do
      py="$OCR_PY"; [ "$e" = tess ] && py="$TESS_PY"
      "$py" -I laptop/ocr_speed.py run --engine "$e" --threads "$t" --label board \
          --tessdata-dir "$TESSDATA" --out "$OUT/board-$e-t$t-r$r.json" || fail "$e t$t run $r failed"
    done
  done
done

step "Board state after"
free -m | tee "$OUT/board-free-after.txt"
oom=$(journalctl -k --since "$start" 2>/dev/null | grep -ci "out of memory")
if [ "$oom" -eq 0 ]; then ok "no out-of-memory kills since $start"
else fail "$oom out-of-memory line(s) since $start: journalctl -k --since '$start' | grep -i 'out of memory'"; fi
systemctl is-active math-llm math-embed | paste -sd ' ' | sed 's/^/  services math-llm math-embed: /'

step "Results"
"$TESS_PY" -I laptop/ocr_speed.py report "$OUT"/board-*.json
echo; echo "Copy $OUT/board-*.json to the laptop, then delete $OUT/images (M3Kang)."
