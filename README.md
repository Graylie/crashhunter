# CrashHunter 动态软件测试平台

本项目是一个本地动态软件测试平台原型，使用 Python 标准库实现。平台输入待测软件所在目录，自动执行目标程序并生成测试输入；程序异常退出、被信号终止或超时时，平台会保存触发问题的输入与运行证据，并生成测试报告。

## 运行

前置条件：

- Windows、macOS 或 Linux；
- Python 3.10 或更高版本；
- 无第三方依赖。

在项目根目录执行演示测试：

```powershell
python -m code.src.crash_hunter --target code/demo_target --iterations 40 --seed 2026
```

平台会自动识别 `code/demo_target/main.py`，并在 `reports/<时间戳>/` 创建测试报告。演示目标程序包含两个已知缺陷，运行后终端将输出两个唯一 bug，分别对应 `CRASH` 和 `OVERFLOW` 输入。

运行单元测试：

```powershell
python -m unittest discover -s code/tests -v
```

### 测试其他软件

待测目录中包含 `main.py`、`app.py`、`target.py`，或仅有一个 Python 文件/可执行文件时，可直接执行：

```powershell
python -m code.src.crash_hunter --target D:\path\to\program --iterations 200
```

不能自动识别启动文件时，可显式指定启动命令。`{input}` 表示当前测试用例文件的绝对路径：

```powershell
python -m code.src.crash_hunter --target D:\path\to\program `
  --command "python app.py --file {input}" --input-mode argv --iterations 500
```

对于从标准输入读取数据的程序：

```powershell
python -m code.src.crash_hunter --target D:\path\to\program `
  --command "python app.py" --input-mode stdin --iterations 500
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `--iterations N` | 执行 N 个测试用例，默认 100 |
| `--timeout 秒` | 单个用例的最长运行时间，默认 3 秒 |
| `--seed N` | 固定随机种子，便于重复实验 |
| `--output 目录` | 报告输出目录，默认 `reports` |
| `--input-mode argv\|stdin` | 以文件路径参数或标准输入传递测试数据 |

## 第一版能力

- 以待测软件目录作为输入，自动发现常见 Python 程序或可执行文件；
- 支持通过 `--command` 配置任意启动命令；
- 内置边界值与高风险种子，包括空输入、长输入、路径片段与格式化字符串；
- 基于确定性随机变异生成后续测试输入；
- 捕获非零退出码、Unix 信号终止和超时；
- 使用“退出类型 + 退出码 + 归一化错误摘要”对重复崩溃去重；
- 为每个 bug 保存触发输入、标准输出、错误输出、元数据与复现命令；
- 同时生成 Markdown 报告和 JSON 汇总报告。

## 报告说明

每次运行生成 `reports/<时间戳>/`：

- `summary.json`：测试用例数、唯一 bug 数与 bug 元数据；
- `report.md`：可直接阅读的测试报告；
- `bugs/BUG-xxx/input.bin`：触发问题的原始输入；
- `bugs/BUG-xxx/stdout.txt`、`stderr.txt`：程序运行输出；
- `bugs/BUG-xxx/metadata.json`：退出状态、崩溃签名和复现命令。

## 代码结构

- `code/src/crash_hunter/cli.py`：命令行入口和测试主循环；
- `code/src/crash_hunter/discovery.py`：待测程序自动发现；
- `code/src/crash_hunter/fuzz.py`：种子语料与变异输入生成；
- `code/src/crash_hunter/runner.py`：子进程执行、超时处理和崩溃签名；
- `code/src/crash_hunter/reporter.py`：证据保存与报告生成；
- `code/src/crash_hunter/model.py`：运行结果与 bug 数据模型；
- `code/demo_target/main.py`：用于演示的待测程序；
- `code/tests/test_platform.py`：平台单元测试；
- `video/README.md`：运行演示说明。

## 运行演示

演示步骤与视频要求见 [video/README.md](video/README.md)。
