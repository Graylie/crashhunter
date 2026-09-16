# 运行演示

本目录用于保存 CrashHunter 的运行演示视频。建议文件名为 `crashhunter-demo.mp4`。

## 演示流程

1. 打开 PowerShell，进入项目根目录：

   ```powershell
   cd C:\Users\32825\Documents\ChatGPT\软件安全
   ```

2. 启动屏幕录制。推荐使用 OBS 的“显示器采集”录制整个屏幕，以便连续展示 PowerShell 和资源管理器。未安装 OBS 时，可打开 Windows 截图工具，切换到“录制”模式，选择整个屏幕后点击“开始”。

3. 在 PowerShell 执行：

   ```powershell
   python -m code.src.crash_hunter --target code/demo_target --iterations 40 --seed 2026
   ```

4. 终端出现 `BUG-001`、`BUG-002` 和报告目录后，复制最后一行中的报告路径。例如：

   ```text
   [DONE] unique_bugs=2 report=C:\...\reports\20260916T000000Z
   ```

5. 在资源管理器中打开该报告目录，依次展示：

   - `report.md`：测试结果与两个 bug 的崩溃签名；
   - `bugs/BUG-001/input.bin`：触发第一个 bug 的测试输入；
   - `bugs/BUG-001/stderr.txt`：程序错误栈；
   - `bugs/BUG-001/metadata.json`：退出状态和复现命令。

6. 停止录制，将视频保存为 `video/crashhunter-demo.mp4`。

## 建议时长

60 至 90 秒。视频依次展示项目目录、测试命令、终端发现 bug、报告证据四部分即可。
