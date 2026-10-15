"""Execute explicit UI steps using fresh Android hierarchy observations."""
from __future__ import annotations

import json
import re
import shlex
import time
import xml.etree.ElementTree as ET
from pathlib import Path


def match_node(root: ET.Element, selector: dict) -> ET.Element | None:
    if not selector or any(k not in {"text", "resource-id", "content-desc", "class"} for k in selector):
        raise ValueError(f"Invalid UI selector: {selector}")
    matches = [n for n in root.iter("node") if all(n.get(k) == v for k, v in selector.items())
               and n.get("enabled") != "false"]
    if len(matches) > 1:
        raise RuntimeError(f"Ambiguous selector ({len(matches)} matches): {selector}")
    return matches[0] if matches else None


def center(node: ET.Element) -> tuple[int, int]:
    bounds = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
    if not bounds:
        raise RuntimeError("Missing UI bounds")
    x1, y1, x2, y2 = map(int, bounds.groups())
    if x1 >= x2 or y1 >= y2:
        raise RuntimeError("UI node is not visible")
    return (x1 + x2) // 2, (y1 + y2) // 2


def execute_scenario(device, scenario: dict, output: Path) -> list[dict]:
    records = []
    (output / "scenario.json").write_text(json.dumps(scenario, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        for index, step in enumerate(scenario["steps"], 1):
            action = step["action"]
            record = {"step": index, "label": step.get("label", action), "action": action, "status": "running"}
            records.append(record)
            print(f"[STEP {index}] {record['label']}", flush=True)
            try:
                if action == "wait":
                    seconds = float(step.get("seconds", 1))
                    if not 0 <= seconds <= 30:
                        raise ValueError("A wait step must be between 0 and 30 seconds")
                    time.sleep(seconds)
                elif action == "key":
                    key = step["key"]
                    if key not in {"KEYCODE_BACK", "KEYCODE_ENTER"}:
                        raise ValueError("Only Back and Enter navigation keys are supported")
                    device.run("shell", "input", "keyevent", key)
                else:
                    remote = "/sdcard/crashhunter-scenario.xml"
                    device.run("shell", "uiautomator", "dump", remote, timeout=30)
                    xml = device.run("shell", "cat", remote)
                    (output / f"step-{index:02d}-before.xml").write_text(xml, encoding="utf-8")
                    root = ET.fromstring(xml)
                    if step.get("guard") and match_node(root, step["guard"]) is None:
                        if not step.get("optional"):
                            raise RuntimeError("Step guard does not match the current page")
                        record["status"] = "skipped"
                        continue
                    node = match_node(root, step.get("selector", {}))
                    record["selector"] = step.get("selector")
                    if node is None:
                        if step.get("optional"):
                            record["status"] = "skipped"
                            continue
                        raise RuntimeError(f"UI control not found: {step.get('selector')}")
                    record["observed"] = dict(node.attrib)
                    x, y = center(node)
                    if action == "tap":
                        device.run("shell", "input", "tap", str(x), str(y))
                    elif action == "set_checked":
                        parents = {child: parent for parent in root.iter() for child in parent}
                        row = node
                        checkboxes = []
                        while row is not None:
                            checkboxes = [n for n in row.iter("node") if n.get("checkable") == "true"]
                            if checkboxes:
                                break
                            row = parents.get(row)
                        if len(checkboxes) != 1:
                            raise RuntimeError("Cannot uniquely identify the selected setting's switch")
                        record["previous_checked"] = checkboxes[0].get("checked") == "true"
                        if record["previous_checked"] != bool(step["checked"]):
                            device.run("shell", "input", "tap", str(x), str(y))
                    elif action == "set_text":
                        value = str(step["value"])
                        if not re.fullmatch(r"[A-Za-z0-9._:/@%+= -]{0,500}", value):
                            raise ValueError("ADB text entry currently supports simple ASCII strings")
                        old = node.get("text", "")
                        if len(old) > 1000:
                            raise ValueError("Existing field text is too long")
                        device.run("shell", "input", "tap", str(x), str(y))
                        device.run("shell", "input", "keyevent", "KEYCODE_MOVE_END", *(["KEYCODE_DEL"] * len(old)))
                        if value:
                            device.run("shell", "input", "text", shlex.quote(value.replace(" ", "%s")))
                        record["value"] = value
                    elif action != "assert_exists":
                        raise ValueError(f"Unsupported UI action: {action}")
                time.sleep(0.6)
                device.screenshot(output / f"step-{index:02d}-after.png")
                record["status"] = "completed"
            except Exception as error:
                record["status"] = "failed"
                record["error"] = str(error)
                raise RuntimeError(f"Scenario step {index} failed: {error}") from error
    finally:
        (output / "actions.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        lines = [f"{r['step']}. [{r['status']}] {r['label']}" for r in records]
        (output / "actions.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return records
