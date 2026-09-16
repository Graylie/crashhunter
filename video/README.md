# 录像提交说明

将一次真实、未剪辑或清晰剪辑的运行录像保存为 `crashhunter-demo.mp4`（或 `.webm`）放在本目录。为避免 Git 仓库过大，视频文件默认被 `.gitignore` 忽略；可上传到 GitHub Release、Bilibili 或网盘，并在本文件末尾补上公开链接。

## 推荐录制内容（60-90 秒）

1. 展示仓库目录中存在 `README.md`、`code/`、`video/`。
2. 在终端执行：

   ```powershell
   python -m code.src.crash_hunter --target code/demo_target --iterations 40 --seed 2026
   ```

3. 展示终端输出的两个 `[BUG]` 以及生成的 `reports/.../report.md`。
4. 打开 `bugs/BUG-001/input.bin`、`stderr.txt` 和 `metadata.json`，说明证据包可以复现。

Windows 可使用 Xbox Game Bar（`Win+Alt+R`）或 OBS 录制；录制前请关闭包含隐私信息的窗口。

## 录像链接

待补充。
