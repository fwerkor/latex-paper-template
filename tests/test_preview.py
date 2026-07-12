from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_preview.py"
CONFIG_READER = ROOT / "scripts" / "read_preview_config.py"


class PreviewControlsTest(unittest.TestCase):
    def run_generator(self, output: Path, *, enabled: bool, block: bool) -> None:
        pdf = output.parent / "input.pdf"
        pdf.write_bytes(b"%PDF-1.4\n% test fixture\n")
        subprocess.run(
            [
                sys.executable,
                str(GENERATOR),
                "--pdf",
                str(pdf),
                "--output",
                str(output),
                "--title",
                "Test Paper",
                "--repository",
                "owner/repository",
                "--sha",
                "0123456789abcdef",
                "--public-preview-enabled",
                str(enabled).lower(),
                "--block-search-indexing",
                str(block).lower(),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_default_configuration_enables_preview_and_blocks_indexing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            subprocess.run(
                [
                    sys.executable,
                    str(CONFIG_READER),
                    "--config",
                    str(ROOT / "preview-config.json"),
                    "--github-output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            values = dict(line.split("=", 1) for line in output.read_text().splitlines())
            self.assertEqual(values["enable_public_preview"], "true")
            self.assertEqual(values["block_search_indexing"], "true")

    def test_blocked_preview_emits_noindex_and_robots_disallow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public"
            self.run_generator(output, enabled=True, block=True)
            self.assertTrue((output / "paper.pdf").is_file())
            self.assertIn('name="robots" content="noindex', (output / "index.html").read_text())
            self.assertEqual((output / "robots.txt").read_text(), "User-agent: *\nDisallow: /\n")

    def test_indexable_preview_emits_allow_rule(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public"
            self.run_generator(output, enabled=True, block=False)
            self.assertNotIn('name="robots"', (output / "index.html").read_text())
            self.assertEqual((output / "robots.txt").read_text(), "User-agent: *\nAllow: /\n")

    def test_disabled_preview_removes_pdf_and_always_blocks_indexing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "public"
            output.mkdir()
            (output / "paper.pdf").write_bytes(b"stale")
            self.run_generator(output, enabled=False, block=False)
            self.assertFalse((output / "paper.pdf").exists())
            self.assertIn("Public preview is disabled", (output / "index.html").read_text())
            self.assertEqual((output / "robots.txt").read_text(), "User-agent: *\nDisallow: /\n")

    def test_config_reader_rejects_non_boolean_values(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "preview-config.json"
            config.write_text(
                json.dumps({"enable_public_preview": "yes", "block_search_indexing": True}),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(CONFIG_READER), "--config", str(config)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be true or false", result.stderr)


if __name__ == "__main__":
    unittest.main()
