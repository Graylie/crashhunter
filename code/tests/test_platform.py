from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from code.src.crash_hunter.fuzz import InputGenerator, SEEDS
from code.src.crash_hunter.reporter import ReportWriter
from code.src.crash_hunter.runner import execute


ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "code" / "demo_target"


class CrashHunterTests(unittest.TestCase):
    def test_seed_corpus_contains_expected_crash_triggers(self) -> None:
        self.assertIn(b"CRASH", SEEDS)
        self.assertEqual(list(InputGenerator(1).cases(3)), list(SEEDS[:3]))

    def test_crash_is_recorded_once_with_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = [sys.executable, str(DEMO / "main.py"), "{input}"]
            writer = ReportWriter(root, DEMO, command)
            first = execute(1, b"CRASH", command, DEMO, "argv", 1, root / "case-1")
            second = execute(2, b"CRASH", command, DEMO, "argv", 1, root / "case-2")
            self.assertIsNotNone(writer.record(first))
            self.assertIsNone(writer.record(second))
            report = writer.finish(2)
            self.assertTrue((report / "summary.json").is_file())
            self.assertTrue((report / "bugs" / "BUG-001" / "input.bin").is_file())


if __name__ == "__main__":
    unittest.main()
