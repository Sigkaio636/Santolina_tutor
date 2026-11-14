#!/usr/bin/env bash
# Convert one or more paper PDFs to Markdown with MinerU.
#
# Usage:  mineru_parse.sh paper.pdf [more.pdf ...]
# Env:    PAPER_OUT  output root (default: <pdf dir>/parsed)
#         TIER       MinerU 4.x tier (default: standard); ignored by 3.x
# Output: <PAPER_OUT>/<name>/.../<name>.md  (the path is printed on stdout)
# Exit:   0 ok, 1 bad input or MinerU failure, 2 MinerU is not installed.
# Skips a paper whose .md already exists. Installs nothing: see install_mineru.sh.
#
# MinerU lookup: project env (.venv/bin/mineru, from `uv sync --group ocr`),
# then PATH. The project pins MinerU 3.x and keeps its models in
# models/mineru-home, so this script points MinerU at them when they exist.
# MinerU 4.x (`mineru parse`) is used if that is what is found.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
TIER="${TIER:-standard}"

if [ "$#" -eq 0 ]; then
  echo "usage: $0 paper.pdf [more.pdf ...]" >&2
  exit 1
fi

if [ -x "$ROOT/.venv/bin/mineru" ]; then
  bin="$ROOT/.venv/bin/mineru"
elif command -v mineru >/dev/null 2>&1; then
  bin="$(command -v mineru)"
else
  echo "MinerU is not installed. Run: bash $(dirname "$0")/install_mineru.sh" >&2
  exit 2
fi

# Use the project's local models (no download at run time) when present.
if [ -f "$ROOT/models/mineru-home/mineru.json" ]; then
  export MINERU_TOOLS_CONFIG_JSON="$ROOT/models/mineru-home/mineru.json"
  export MINERU_MODEL_SOURCE=local
fi

major=""   # looked up on first use: `--version` imports torch (~5 s)

status=0
for pdf in "$@"; do
  if [ ! -s "$pdf" ] || ! head -c4 "$pdf" | grep -q '%PDF'; then
    echo "SKIP not a PDF: $pdf" >&2; status=1; continue
  fi
  name="$(basename "${pdf%.*}")"
  out="${PAPER_OUT:-$(dirname "$pdf")/parsed}/$name"
  md="$(find "$out" -name '*.md' -size +0 2>/dev/null | head -1 || true)"
  if [ -n "$md" ]; then
    echo "$md"; continue
  fi
  mkdir -p "$out"
  if [ -z "$major" ]; then
    major="$("$bin" --version 2>/dev/null | grep -oE '[0-9]+' | head -1 || true)"
    major="${major:-3}"
  fi
  if [ "$major" -ge 4 ]; then
    "$bin" parse "$pdf" --pages all -o "$out/$name.md" --wait 600 >&2 || true
  else
    "$bin" -p "$pdf" -o "$out" -b pipeline >&2 || true
  fi
  md="$(find "$out" -name '*.md' -size +0 2>/dev/null | head -1 || true)"
  if [ -n "$md" ]; then
    echo "$md"
  else
    echo "FAIL $pdf" >&2; status=1
  fi
done
exit "$status"
