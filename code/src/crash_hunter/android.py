"""APK directory testing with ADB, Monkey, attributed crash evidence and video."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def attributed_incidents(logcat: str, monkey: str, package: str) -> list[dict]:
    """Only report target-process crashes, never arbitrary logcat errors."""
    groups: dict[tuple[str, str], list[str]] = {}
    active: dict[tuple[str, str], list[str]] = {}
    completed: list[list[str]] = []
    pattern = re.compile(r"^\S+\s+\S+\s+(\d+)\s+\d+\s+[VDIWEF]\s+(AndroidRuntime|DEBUG)\s*:\s?(.*)$")
    for line in logcat.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        pid, tag, message = match.groups()
        key = (pid, tag)
        if "FATAL EXCEPTION" in message or "*** *** ***" in message:
            if key in active:
                completed.append(active[key])
            active[key] = []
        if key in active:
            active[key].append(message)
        elif tag == "DEBUG":
            groups.setdefault(key, []).append(message)
    completed.extend(active.values())
    completed.extend(groups.values())
    incidents = []
    escaped = re.escape(package)
    for lines in completed:
        evidence = "\n".join(lines)
        java = re.search(rf"Process:\s*{escaped}(?::[\w.]+)?\s*,", evidence)
        native = re.search(rf"(?:Cmdline:\s*|>>>\s*){escaped}(?::[\w.]+)?(?:\s|$)", evidence)
        native = native and bool(re.search(r"signal \d+|Abort message:|\*\*\* \*\*\*", evidence))
        if java or native:
            kind = "JAVA_CRASH" if java else "NATIVE_CRASH"
            signature_lines = [s for s in lines if re.search(r"Exception|Error|Caused by:|^\s*at |signal |#\d+", s)]
            signature = "\n".join(signature_lines[:12]) or evidence
            signature = re.sub(r"0x[0-9a-fA-F]+|@[0-9a-fA-F]+", "<address>", signature)
            incidents.append({"kind": kind, "signature": signature, "evidence": evidence})
    marker = re.compile(rf"^//\s*(CRASH|NOT RESPONDING):\s*{escaped}(?::[\w.]+)?(?:\s|$)", re.M)
    for match in marker.finditer(monkey):
        kind = "ANR" if match.group(1) == "NOT RESPONDING" else "MONKEY_CRASH"
        if kind == "MONKEY_CRASH" and any(i["kind"].endswith("CRASH") for i in incidents):
            continue
        block = monkey[match.start():].split("// Monkey", 1)[0][:16000]
        stable = re.sub(r"\bpid=\d+|\bPID:\s*\d+|\b\d+ms\b", "<dynamic>", block)
        incidents.append({"kind": kind, "signature": stable, "evidence": block})
    return incidents


class Device:
    def __init__(self, adb: Path, serial: str):
        self.adb, self.serial = adb, serial

    def command(self, *args: str) -> list[str]:
        return [str(self.adb), "-s", self.serial, *args]

    def run(self, *args: str, timeout: float = 60, check: bool = True) -> str:
        result = subprocess.run(self.command(*args), capture_output=True, timeout=timeout)
        text = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        if check and result.returncode:
            raise RuntimeError(f"ADB command failed: {args}\n{text[-4000:]}")
        return text

    def screenshot(self, path: Path) -> None:
        result = subprocess.run(self.command("exec-out", "screencap", "-p"), capture_output=True, timeout=30)
        if result.returncode or not result.stdout.startswith(b"\x89PNG"):
            raise RuntimeError("Device screenshot failed")
        path.write_bytes(result.stdout)


def tools(sdk: Path | None) -> tuple[Path, Path]:
    candidates = [sdk, Path(os.environ.get("ANDROID_SDK_ROOT", "")),
                  Path(os.environ.get("ANDROID_HOME", "")), Path("E:/AndroidStudio/Sdk")]
    for root in candidates:
        if root and (root / "platform-tools/adb.exe").exists():
            aapts = sorted((root / "build-tools").glob("*/aapt.exe"), reverse=True)
            if aapts:
                return root / "platform-tools/adb.exe", aapts[0]
        if root and (root / "platform-tools/adb").exists():
            aapts = sorted((root / "build-tools").glob("*/aapt"), reverse=True)
            if aapts:
                return root / "platform-tools/adb", aapts[0]
    adb, aapt = shutil.which("adb"), shutil.which("aapt")
    if adb and aapt:
        return Path(adb), Path(aapt)
    raise RuntimeError("ADB/aapt not found. Install SDK Platform-Tools and Build-Tools; pass --sdk.")


def apk_info(aapt: Path, apk: Path) -> dict:
    # Older Windows aapt builds cannot open non-ASCII absolute paths.
    result = subprocess.run([str(aapt), "dump", "badging", apk.name], cwd=apk.parent, capture_output=True, timeout=60)
    text = result.stdout.decode("utf-8", errors="replace")
    package = re.search(r"^package: name='([^']+)'", text, re.M)
    activity = re.search(r"^launchable-activity: name='([^']+)'", text, re.M)
    version = re.search(r"versionName='([^']*)'", text)
    if result.returncode or not package or not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+", package.group(1)):
        raise RuntimeError(f"Cannot parse a standalone APK: {apk}")
    return {"apk": str(apk), "package": package.group(1), "activity": activity.group(1) if activity else None,
            "version": version.group(1) if version else "", "sha256": hashlib.sha256(apk.read_bytes()).hexdigest()}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def finish(report: Path, summary: dict) -> None:
    write_json(report / "summary.json", summary)
    lines = ["# Android 动态测试报告", "", f"状态：{summary['status']}",
             f"设备：`{summary['device']}`", f"唯一问题数：{len(summary['bugs'])}", "",
             "随机测试未发现崩溃，不代表软件不存在其他缺陷。安装失败、测试超时和工具错误单独记录，不计作应用 bug。", "",
             "## 应用与测试轮次", ""]
    for app in summary["apps"]:
        lines += [f"### {app['package']} ({app['version']})", "", f"APK SHA-256：`{app['sha256']}`", ""]
    for run in summary["runs"]:
        lines += [f"- {run['package']}：seed={run['seed']}，请求事件={run['requested_events']}，"
                  f"实际注入={run['injected_events']}，状态={run['status']}，日志=`{run['directory']}`"]
    lines += ["", "## 问题", ""]
    for bug in summary["bugs"]:
        lines += [f"- [{bug['id']}: {bug['kind']}](bugs/{bug['id']}/evidence.txt)",
                  f"  - 证据、触发轮次日志和复测命令：`bugs/{bug['id']}/`"]
    if not summary["bugs"]:
        lines += ["本次未捕获目标应用的崩溃或 ANR。"]
    if summary["errors"]:
        lines += ["", "## 运行错误", "", *[f"- {e}" for e in summary["errors"]]]
    text = "\n".join(lines) + "\n"
    (report / "report.md").write_text(text, encoding="utf-8")
    body = f"<!doctype html><meta charset='utf-8'><title>Android 测试报告</title><style>body{{font-family:system-ui;max-width:1000px;margin:40px auto}}pre{{white-space:pre-wrap}}img{{width:220px}}</style><h1>Android 动态测试报告</h1><pre>{html.escape(text)}</pre>"
    for run in summary["runs"]:
        image = f"{run['directory']}/after.png"
        if (report / image).exists():
            body += f"<h2>{html.escape(run['package'])} seed={run['seed']}</h2><img src='{image}'><p><a href='{run['directory']}/monkey.txt'>操作日志</a> · <a href='{run['directory']}/logcat.txt'>Android 日志</a></p>"
    (report / "report.html").write_text(body, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Test an APK directory on an Android emulator or device")
    parser.add_argument("--target", type=Path, required=True, help="Directory containing standalone APK files")
    parser.add_argument("--sdk", type=Path)
    parser.add_argument("--device", help="ADB serial; required when more than one device is online")
    parser.add_argument("--events", type=int, default=300)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--throttle", type=int, default=100, help="Milliseconds between injected events")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--output", type=Path, default=Path("reports"))
    parser.add_argument("--video", type=Path, help="Record the first test round to this MP4 (up to 180 seconds)")
    args = parser.parse_args(argv)
    if min(args.events, args.rounds) < 1 or args.throttle < 0 or args.timeout <= 0:
        parser.error("events/rounds/timeout must be positive; throttle must be nonnegative")
    apks = sorted(args.target.resolve().rglob("*.apk")) if args.target.is_dir() else []
    if not apks:
        parser.error("--target must be a directory containing standalone .apk files")
    summary = {"status": "running", "device": args.device, "target": str(args.target.resolve()),
               "apps": [], "runs": [], "bugs": [], "errors": [], "video": None}
    report = args.output.resolve() / ("android-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    report.mkdir(parents=True)
    seen: dict[str, dict] = {}
    try:
        adb, aapt = tools(args.sdk)
        listing = subprocess.run([str(adb), "devices"], capture_output=True, check=True).stdout.decode()
        online = re.findall(r"^(\S+)\s+device\s*$", listing, re.M)
        serial = args.device or (online[0] if len(online) == 1 else None)
        if serial not in online:
            raise RuntimeError(f"Choose an online --device. Online devices: {online}")
        summary["device"] = serial
        device = Device(adb, serial)
        if device.run("shell", "getprop", "sys.boot_completed").strip() != "1":
            raise RuntimeError("Android has not finished booting")
        print(f"[Android] device={serial} target={args.target.resolve()}", flush=True)
        for app_index, apk in enumerate(apks):
            app = apk_info(aapt, apk)
            summary["apps"].append(app)
            package = app["package"]
            print(f"[INSTALL] {package} version={app['version']}", flush=True)
            install = device.run("install", "-r", str(apk), timeout=180)
            if "Success" not in install:
                raise RuntimeError(install)
            resolved = device.run("shell", "cmd", "package", "resolve-activity", "--brief", "-a", "android.intent.action.MAIN", "-c", "android.intent.category.LAUNCHER", package)
            components = [line.strip() for line in resolved.splitlines() if re.fullmatch(r"[\w.]+/[\w.$]+", line.strip())]
            if not components:
                raise RuntimeError(f"No enabled launcher activity for {package}: {resolved}")
            component = components[-1]
            app["activity"] = component
            for round_index in range(args.rounds):
                seed = args.seed + round_index
                run_dir = report / f"app-{app_index + 1:02d}-round-{round_index + 1:02d}"
                run_dir.mkdir()
                device.run("shell", "am", "force-stop", package)
                if device.run("shell", "pidof", "com.android.commands.monkey", check=False).strip():
                    raise RuntimeError("Another Monkey is already running")
                command = device.command("shell", "monkey", "-p", package, "-s", str(seed),
                                         "--throttle", str(args.throttle), "--ignore-crashes", "--ignore-timeouts",
                                         "--ignore-security-exceptions", "--monitor-native-crashes",
                                         "--pct-syskeys", "0", "-v", "-v", str(args.events))
                run = {"package": package, "seed": seed, "requested_events": args.events,
                       "injected_events": 0, "directory": run_dir.name, "status": "running",
                       "command": command}
                summary["runs"].append(run)
                write_json(run_dir / "metadata.json", run)
                log_file = (run_dir / "logcat.txt").open("wb")
                logger = subprocess.Popen(device.command("logcat", "-b", "main", "-b", "system", "-b", "crash", "-v", "threadtime", "-T", "1"), stdout=log_file, stderr=subprocess.STDOUT)
                recorder = None
                remote_video = f"/sdcard/crashhunter-{report.name}.mp4"
                remote_pid = ""
                try:
                    launch = device.run("shell", "am", "start", "-W", "-n", component)
                    (run_dir / "launch.txt").write_text(launch, encoding="utf-8")
                    if "Error:" in launch or "Status: ok" not in launch:
                        raise RuntimeError(f"Launch failed: {launch}")
                    device.screenshot(run_dir / "before.png")
                    if args.video and app_index == 0 and round_index == 0:
                        if device.run("shell", "pidof", "screenrecord", check=False).strip():
                            raise RuntimeError("A screen recording is already running")
                        recorder = subprocess.Popen(device.command("shell", "screenrecord", "--size", "540x1200", "--bit-rate", "2000000", "--time-limit", "180", remote_video), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(1)
                        remote_pid = device.run("shell", "pidof", "screenrecord", check=False).strip()
                    print(f"[RUN] {package} round={round_index + 1} seed={seed} events={args.events}", flush=True)
                    result = subprocess.run(command, capture_output=True, timeout=args.timeout)
                    monkey = (result.stdout + result.stderr).decode("utf-8", errors="replace")
                    (run_dir / "monkey.txt").write_text(monkey, encoding="utf-8")
                    count = re.search(r"Events injected:\s*(\d+)", monkey)
                    run["injected_events"] = int(count.group(1)) if count else 0
                    run["exit_code"] = result.returncode
                    run["status"] = "completed" if count and run["injected_events"] == args.events and result.returncode == 0 else "incomplete"
                    time.sleep(1)
                    device.screenshot(run_dir / "after.png")
                except subprocess.TimeoutExpired as error:
                    (run_dir / "monkey.txt").write_bytes((error.stdout or b"") + (error.stderr or b""))
                    run["status"] = "timeout"
                    pids = device.run("shell", "pidof", "com.android.commands.monkey", check=False).split()
                    for pid in pids:
                        if pid.isdecimal():
                            device.run("shell", "kill", pid, check=False)
                    summary["errors"].append(f"{package} seed={seed}: test tool timeout")
                except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                    run["status"] = "failed"
                    summary["errors"].append(f"{package} seed={seed}: {error}")
                finally:
                    if recorder:
                        if remote_pid.isdecimal():
                            device.run("shell", "kill", "-2", remote_pid, check=False)
                        try:
                            recorder.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            recorder.terminate()
                            recorder.wait(timeout=5)
                        try:
                            args.video.parent.mkdir(parents=True, exist_ok=True)
                            device.run("pull", remote_video, str(args.video.resolve()))
                            summary["video"] = str(args.video.resolve())
                        except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                            summary["errors"].append(f"Video recording failed: {error}")
                    if logger.poll() is not None:
                        run["status"] = "incomplete"
                        summary["errors"].append(f"{package} seed={seed}: logcat stopped before collection completed")
                    else:
                        logger.terminate()
                    logger.wait(timeout=10)
                    log_file.close()
                logcat = (run_dir / "logcat.txt").read_text(encoding="utf-8", errors="replace")
                if not (run_dir / "monkey.txt").exists():
                    (run_dir / "monkey.txt").write_text("Test did not reach the Monkey event phase.\n", encoding="utf-8")
                monkey = (run_dir / "monkey.txt").read_text(encoding="utf-8", errors="replace")
                for incident in attributed_incidents(logcat, monkey, package):
                    key = hashlib.sha256((package + incident["kind"] + incident["signature"]).encode()).hexdigest()
                    if key in seen:
                        seen[key]["occurrences"].append(run_dir.name)
                        continue
                    bug_id = f"BUG-{len(seen) + 1:03d}"
                    bug = {"id": bug_id, "package": package, **incident, "occurrences": [run_dir.name]}
                    seen[key] = bug
                    summary["bugs"].append(bug)
                    bug_dir = report / "bugs" / bug_id
                    bug_dir.mkdir(parents=True)
                    (bug_dir / "evidence.txt").write_text(incident["evidence"], encoding="utf-8")
                    for name in ("logcat.txt", "monkey.txt", "after.png"):
                        if (run_dir / name).exists():
                            shutil.copy2(run_dir / name, bug_dir / name)
                    (bug_dir / "replay.txt").write_text(subprocess.list2cmdline(command) + "\n同一 seed 可重新生成事件流，复现也依赖相同应用状态、版本、设备和执行时序。\n", encoding="utf-8")
                    print(f"[BUG] {bug_id} {package} {incident['kind']}", flush=True)
                write_json(run_dir / "metadata.json", run)
                print(f"[ROUND DONE] status={run['status']} injected={run['injected_events']}", flush=True)
        summary["status"] = "completed" if not summary["errors"] and all(r["status"] == "completed" for r in summary["runs"]) else "incomplete"
    except (OSError, RuntimeError, subprocess.SubprocessError) as error:
        summary["status"] = "failed"
        summary["errors"].append(str(error))
        print(f"[ERROR] {error}", flush=True)
    finally:
        for bug in summary["bugs"]:
            write_json(report / "bugs" / bug["id"] / "metadata.json", bug)
        finish(report, summary)
    print(f"[DONE] status={summary['status']} unique_bugs={len(summary['bugs'])} report={report}", flush=True)
    return 0 if summary["status"] == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
