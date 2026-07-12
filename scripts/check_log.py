#!/usr/bin/env python3
"""Fail CI on unresolved references, citations, or severe LaTeX diagnostics."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = {
    "undefined references": re.compile(r"LaTeX Warning: There were undefined references"),
    "undefined citations": re.compile(r"LaTeX Warning: There were undefined citations"),
    "missing citation": re.compile(r"Citation [`'][^`']+['`] on page .* undefined"),
    "missing reference": re.compile(r"Reference [`'][^`']+['`] on page .* undefined"),
    "multiply defined labels": re.compile(r"multiply defined"),
    "missing file": re.compile(r"LaTeX Error: File [`'][^`']+['`] not found"),
    "fatal error": re.compile(r"Fatal error occurred"),
    "emergency stop": re.compile(r"Emergency stop"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument(
        "--fail-on-overfull",
        action="store_true",
        help="also fail on overfull boxes",
    )
    args = parser.parse_args()

    if not args.log.is_file():
        raise SystemExit(f"LaTeX log not found: {args.log}")

    text = args.log.read_text(encoding="utf-8", errors="replace")
    failures: list[str] = []
    for name, pattern in PATTERNS.items():
        if pattern.search(text):
            failures.append(name)

    if args.fail_on_overfull and "Overfull \\hbox" in text:
        failures.append("overfull horizontal box")

    if failures:
        print("LaTeX quality checks failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    overfull = text.count("Overfull \\hbox")
    underfull = text.count("Underfull \\hbox")
    print(f"LaTeX log checks passed (overfull={overfull}, underfull={underfull}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
