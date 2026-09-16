"""Subprocess execution with timeout and crash signature generation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .model import ExecutionResult


def build_command(template: list[str], input_path: Path) -> list[str]:
    return [part.replace("{input}", str(input_path)) for part in template]


def execute(
    case_id: int, payload: bytes, template: list[str], target: Path, input_mode: str, timeout: float, case_dir: Path
) -> ExecutionResult:
    case_dir.mkdir(parents=True, exist_ok=True)
    input_path = case_dir / "input.bin"
    input_path.write_bytes(payload)
    command = build_command(template, input_path)
    stdin = payload if input_mode == "stdin" else None
    try:
        completed = subprocess.run(
            command,
            cwd=target,
            input=stdin,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return ExecutionResult(
            case_id, payload, command, completed.returncode, False,
            completed.stdout.decode("utf-8", errors="replace"),
            completed.stderr.decode("utf-8", errors="replace"),
        )
    except subprocess.TimeoutExpired as error:
        return ExecutionResult(
            case_id, payload, command, None, True,
            (error.stdout or b"").decode("utf-8", errors="replace"),
            (error.stderr or b"").decode("utf-8", errors="replace"),
        )
    except OSError as error:
        return ExecutionResult(case_id, payload, command, 127, False, "", f"launcher error: {error}")


def signature(result: ExecutionResult) -> str:
    """Normalize volatile details so identical crashes become one bug."""
    text = result.stderr.strip() or result.stdout.strip()
    text = re.sub(r"[A-Za-z]:\\[^\n:]+", "<path>", text)
    text = re.sub(r"/[^\s:]+", "<path>", text)
    text = re.sub(r"\b\d+\b", "#", text)
    compact = " ".join(text.split())[:240]
    return f"{result.outcome}|{compact or '<no diagnostic output>'}"
