# Android World Test

基于 Claude Code + MCP 的 AndroidWorld 自动化测试框架。通过 MCP（Model Context Protocol）远程连接 Android 真机，用 Claude 作为 Agent 自主完成设备操作任务并自评估。

## 架构

```
┌─────────────┐     MCP (HTTP)     ┌──────────────┐     ADB      ┌──────────┐
│  Claude Code │ ◄──────────────► │  wimb-device  │ ◄──────────► │  Android  │
│  (Agent)     │   工具调用/截图    │   Server      │   屏幕操作    │  真机     │
└─────────────┘                   └──────────────┘              └──────────┘
       │
       │ stream-json
       ▼
┌─────────────┐
│ run_task.py  │ ── 解析结果 ──► summary.json / report.md
│ run_all.py   │
└─────────────┘
```

- **Claude Code** 以 headless 模式（`claude -p`）运行，接收任务 prompt，通过 MCP 工具操作手机
- **wimb-device MCP Server** 提供设备控制工具：截图、点击、滑动、输入文本、打开 App 等
- **run_task.py / run_all.py** 负责批量调度、结果解析、报告生成

## 快速开始

### 前置条件

- Node.js 18+（安装 Claude Code CLI）
- Python 3.10+
- 可访问的 wimb-device MCP 服务器 + 已连接的 Android 设备

### 安装

```bash
# 安装 Claude Code CLI
npm i -g @anthropic-ai/claude-code

# 克隆项目
git clone git@github.com:MetaFlowCodeRepo/android_world_test.git
cd android_world_test

# 配置 MCP 连接（修改 .mcp.json 中的设备 URL）
cat .mcp.json
```

### 安装第三方 APK（可选）

```bash
# 通过 ADB 安装 AndroidWorld 所需的第三方 App
./scripts/install_apks.sh

# 仅安装部分 App
ONLY="markor calendar" ./scripts/install_apks.sh

# 指定设备
./scripts/install_apks.sh -s <device-serial>
```

### 运行单个任务

```bash
python androidworld_mcp/runner/run_task.py \
    --specs androidworld_mcp/runner/task_specs.json \
    --hints androidworld_mcp/runner/eval_hints.yaml \
    --task SystemBluetoothTurnOn
```

### 批量运行

```bash
# 运行所有任务
python androidworld_mcp/runner/run_all.py \
    --specs androidworld_mcp/runner/task_specs.json \
    --hints androidworld_mcp/runner/eval_hints.yaml \
    --out-dir androidworld_mcp/run_results

# 只跑部分任务
python androidworld_mcp/runner/run_all.py \
    --specs androidworld_mcp/runner/task_specs.json \
    --hints androidworld_mcp/runner/eval_hints.yaml \
    --only ClockTimerEntry,CameraTakePhoto

# 断点续跑（跳过已通过的）
python androidworld_mcp/runner/run_all.py \
    --specs androidworld_mcp/runner/task_specs.json \
    --hints androidworld_mcp/runner/eval_hints.yaml \
    --resume
```

## 项目结构

```
android_world_test/
├── .mcp.json                          # MCP 服务器连接配置
├── CLAUDE.md                          # Claude Code 操作指南
├── androidworld_mcp/
│   ├── runner/
│   │   ├── run_task.py                # 单任务执行 + stream.jsonl 解析
│   │   ├── run_all.py                 # 批量执行 + 报告生成
│   │   ├── task_specs.json            # 任务定义（goal、params、complexity）
│   │   ├── eval_hints.yaml            # 评估提示（exec_hint、verify、evidence）
│   │   └── build_specs.py             # 从 AndroidWorld 源码生成 specs
│   └── run_results/                   # 运行结果（按任务名/时间戳组织）
│       ├── report.md                  # 汇总报告
│       └── <TaskName>/
│           └── <instance>-<timestamp>/
│               ├── prompt.txt         # 发给 Claude 的完整 prompt
│               ├── stream.jsonl       # Claude Code 原始输出流
│               ├── summary.json       # 解析后的结构化结果
│               └── spec.json          # 任务定义副本
└── scripts/
    └── install_apks.sh                # 批量安装第三方 APK
```

## 任务定义

### task_specs.json

每个任务包含以下字段：

```json
{
  "task": "MarkorCreateFolder",
  "goal": "Create a new folder named 'Work Notes' in Markor's notebook directory.",
  "params": { "folder_name": "Work Notes" },
  "app_names": ["markor"],
  "complexity": 1,
  "instance_id": "MarkorCreateFolder#0"
}
```

### eval_hints.yaml

为每个任务提供执行提示和验证标准：

```yaml
MarkorCreateFolder:
  exec_hint: |
    打开 Markor，进入 Notebook 文件浏览器。
    点右下角 + 按钮，选择"文件夹/Folder"选项。
    输入文件夹名称 "{folder_name}"，确认创建。
  verify: |
    回到 Markor 文件列表，截图证明存在名为 "{folder_name}" 的文件夹条目。
  evidence: 1 张文件列表截图
```

## 结果输出

### summary.json

每次运行生成的结构化结果：

```json
{
  "instance_id": "MarkorCreateFolder#0",
  "task": "MarkorCreateFolder",
  "params": { "folder_name": "Work Notes" },
  "returncode": 0,
  "self_eval": {
    "success": true,
    "confidence": 0.95,
    "evidence_summary": "文件列表中可见 Work Notes 文件夹",
    "failure_reason": ""
  },
  "timing": { "wall_ms": 226000, "api_ms": 180000 },
  "num_turns": 31,
  "cost_usd": 0.91,
  "stop_reason": "success",
  "num_steps": 30,
  "steps": [
    { "step": 1, "tool": "press_home", "input": {}, "success": true },
    { "step": 2, "tool": "get_screenshot", "input": {"quality": 15}, "success": true }
  ]
}
```

### report.md 字段说明

| 字段 | 含义 |
|---|---|
| **steps** | MCP 工具调用次数（每次 `press_home`、`ai_click` 等计一步） |
| **turns** | Claude API 对话轮次（一个 turn 内可能包含多个工具调用） |
| **wall_s** | 任务墙钟耗时（秒） |
| **cost** | API 费用（美元），由 Claude Code 根据 token 用量计算 |
| **stop_reason** | `success` = 正常完成，`error_max_turns` = 达到轮次上限 |

## 已支持的任务（47 个）

**系统设置类（11 个）**：蓝牙开关、亮度调节、WiFi 开关、剪贴板、存储/关于手机查看

**系统 App 类（9 个）**：时钟秒表/计时器/闹钟、相机拍照/录像、通讯录增删

**第三方 App 打开类（10 个）**：Markor、Simple Calendar、Pro Expense、Broccoli、Retro Music、VLC、Audio Recorder、Simple Draw、Simple Gallery、OsmAnd

**第三方 App 操作类（7 个）**：Markor 建文件夹/笔记、日历建事件、费用记账、食谱添加、画图

**组合任务（3 个）**：开 WiFi + 打开 App、开蓝牙 + 打开 App

## 当前测试结果

通过率：**40/47（85.1%）**

详见 [androidworld_mcp/run_results/report.md](androidworld_mcp/run_results/report.md)
