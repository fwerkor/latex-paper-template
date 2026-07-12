#!/usr/bin/env python3
"""Validate repository structure and referenced LaTeX inputs."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "paper.tex"
INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
BIB_RE = re.compile(r"\\bibliography\{([^}]+)\}")
GENERATED_SUFFIXES = {
    ".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls", ".log",
    ".out", ".run.xml", ".synctex.gz", ".toc", ".xdv",
}


def resolve_tex(base: Path, value: str) -> Path:
    candidates = [ROOT / value, base / value]
    for candidate in candidates:
        if candidate.suffix == "":
            candidate = candidate.with_suffix(".tex")
        if candidate.is_file():
            return candidate.resolve()
    candidate = candidates[0]
    if candidate.suffix == "":
        candidate = candidate.with_suffix(".tex")
    return candidate.resolve()


def walk_tex(path: Path, visited: set[Path], missing: list[Path]) -> None:
    path = path.resolve()
    if path in visited:
        return
    visited.add(path)
    if not path.is_file():
        missing.append(path)
        return

    text = path.read_text(encoding="utf-8")
    for value in INPUT_RE.findall(text):
        child = resolve_tex(path.parent, value)
        if ROOT not in child.parents and child != ROOT:
            raise SystemExit(f"Referenced path escapes repository: {child}")
        walk_tex(child, visited, missing)

    for group in BIB_RE.findall(text):
        for value in group.split(","):
            candidates = [
                (ROOT / value.strip()).with_suffix(".bib"),
                (path.parent / value.strip()).with_suffix(".bib"),
            ]
            if not any(candidate.is_file() for candidate in candidates):
                missing.append(candidates[0].resolve())


def main() -> int:
    required = [
        ENTRYPOINT,
        ROOT / "metadata.tex",
        ROOT / "references.bib",
        ROOT / "preview-config.json",
        ROOT / "README.md",
        ROOT / "LICENSE",
    ]
    missing = [path for path in required if not path.is_file()]
    visited: set[Path] = set()
    walk_tex(ENTRYPOINT, visited, missing)

    generated = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "build" in path.parts:
            continue
        if any(path.name.endswith(suffix) for suffix in GENERATED_SUFFIXES):
            generated.append(path)

    if missing or generated:
        if missing:
            print("Missing required or referenced files:")
            for path in sorted(set(missing)):
                print(f"  - {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}")
        if generated:
            print("Generated LaTeX files should not be committed:")
            for path in generated:
                print(f"  - {path.relative_to(ROOT)}")
        return 1

    print(f"Structure checks passed; traversed {len(visited)} TeX files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
