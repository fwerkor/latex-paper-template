#!/usr/bin/env python3
"""Generate a dependency-free GitHub Pages viewer for the latest PDF."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import shutil
from pathlib import Path


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--public-preview-enabled", required=True, type=parse_bool)
    parser.add_argument("--block-search-indexing", required=True, type=parse_bool)
    args = parser.parse_args()

    if args.public_preview_enabled and (args.pdf is None or not args.pdf.is_file()):
        raise SystemExit(f"PDF not found: {args.pdf}")

    if args.output.exists():
        shutil.rmtree(args.output)
    args.output.mkdir(parents=True, exist_ok=True)

    generated = dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()
    repo_url = f"https://github.com/{args.repository}"
    commit_url = f"{repo_url}/commit/{args.sha}"
    actions_url = f"{repo_url}/actions"
    effective_block_indexing = args.block_search_indexing or not args.public_preview_enabled
    robots_meta = (
        '  <meta name="robots" content="noindex, nofollow, noarchive, nosnippet, noimageindex">\n'
        '  <meta name="googlebot" content="noindex, nofollow, noarchive, nosnippet, noimageindex">\n'
        if effective_block_indexing
        else ""
    )

    if args.public_preview_enabled:
        assert args.pdf is not None
        shutil.copy2(args.pdf, args.output / "paper.pdf")
        viewer = """  <object data="paper.pdf#view=FitH" type="application/pdf">
    <div class="fallback">
      PDF preview is unavailable in this browser. <a href="paper.pdf">Open or download the PDF.</a>
    </div>
  </object>"""
        controls = """    <a href="paper.pdf">Open PDF</a>
    <a href="paper.pdf" download>Download</a>"""
        heading = html.escape(args.title)
    else:
        viewer = """  <main class="disabled">
    <h2>Public preview is disabled</h2>
    <p>The paper is still compiled by CI, but it is not included in this public Pages deployment.</p>
  </main>"""
        controls = ""
        heading = "Public preview disabled"

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
{robots_meta}  <title>{heading}</title>
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
    .disabled {{ max-width: 680px; margin: 15vh auto; padding: 32px; line-height: 1.6; }}
  </style>
</head>
<body>
  <header>
    <h1>{heading}</h1>
    <span class="meta">Built from <a href="{commit_url}">{html.escape(args.sha[:7])}</a> at {generated}</span>
{controls}
    <a href="{repo_url}">Source</a>
    <a href="{actions_url}">Builds</a>
  </header>
{viewer}
</body>
</html>
"""
    (args.output / "index.html").write_text(page, encoding="utf-8")
    robots = "User-agent: *\nDisallow: /\n" if effective_block_indexing else "User-agent: *\nAllow: /\n"
    (args.output / "robots.txt").write_text(robots, encoding="utf-8")
    (args.output / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Generated preview site in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
