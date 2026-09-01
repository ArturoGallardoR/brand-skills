from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAND = ROOT / "skills" / "brand-init" / "scripts" / "brand.py"
AVAIL = ROOT / "skills" / "naming" / "scripts" / "check_availability.py"
VALIDATE = ROOT / "scripts" / "validate_skills.py"


class CrossPlatformScriptTests(unittest.TestCase):
    def run_cmd(self, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *map(str, args)],
            cwd=cwd or ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_brand_init_list_and_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            result = self.run_cmd(
                BRAND,
                "init",
                "--name",
                "Cafe Mexico",
                "--one-liner",
                "Tools for makers",
                "--out",
                "brands/cafe-mexico",
                "--date",
                "2026-09-01",
                "--register",
                "brands/registry.yaml",
                cwd=work,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = work / "brands" / "cafe-mexico" / "brand.yaml"
            self.assertTrue(manifest.exists())
            self.assertIn("slug: cafe-mexico", manifest.read_text(encoding="utf-8"))

            result = self.run_cmd(
                BRAND,
                "set",
                "--package",
                "brands/cafe-mexico",
                "--key",
                "one_liner",
                "--value",
                "Better tools for makers",
                cwd=work,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("one_liner: Better tools for makers", manifest.read_text(encoding="utf-8"))

            result = self.run_cmd(BRAND, "list", "--registry", "brands/registry.yaml", cwd=work)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("cafe-mexico", result.stdout)

    def test_brand_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            first = self.run_cmd(BRAND, "init", "--name", "Acme", "--out", "brand", cwd=work)
            second = self.run_cmd(BRAND, "init", "--name", "Acme", "--out", "brand", cwd=work)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refusing to overwrite", second.stderr)

    def test_availability_cli_parses_without_network(self) -> None:
        result = self.run_cmd(AVAIL, "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("availability", result.stdout.lower())

    def test_repo_validator(self) -> None:
        result = self.run_cmd(VALIDATE)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
