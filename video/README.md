# Android 实际运行演示

[播放实际测试录像](android-calculator-demo.mp4)

录像通过模拟器的 `screenrecord` 生成，展示 Fossify Calculator 1.4.0 第一轮测试的真实画面：seed=2026，300 个操作。它是应用屏幕录像，终端和报告不在录制范围内。

三轮共注入 900 个操作，全部完成，未捕获目标应用的崩溃或 ANR。结果见 [实测摘要](../code/examples/calculator-test-result.md)。

测试与录制命令：

```powershell
python -m code.src.crash_hunter.android --target targets/fossify-calculator --sdk E:\AndroidStudio\Sdk --device emulator-5554 --events 300 --rounds 3 --seed 2026 --throttle 150 --video video/android-calculator-demo.mp4
```
