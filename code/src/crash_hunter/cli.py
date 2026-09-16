"""Command-line entry point."""

from __future__ import annotations

import argparse
import shlex
import tempfile
from pathlib import Path

from .discovery import discover_command
from .fuzz import InputGenerator
from .reporter import ReportWriter
from .runner import execute


def parser() -> argparse.ArgumentParser:
    arg = argparse.ArgumentParser(description="Dynamically test a program directory and preserve crashes.")
    arg.add_argument("--target", required=True, type=Path, help="Directory containing the program under test")
    arg.add_argument("--command", help="Launch command; use {input} for the generated input file")
    arg.add_argument("--input-mode", choices=("argv", "stdin"), default="argv")
    arg.add_argument("--iterations", type=int, default=100)
    arg.add_argument("--timeout", type=float, default=3.0)
    arg.add_argument("--seed", type=int, default=2026)
    arg.add_argument("--output", type=Path, default=Path("reports"))
    return arg


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    target = args.target.resolve()
    if not target.is_dir():
        parser().error(f"--target is not a directory: {target}")
    if args.iterations < 1 or args.timeout <= 0:
        parser().error("--iterations must be >= 1 and --timeout must be > 0")
    template = shlex.split(args.command) if args.command else discover_command(target)
    if not template:
        parser().error("--command may not be empty")
    writer = ReportWriter(args.output.resolve(), target, template)
    print(f"[CrashHunter] target={target}")
    print(f"[CrashHunter] command={template}; iterations={args.iterations}; timeout={args.timeout}s")
    # Ordinary inputs are transient. Inputs for crashes are copied into bugs/<id>/.
    with tempfile.TemporaryDirectory(prefix="crashhunter-") as temporary:
        work_dir = Path(temporary)
        for case_id, payload in enumerate(InputGenerator(args.seed).cases(args.iterations), start=1):
            result = execute(case_id, payload, template, target, args.input_mode, args.timeout, work_dir / f"case-{case_id:04d}")
            bug = writer.record(result)
            if bug:
                print(f"[BUG] {bug.bug_id}: {bug.signature}")
    report = writer.finish(args.iterations)
    print(f"[DONE] unique_bugs={len(writer.bugs)} report={report}")
    return 0
