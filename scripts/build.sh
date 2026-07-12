#!/usr/bin/env bash
set -euo pipefail

root_file="${ROOT_FILE:-paper.tex}"
out_dir="${OUT_DIR:-build}"

mkdir -p "$out_dir"
latexmk \
  -pdf \
  -file-line-error \
  -halt-on-error \
  -interaction=nonstopmode \
  -synctex=1 \
  -outdir="$out_dir" \
  "$root_file"

python3 scripts/check_log.py "$out_dir/${root_file%.tex}.log"
