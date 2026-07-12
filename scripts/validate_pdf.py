#!/usr/bin/env python3
"""Perform lightweight integrity checks on the generated PDF."""

from __future__ import annotations

import argparse
from pathlib import Path

from pypdf import PdfReader


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")
    if args.pdf.stat().st_size < 10_000:
        raise SystemExit(f"PDF is unexpectedly small: {args.pdf.stat().st_size} bytes")
    if args.pdf.read_bytes()[:5] != b"%PDF-":
        raise SystemExit("Output does not have a PDF header")

    reader = PdfReader(str(args.pdf))
    pages = len(reader.pages)
    if pages < 1:
        raise SystemExit("PDF contains no pages")
    if reader.is_encrypted:
        raise SystemExit("PDF must not be encrypted")

    metadata = reader.metadata or {}
    title = str(metadata.get("/Title", "")).strip()
    if not title:
        raise SystemExit("PDF title metadata is empty")

    print(
        f"PDF checks passed: pages={pages}, bytes={args.pdf.stat().st_size}, "
        f"title={title!r}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
