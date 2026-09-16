"""Persistent human-readable and machine-readable bug reports."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from .model import Bug, ExecutionResult
from .runner import signature


class ReportWriter:
    def __init__(self, root: Path, target: Path, command: list[str]) -> None:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        self.root = root / stamp
        self.target = target
        self.command = command
        self.bugs: list[Bug] = []
        self._signatures: set[str] = set()

    def record(self, result: ExecutionResult) -> Bug | None:
        if not result.crashed:
            return None
        key = signature(result)
        if key in self._signatures:
            return None
        self._signatures.add(key)
        bug_id = f"BUG-{len(self.bugs) + 1:03d}"
        bug = Bug(bug_id, key, result)
        self.bugs.append(bug)
        folder = self.root / "bugs" / bug_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "input.bin").write_bytes(result.payload)
        (folder / "stdout.txt").write_text(result.stdout, encoding="utf-8")
        (folder / "stderr.txt").write_text(result.stderr, encoding="utf-8")
        metadata = bug.metadata(self.target)
        metadata["reproduction_command"] = result.command
        (folder / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return bug

    def finish(self, total_cases: int) -> Path:
        self.root.mkdir(parents=True, exist_ok=True)
        summary = {
            "target": str(self.target), "command_template": self.command,
            "executed_cases": total_cases, "unique_bugs": len(self.bugs),
            "bugs": [bug.metadata(self.target) for bug in self.bugs],
        }
        (self.root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        lines = ["# CrashHunter 测试报告", "", f"- 待测目录：`{self.target}`", f"- 执行用例：{total_cases}", f"- 唯一 bug：{len(self.bugs)}", ""]
        if not self.bugs:
            lines.append("本次未观察到崩溃；这不代表程序不存在缺陷。")
        for bug in self.bugs:
            digest = hashlib.sha256(bug.result.payload).hexdigest()[:12]
            lines.extend([f"## {bug.bug_id}", "", f"- 类型：`{bug.result.outcome}`", f"- 输入 SHA-256 前缀：`{digest}`", f"- 签名：`{bug.signature}`", f"- 复现证据：`bugs/{bug.bug_id}/`", ""])
        (self.root / "report.md").write_text("\n".join(lines), encoding="utf-8")
        return self.root
