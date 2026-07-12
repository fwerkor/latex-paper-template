#!/usr/bin/env python3
"""Generate a dependency-free GitHub Pages viewer for the latest PDF."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()

    if not args.pdf.is_file():
        raise SystemExit(f"PDF not found: {args.pdf}")

    args.output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.pdf, args.output / "paper.pdf")
    generated = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    repo_url = f"https://github.com/{args.repository}"
    commit_url = f"{repo_url}/commit/{args.sha}"
    actions_url = f"{repo_url}/actions"

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <title>{html.escape(args.title)}</title>
  <style>
    :root {{ font-family: ui-sans-serif, system-ui, sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #111827; color: #f9fafb; }}
    header {{ min-height: 56px; display: flex; gap: 12px; align-items: center; padding: 10px 16px; flex-wrap: wrap; }}
    h1 {{ margin: 0 auto 0 0; font-size: 16px; font-weight: 650; }}
    .meta {{ color: #cbd5e1; font-size: 12px; }}
    a {{ color: inherit; text-decoration: none; border: 1px solid #4b5563; border-radius: 7px; padding: 7px 10px; }}
    a:hover {{ background: #374151; }}
    object {{ display: block; width: 100%; height: calc(100vh - 76px); border: 0; background: white; }}
    .fallback {{ padding: 32px; color: #111827; }}
  </style>
</head>
<body>
  <header>
    <h1>{html.escape(args.title)}</h1>
    <span class="meta">Built from <a href="{commit_url}">{html.escape(args.sha[:7])}</a> at {generated}</span>
    <a href="paper.pdf">Open PDF</a>
    <a href="paper.pdf" download>Download</a>
    <a href="{repo_url}">Source</a>
    <a href="{actions_url}">Builds</a>
  </header>
  <object data="paper.pdf#view=FitH" type="application/pdf">
    <div class="fallback">
      PDF preview is unavailable in this browser. <a href="paper.pdf">Open or download the PDF.</a>
    </div>
  </object>
</body>
</html>
"""
    (args.output / "index.html").write_text(page, encoding="utf-8")
    (args.output / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Generated preview site in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
