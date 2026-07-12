#!/usr/bin/env bash
set -euo pipefail

mkdir -p dist
python3 scripts/check_structure.py

archive="dist/paper-source.tar.gz"
git archive --format=tar.gz --output="$archive" HEAD
cp build/paper.pdf dist/paper.pdf
sha256sum dist/paper.pdf "$archive" > dist/SHA256SUMS
printf 'Created release files in dist/\n'
