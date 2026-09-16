"""Intentionally vulnerable demo program. Do not use as production code."""

from __future__ import annotations

import sys
import time
from pathlib import Path


def main() -> int:
    data = Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else sys.stdin.buffer.read()
    if data == b"CRASH":
        raise RuntimeError("demo parser crashed on CRASH token")
    if data == b"OVERFLOW":
        # A controlled stand-in for a native program's memory-safety crash.
        raise ValueError("demo size validation failure: OVERFLOW token")
    if data == b"HANG":
        time.sleep(60)
    print(f"accepted {len(data)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
