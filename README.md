# CrashHunter 软件动态测试平台

本项目使用 Python + Android SDK 实现软件动态测试。输入待测软件所在目录，平台自动执行程序、捕获崩溃并输出测试报告。Android 模式读取目录中的 APK，安装到模拟器或安卓手机，通过 Monkey 自动点击、滑动和切换页面，收集目标应用的 Java 崩溃、Native 崩溃及 ANR。

**主演示：LibreNews 1.4 真实崩溃复现。** [查看完整报告和逐步截图](code/examples/librenews-issue-22/report/README.md) · [查看最新实际录像](video/librenews-issue-22-verified.mp4)。最新复测完成 10 个明确步骤，捕获 1 个数组越界崩溃。计算器视频仅保留为随机压力测试基线。

## 运行

前置条件：

- Python 3.10+，不需要第三方 Python 库。
- Android SDK Platform-Tools、Build-Tools，及已经启动的模拟器或已连接的安卓手机。
- `adb devices` 中设备状态为 `device`。

本机 SDK 位于 `E:\AndroidStudio\Sdk`。在项目根目录启动模拟器：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\code\scripts\start-emulator.ps1
```

检查设备：

```powershell
& 'E:\AndroidStudio\Sdk\platform-tools\adb.exe' devices -l
```

将待测 APK 放进一个目录，例如 `targets/my-app/`，运行：

```powershell
python -m code.src.crash_hunter.android --target targets/my-app --sdk E:\AndroidStudio\Sdk --device emulator-5554 --events 300 --rounds 3 --seed 2026
```

`--target` 是待测软件目录，目录中的每个独立 APK 都会被测试。平台不支持 split APK/APKS 安装包。设备只有一台时可以省略 `--device`。

## Android 模式能力

- 扫描 APK 目录，解析包名、版本及 SHA-256，自动安装并启动应用。
- 根据随机种子发送点击、滑动、按键和页面切换事件，限定在目标包内运行。
- 连续收集 Android 日志，仅将明确属于目标包及其子进程的崩溃计入报告。
- 捕获 Java 异常、Native 崩溃和 Monkey 报告的 ANR，去重并保存证据。
- 每轮保存操作日志、Android 日志、开始/结束截图、启动记录和测试参数。
- 生成 Markdown、HTML 和 JSON 报告，以及每个问题的独立证据和复测命令。
- 可录制首个应用第一轮测试的真实安卓屏幕，最长 180 秒。

平台使用 Android 官方 [Monkey](https://developer.android.com/studio/test/other-testing-tools/monkey) 和 [Logcat](https://developer.android.com/tools/logcat)。参考项目：[Android Teaching Test Platform](https://github.com/jinglingsun/android-testing-platform)。支持随机探索和按明确控件步骤执行 JSON 用例；不包含参考项目的网页配置、DFS/BFS 和性质插件。

安装使用 `adb install -r`；每轮开始前停止目标应用，不清除应用数据。同一 seed 可重新生成事件流，完全复现还需要相同应用数据、版本、设备及执行时序。

## 真实 App 实测

### 已知缺陷复现：LibreNews 1.4

使用官方历史 APK，按公开的 [Issue #22](https://github.com/milesmcc/LibreNews-Android/issues/22) 关闭自动刷新，将服务器地址改为 `xxyyzz`，再点击刷新。已在当前 API 37.0 模拟器成功捕获 `BUG-001`：`ArrayIndexOutOfBoundsException: length=0; index=0`，错误位置为 `FlashManager.java:184`，与原始问题记录一致。这是公开历史缺陷的复现，不是新发现的漏洞，也没有修改待测 App 制造异常。

下载方法见 [targets/librenews/README.md](targets/librenews/README.md)。运行明确步骤用例：

```powershell
python -m code.src.crash_hunter.android --target targets/librenews --sdk E:\AndroidStudio\Sdk --device emulator-5554 --scenario code/scenarios/librenews-issue-22.json --rounds 1 --reset-app-data --video video/librenews-issue-22-verified.mp4
```

平台根据每一步的新 UI XML 定位控件，按 `resource-id` 或文本交互，保存每步操作、原始 UI 树和截图；定位失败会停止用例并报告执行失败，不会随意点击其他位置。用例需要应用界面使用英文，首次运行若有系统兼容性提示，需先关闭该提示。

复现说明和真实错误栈见 [code/examples/librenews-issue-22/README.md](code/examples/librenews-issue-22/README.md)。

完整报告、逐步截图和实际错误栈已整理在 [GitHub 可读报告](code/examples/librenews-issue-22/report/README.md)。这个缺陷需要本次进程中的服务器地址发生变化；`--reset-app-data` 在每轮前清除目标 App 数据，以恢复默认配置。仅在专用测试设备上使用该参数。

### 随机测试基线：Fossify Calculator

测试对象为官方发布的 [Fossify Calculator 1.4.0](https://github.com/FossifyOrg/Calculator/releases/tag/1.4.0)，没有为本项目设置缺陷。下载方法见 [targets/fossify-calculator/README.md](targets/fossify-calculator/README.md)。

```powershell
python -m code.src.crash_hunter.android --target targets/fossify-calculator --sdk E:\AndroidStudio\Sdk --device emulator-5554 --events 300 --rounds 3 --seed 2026 --throttle 150 --video video/android-calculator-demo.mp4
```

2026-10-15 实测：种子 2026、2027、2028，每轮实际注入 300 个事件，三轮全部完成，未捕获目标应用的崩溃或 ANR。结果见 [实测摘要](code/examples/calculator-test-result.md)，实际录像见 [video/](video/README.md)。

**未发现问题不代表应用没有 bug。** 当前检测崩溃和无响应，不能自动判定计算结果错误等所有逻辑缺陷。安装失败、设备离线和工具超时单独报告，不计作应用 bug。

## 参数

| 参数 | 说明 |
| --- | --- |
| `--target` | 独立 APK 所在目录，必填 |
| `--sdk` | SDK 根目录，也支持环境变量或 PATH 自动发现 |
| `--device` | ADB 设备号，多台设备时必填 |
| `--events` | 每轮操作数，默认 300 |
| `--rounds` | 每个 APK 测试轮数，默认 3 |
| `--seed` | 首轮随机种子，后续每轮加 1 |
| `--throttle` | 操作间隔毫秒，默认 100 |
| `--timeout` | 单轮 Monkey 超时秒数，默认 300 |
| `--output` | 报告根目录，默认 `reports` |
| `--video` | 首轮实际屏幕录像保存位置，可选 |
| `--scenario` | JSON 控件步骤用例，启用后替代 Monkey 随机事件 |
| `--reset-app-data` | 每轮清除目标 App 数据，默认关闭；用于专用设备的干净状态复测 |

## 输出

每次生成 `reports/android-<时间戳>/`：

- `report.html`、`report.md`：测试结果。
- `summary.json`：应用信息、各轮实际事件数、状态及问题列表。
- `app-xx-round-xx/`：`monkey.txt`、`logcat.txt`、测试元数据及开始/结束截图。
- 控件步骤模式额外保存 `scenario.json`、`actions.json`、`actions.txt` 和各步 UI XML/截图；步骤失败属于用例执行失败，不自动当作应用 bug。
- `bugs/BUG-xxx/`：发现问题时创建，保存 `evidence.txt`、日志、结束截图、`metadata.json` 和 `replay.txt`。

截图是该轮结束时的界面，不保证是崩溃瞬间。`replay.txt` 用于同一种子复测，在不同应用状态下不保证必然复现。

## 代码结构

- `code/src/crash_hunter/android.py`：Android 设备适配、APK 解析、自动测试、崩溃筛选及报告。
- `code/src/crash_hunter/ui_scenario.py`：根据最新控件树执行明确步骤并保存过程证据。
- `code/scenarios/`：可编辑的 JSON 测试用例。
- `code/src/crash_hunter/cli.py`：命令行程序测试入口。
- `code/src/crash_hunter/runner.py`、`fuzz.py`、`reporter.py`：命令行执行、输入变异和报告。
- `code/scripts/`：模拟器启动脚本。
- `code/tests/`：自动化测试。
- `code/examples/`：真实 App 实测摘要。
- `video/`：实际运行录像及说明。

## 测试命令行程序

原有模式仍可测试通过文件或标准输入读取数据的 Python 程序和可执行文件：

```powershell
python -m code.src.crash_hunter --target D:\path\to\program --iterations 200
```

指定启动入口：

```powershell
python -m code.src.crash_hunter --target D:\path\to\program --command "python app.py --file {input}" --input-mode argv --iterations 200
```

`code/demo_target/` 仅用于命令行模式自检，包含已知缺陷；Android 实测使用真实开源 App。

## 验证平台

```powershell
python -m unittest discover -s code/tests -v
```

测试覆盖目标包及子进程崩溃归属、Native 崩溃、ANR、无关进程排除及命令行崩溃证据保存。

## 许可证

平台代码按 [MIT License](LICENSE) 开源。第三方待测应用的代码、名称及 APK 仍遵循其原项目许可，APK 不纳入本仓库。
