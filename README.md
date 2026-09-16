# CrashHunter

CrashHunter 是一个面向课程小项目的轻量级动态软件测试平台。它接收待测软件的目录，自动执行目标程序并生成变异输入；当程序异常退出、被信号终止或超时时，平台会保存可复现的崩溃证据，并输出 bug 报告。

> 仅测试你拥有授权的软件。默认模式不会联网，也不会以管理员权限运行目标程序。

## 项目结构

```text
.
├── README.md
├── code/                  # 平台源代码、单元测试与演示目标程序
│   ├── src/crash_hunter/
│   ├── tests/
│   └── demo_target/
└── video/                 # 运行演示材料
```

## 环境

- Python 3.10 或更高版本
- Windows、macOS 或 Linux

不需要安装第三方包。

## 快速开始

从仓库根目录执行下面的命令。Windows PowerShell、macOS Terminal 和 Linux shell 均可使用。

```powershell
python -m code.src.crash_hunter --target code/demo_target --iterations 40 --seed 2026
```

命令会自动识别 `code/demo_target/main.py`，生成报告到 `reports/<时间戳>/`。演示程序特意含有两个缺陷，因此正常情况下报告会显示至少两个唯一 bug。

## 测试自己的软件

### 自动发现

如果目录中有 `main.py`、`app.py`、`target.py`，或仅有一个 Python 文件/可执行文件，可直接运行：

```powershell
python -m code.src.crash_hunter --target D:\\path\\to\\program --iterations 200
```

### 显式指定命令

不能自动发现时，用 `--command` 指定启动命令。`{input}` 会被安全地替换为本次测试输入文件的绝对路径；命令以参数数组执行，不通过 shell 拼接。

```powershell
python -m code.src.crash_hunter --target D:\\path\\to\\program `
  --command "python app.py --file {input}" --input-mode argv --iterations 500
```

若程序从标准输入读取数据，使用：

```powershell
python -m code.src.crash_hunter --target D:\\path\\to\\program `
  --command "python app.py" --input-mode stdin
```

常用选项：

| 选项 | 含义 |
| --- | --- |
| `--iterations N` | 生成并执行的测试用例数，默认 100 |
| `--timeout 秒` | 单个测试用例的最长运行时间，默认 3 秒 |
| `--seed N` | 固定随机种子，便于重复实验 |
| `--output 目录` | 报告输出目录，默认 `reports` |
| `--input-mode argv\|stdin` | 将输入文件路径作为参数，或把输入字节写入标准输入 |

## 输出与复现

每次执行都会创建 `reports/<时间戳>/`：

- `summary.json`：结构化汇总，包括总测试数、唯一 bug 数和每个 bug 的退出状态；
- `report.md`：适合直接阅读/提交的报告；
- `bugs/<bug-id>/input.bin`：触发崩溃的最小化前原始输入；
- `bugs/<bug-id>/stdout.txt`、`stderr.txt`、`metadata.json`：进程输出、错误信息和可复现命令。

在报告中复制 `reproduction_command` 数组中的参数即可重现。CrashHunter 使用“退出类型 + 退出码 + stderr 归一化摘要”去重，避免同一崩溃被重复计数。

## 设计说明

平台先使用一组边界值/高风险种子（空输入、超长输入、`CRASH`、`OVERFLOW` 等），再进行确定性随机变异。它把以下结果视为 bug 候选：

- 非零退出码；
- Unix 信号终止；
- 超时（可能是死循环或阻塞）。

该工具是动态测试器而不是形式化验证器：未报告崩溃不等于软件没有 bug。

## 自检

```powershell
python -m unittest discover -s code/tests -v
```

## 演示视频

运行演示的说明和材料位于 [video/README.md](video/README.md)。

## GitHub 发布

```powershell
git add README.md .gitignore code video
git commit -m "feat: add CrashHunter dynamic testing platform"
git branch -M main
git remote add origin https://github.com/Graylie/crashhunter.git
git push -u origin main
```
