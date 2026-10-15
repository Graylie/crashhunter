"""Export a portable, GitHub-readable report with target crash and UI evidence."""
import argparse
import html
import json
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    source, output = args.report.resolve(), args.destination.resolve()
    data = json.loads((source / "summary.json").read_text(encoding="utf-8"))
    if data["status"] != "completed":
        parser.error("Only completed test reports can be exported")
    output.mkdir(parents=True, exist_ok=True)
    portable = {"report_id": source.name, "status": data["status"], "device": data["device"],
                "apps": [{key: app[key] for key in ("package", "version", "sha256")} for app in data["apps"]],
                "runs": [], "bugs": data["bugs"], "errors": data["errors"]}
    lines = ["# LibreNews 1.4 实测报告", "", "本报告由实际模拟器运行记录导出。复现的是已公开的历史缺陷，不是新发现的漏洞。", "",
             "缺陷来源：[LibreNews Issue #22](https://github.com/milesmcc/LibreNews-Android/issues/22)。", "",
             f"报告编号：`{source.name}`；状态：`{data['status']}`；捕获问题：**{len(data['bugs'])}**。", "",
             "预期：无效服务器地址应显示错误，应用保持可用。实际：修改地址后点击刷新，目标应用发生数组越界崩溃。", ""]
    for app in portable["apps"]:
        lines += [f"应用：`{app['package']}`，版本 `{app['version']}`。", f"APK SHA-256：`{app['sha256']}`。", ""]
    for run in data["runs"]:
        portable["runs"].append({key: run[key] for key in ("package", "mode", "status", "requested_events", "injected_events", "reset_app_data") if key in run})
        run_source, run_output = source / run["directory"], output / run["directory"]
        run_output.mkdir(exist_ok=True)
        lines += ["## 操作步骤与截图", "", f"执行状态：`{run['status']}`。请求步骤 {run['requested_events']}，完成 {run['injected_events']}。", ""]
        for name in ("actions.json", "actions.txt", "scenario.json"):
            if (run_source / name).exists():
                shutil.copy2(run_source / name, run_output / name)
        actions = json.loads((run_source / "actions.json").read_text(encoding="utf-8"))
        for action in actions:
            lines += [f"### 步骤 {action['step']}：{action['label']}", "", f"状态：`{action['status']}`。", ""]
            frame = f"step-{action['step']:02d}-after.png"
            if (run_source / frame).exists():
                shutil.copy2(run_source / frame, run_output / frame)
                lines += [f"![实际步骤截图]({run['directory']}/{frame})", ""]
            xml = f"step-{action['step']:02d}-before.xml"
            if (run_source / xml).exists():
                shutil.copy2(run_source / xml, run_output / xml)
        lines += [f"[机器可读操作记录]({run['directory']}/actions.json) · [可复测用例]({run['directory']}/scenario.json)", ""]
    lines += ["## 捕获到的崩溃", ""]
    for bug in data["bugs"]:
        bug_output = output / "bugs" / bug["id"]
        bug_output.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / "bugs" / bug["id"] / "evidence.txt", bug_output / "evidence.txt")
        lines += [f"### {bug['id']}：{bug['kind']}", "", "```text", bug["evidence"], "```", "",
                  f"[完整错误栈](bugs/{bug['id']}/evidence.txt)", ""]
    lines += ["## 复测前置条件", "", "服务器地址必须在同一次应用运行中发生变化。保留已有 xxyyzz 配置再输入相同地址，不一定会触发该分支。建议在专用模拟器使用 --reset-app-data 恢复首次安装状态，该参数会清除目标 App 的测试数据。", "",
              "原始全设备日志保留在本机；此处发布目标包错误栈、实际步骤、原始 UI 树和截图。"]
    markdown = "\n".join(lines) + "\n"
    (output / "README.md").write_text(markdown, encoding="utf-8")
    (output / "summary.json").write_text(json.dumps(portable, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "report.html").write_text("<!doctype html><meta charset='utf-8'><title>LibreNews 实测报告</title><style>body{max-width:960px;margin:30px auto;font-family:system-ui}pre{white-space:pre-wrap}</style><pre>" + html.escape(markdown) + "</pre>", encoding="utf-8")
    print(f"Exported completed report: {output}")


if __name__ == "__main__":
    main()
