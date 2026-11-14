#!/usr/bin/env bash
# Install MinerU the way this project declares it: the `ocr` dependency group
# in pyproject.toml (mineru[core]==3.4.5). Run it yourself: it pulls PyTorch and
# other large wheels into .venv (several GB). It does not touch other projects.
# The pipeline models are expected in models/mineru-home (git-ignored, ~1.6 GB).
# Usage: install_mineru.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
cd "$ROOT"

command -v uv >/dev/null 2>&1 || { echo "uv is required: https://docs.astral.sh/uv/" >&2; exit 1; }

uv sync --group ocr

if [ ! -d models/mineru-home/pipeline/models ]; then
  echo "Models not found in models/mineru-home." >&2
  echo "Download them: MINERU_TOOLS_CONFIG_JSON=\$PWD/models/mineru-home/mineru.json .venv/bin/mineru-models-download -s huggingface -m pipeline" >&2
  exit 1
fi

.venv/bin/mineru --version
echo "MinerU ready. Test: bash $(dirname "$0")/mineru_parse.sh paper.pdf"
