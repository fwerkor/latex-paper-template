#!/usr/bin/env python3
"""Validate preview-config.json and expose normalized boolean values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_KEYS = {"enable_public_preview", "block_search_indexing"}


def load_config(path: Path) -> dict[str, bool]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Preview configuration not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise SystemExit(f"Preview configuration must be a JSON object: {path}")

    missing = EXPECTED_KEYS - raw.keys()
    unknown = raw.keys() - EXPECTED_KEYS
    if missing:
        raise SystemExit(f"Missing preview configuration keys: {', '.join(sorted(missing))}")
    if unknown:
        raise SystemExit(f"Unknown preview configuration keys: {', '.join(sorted(unknown))}")

    for key in sorted(EXPECTED_KEYS):
        if not isinstance(raw[key], bool):
            raise SystemExit(f"Preview configuration value {key!r} must be true or false")

    return {key: raw[key] for key in EXPECTED_KEYS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("preview-config.json"))
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    config = load_config(args.config)
    lines = [f"{key}={str(config[key]).lower()}" for key in sorted(EXPECTED_KEYS)]
    text = "\n".join(lines) + "\n"

    if args.github_output is not None:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
