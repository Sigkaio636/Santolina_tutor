#!/usr/bin/env bash
# Download the PDFs listed in papers.tsv (category, arXiv ID, short name) from arXiv.
# PDFs are git-ignored; run this once after cloning. Skips files that already exist.
set -euo pipefail
cd "$(dirname "$0")"
while IFS=$'\t' read -r cat id slug; do
  mkdir -p "$cat"; out="$cat/${slug}_${id}.pdf"
  if [ -s "$out" ] && head -c4 "$out" | grep -q '%PDF'; then continue; fi
  if curl -sSfL -o "$out" "https://arxiv.org/pdf/$id" && head -c4 "$out" | grep -q '%PDF'; then
    echo "OK   $id"
  else
    echo "FAIL $id"; rm -f "$out"
  fi
  sleep 3  # be polite to arXiv
done < papers.tsv
