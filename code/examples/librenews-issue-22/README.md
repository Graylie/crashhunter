# LibreNews 1.4 真实崩溃复现

2026-10-15 在 API 37.0、x86_64 模拟器 `emulator-5554` 实测成功。

被测软件：官方发布的 LibreNews 1.4，包名 `app.librenews.io.librenews`。缺陷来源：[原始 Issue #22](https://github.com/milesmcc/LibreNews-Android/issues/22)。这是对历史缺陷的复现，不是平台首次发现的问题。

## 操作与结果

1. 启动并进入 LibreNews。
2. 将 Automatically refresh 设置为关闭。
3. 点击 Server，将地址改为 `xxyyzz` 并保存。
4. 点击 REFRESH。
5. 应用崩溃；平台捕获 Java 崩溃并保存 `BUG-001`。

预期：无效服务器地址应被拒绝或显示错误，应用保持可用。

实际：空新闻列表被访问第 0 个元素，产生 `java.lang.ArrayIndexOutOfBoundsException: length=0; index=0`。

关键栈：

```text
FlashManager.convertFlashesToOutputString(FlashManager.java:184)
FlashManager.writeFlashesToStorage(FlashManager.java:152)
FlashManager.clearPushedFlashes(FlashManager.java:200)
FlashManager.refresh(FlashManager.java:256)
MainFlashActivity$1.onClick(MainFlashActivity.java:67)
```

完整实测错误栈：[evidence.txt](evidence.txt)。首次成功报告编号：`android-20261015T025531330412Z`，8 个明确步骤全部完成，捕获 1 个唯一问题，无工具错误。每步原始 XML、截图、操作记录及系统日志在本机报告目录。

[在 GitHub 阅读完整实测报告与逐步截图](report/README.md)。

最终干净状态复测报告编号：`android-20261015T063333772654Z`。10 步全部完成，再次捕获相同数组越界崩溃，无工具错误。[最新完整实际录像](../../../video/librenews-issue-22-verified.mp4)。

录像：[首次成功复现](../../../video/librenews-issue-22.mp4)。它是模拟器屏幕的实际录像，应用崩溃后会退出界面，不保证系统显示“已停止运行”弹窗；以保存的 FATAL EXCEPTION 和目标包调用栈作为崩溃证据。

## 运行

```powershell
python -m code.src.crash_hunter.android --target targets/librenews --sdk E:\AndroidStudio\Sdk --device emulator-5554 --scenario code/scenarios/librenews-issue-22.json --rounds 1 --reset-app-data --video video/librenews-issue-22-verified.mp4
```

当前用例增加了输入值核验及可选兼容性提示处理，共 10 步。复现还要求本次进程内服务器地址发生变化；`--reset-app-data` 会清除目标 App 的测试数据，确保从默认地址开始。实际 APK 获取方法见 [测试对象说明](../../../targets/librenews/README.md)。
