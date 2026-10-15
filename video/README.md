# Android 实际运行演示

## LibreNews：真实历史缺陷复现

**主演示：[最新完整复现录像](librenews-issue-22-verified.mp4)**。

该轮使用干净的测试 App 数据，10 个明确步骤全部完成，捕获 1 个 Java 崩溃。报告编号 `android-20261015T063333772654Z`。完整操作记录、逐步截图、错误栈和机器可读结果见 [GitHub 完整报告](../code/examples/librenews-issue-22/report/README.md)。

[首次成功复现录像（补充）](librenews-issue-22.mp4)

录像展示关闭自动刷新、输入无效地址 `xxyyzz`、保存并刷新。最新复测中刷新后短暂白屏，随后回到欢迎页；保存的日志确认原进程发生主线程 FATAL EXCEPTION。平台捕获到数组越界异常，位置为 `FlashManager.java:184`，与公开 Issue #22 一致。见 [复现说明及错误栈](../code/examples/librenews-issue-22/README.md)。

```powershell
python -m code.src.crash_hunter.android --target targets/librenews --sdk E:\AndroidStudio\Sdk --device emulator-5554 --scenario code/scenarios/librenews-issue-22.json --rounds 1 --reset-app-data --video video/librenews-issue-22-verified.mp4
```

## Calculator：随机压力测试

[播放实际测试录像](android-calculator-demo.mp4)

录像通过模拟器的 `screenrecord` 生成，展示 Fossify Calculator 1.4.0 第一轮测试的真实画面：seed=2026，300 个操作。它是应用屏幕录像，终端和报告不在录制范围内。

三轮共注入 900 个操作，全部完成，未捕获目标应用的崩溃或 ANR。结果见 [实测摘要](../code/examples/calculator-test-result.md)。

测试与录制命令：

```powershell
python -m code.src.crash_hunter.android --target targets/fossify-calculator --sdk E:\AndroidStudio\Sdk --device emulator-5554 --events 300 --rounds 3 --seed 2026 --throttle 150 --video video/android-calculator-demo.mp4
```
