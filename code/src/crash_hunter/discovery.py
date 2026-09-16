"""Conservative program discovery; explicit --command always wins."""

from __future__ import annotations

import os
import sys
from pathlib import Path


PREFERRED_PYTHON_NAMES = ("main.py", "app.py", "target.py")


def discover_command(target: Path) -> list[str]:
    """Return a launch command ending in the literal `{input}` placeholder."""
    for name in PREFERRED_PYTHON_NAMES:
        candidate = target / name
        if candidate.is_file():
            return [sys.executable, str(candidate), "{input}"]

    python_files = sorted(path for path in target.glob("*.py") if not path.name.startswith("test_"))
    if len(python_files) == 1:
        return [sys.executable, str(python_files[0]), "{input}"]

    if os.name == "nt":
        executables = sorted(path for path in target.iterdir() if path.is_file() and path.suffix.lower() == ".exe")
    else:
        executables = sorted(path for path in target.iterdir() if path.is_file() and os.access(path, os.X_OK))
    if len(executables) == 1:
        return [str(executables[0]), "{input}"]

    raise ValueError(
        "Cannot identify one runnable program. Supply --command, for example: "
        '--command "python app.py --file {input}".'
    )
