# Fossify Calculator 模拟器实测

- 测试日期：2026-10-15（北京时间）。
- 设备：Android 模拟器 `emulator-5554`，API 37.0，x86_64。
- 应用：Fossify Calculator 1.4.0，包名 `org.fossify.math`。
- APK SHA-256：`7c5443c22d6d62c67dfe80df33ea9161ff0fa440f92590bcb45d7008b57613ed`。
- 本机报告编号：`android-20261015T020740765770Z`。

| 轮次 | seed | 请求操作 | 实际注入 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | 2026 | 300 | 300 | completed |
| 2 | 2027 | 300 | 300 | completed |
| 3 | 2028 | 300 | 300 | completed |

三轮 Monkey 退出码均为 0，运行错误为 0，唯一崩溃/ANR 为 0。这只说明本次随机探索没有捕获这些问题，不证明应用没有其他缺陷。

第一轮实际录像：[`video/android-calculator-demo.mp4`](../../video/android-calculator-demo.mp4)。每轮操作日志、Android 日志、开始/结束截图及元数据保存在本机报告目录，原始日志未公开上传。

测试对象是实际发布的开源应用，没有修改应用代码或预置异常。
