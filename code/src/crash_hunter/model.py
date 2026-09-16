"""Data structures shared by the test runner and report writer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExecutionResult:
    case_id: int
    payload: bytes
    command: list[str]
    return_code: int | None
    timed_out: bool
    stdout: str
    stderr: str

    @property
    def crashed(self) -> bool:
        return self.timed_out or (self.return_code is not None and self.return_code != 0)

    @property
    def outcome(self) -> str:
        if self.timed_out:
            return "timeout"
        if self.return_code is None:
            return "unknown"
        if self.return_code < 0:
            return f"signal:{-self.return_code}"
        return f"exit:{self.return_code}"


@dataclass(frozen=True)
class Bug:
    bug_id: str
    signature: str
    result: ExecutionResult

    def metadata(self, target: Path) -> dict:
        data = asdict(self.result)
        data.pop("payload")
        data.update({"bug_id": self.bug_id, "signature": self.signature, "target": str(target)})
        return data
