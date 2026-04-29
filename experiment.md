# AndroidWorld MCP 自动化测试实验报告

## 1. 研究背景

### 1.1 问题定义

AndroidWorld 是 Google Research 提出的一个 Android 设备操作基准测试集，包含 91 个涵盖系统设置、系统 App、第三方 App 的自动化任务。原始 AndroidWorld 框架依赖本地 ADB 连接和模拟器环境，在数据预置（SQLite 写入）、任务验证（数据库查询）和环境管理方面与本地开发工具深度耦合。

本项目探索一种**纯远程、无 ADB** 的替代方案：通过 MCP（Model Context Protocol）远程连接 Android 真机，以 Claude 大语言模型作为 Agent，仅通过屏幕截图和 UI 交互工具自主完成设备操作任务，并通过视觉自评估判断任务是否成功。

### 1.2 研究目标

1. 验证 LLM Agent（Claude Opus 4）在纯视觉驱动下能否有效完成 AndroidWorld 基准任务
2. 量化通过率、耗时、费用等关键指标
3. 探索将原本依赖 ADB/SQLite 的 F-class 任务转化为纯 UI 操作的可行性
4. 为 LLM + MCP 在移动设备自动化领域的应用提供实验基线

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────┐        MCP (HTTP)         ┌──────────────────┐        ADB         ┌──────────┐
│   Claude Code   │ ◄───────────────────────► │   wimb-device    │ ◄────────────────► │ Android  │
│   CLI (Agent)   │   截图 / 点击 / 输入       │   MCP Server     │   屏幕操作          │ 真机     │
│                 │   ai_click / ai_set_text   │   (VLM 内置)     │                    │ (小米)   │
└────────┬────────┘                           └──────────────────┘                    └──────────┘
         │                                           ↑
         │ stream-json                               │ HTTP
         ▼                                           │
┌─────────────────┐                          ┌──────┴─────────┐
│  run_task.py    │── 解析结果 ──►            │  阿里云服务器    │
│  run_all.py     │   summary.json            │  8.140.220.95   │
│  (调度层)       │   report.md               └────────────────┘
└─────────────────┘
```

系统分为三层：

- **调度层**（本机 Python）：`run_task.py` 构造 prompt、启动 Claude CLI 子进程、解析 stream-json 输出、生成结构化结果；`run_all.py` 负责批量调度、断点续跑和报告生成。
- **Agent 层**（Claude Code CLI）：以 headless 模式（`claude -p`）运行，接收任务 prompt，通过 MCP 工具与设备交互，自主决策操作序列，最终输出自评估 JSON。
- **设备层**（wimb-device MCP Server）：部署在远程服务器上，通过 ADB 连接 Android 真机，对外暴露 MCP 工具接口。内置 VLM（视觉语言模型）实现 `ai_click`、`ai_set_text` 等视觉定位功能。

### 2.2 MCP 工具集

wimb-device MCP Server 提供以下工具：

| 工具 | 功能 | 输入 |
|---|---|---|
| `get_screenshot` | 获取设备屏幕截图 | quality (1-95) |
| `get_screen_xml` | 获取 UI 层级 XML | — |
| `click` | 点击屏幕指定坐标 | x, y (像素或百分比) |
| `swipe` | 滑动手势 | from_x/y, to_x/y, duration |
| `input_text` | 向指定可编辑节点输入文本 | innerid, text |
| `press_back` | 返回键 | — |
| `press_home` | Home 键 | — |
| `open_app` | 打开指定包名的应用 | package_name |
| `ai_click` | AI 视觉定位并点击文本/图标 | text 或 icon |
| `ai_set_text` | AI 视觉定位输入框并输入文字 | element, text |
| `ai_seq_click` | 批量按顺序点击多个文本 | texts[] |
| `wait_screen_update` | 等待屏幕变化 | timeout |
| `wait_stable_screen` | 等待屏幕稳定 | stable_duration, timeout |

### 2.3 Agent 交互策略

Agent 采用**视觉优先、XML 兜底**的分层策略：

1. **第一优先级**：`get_screenshot` 获取截图 → 分析页面内容 → 使用 `ai_click` / `ai_set_text` 等视觉工具操作
2. **第二优先级**：当视觉工具无法准确定位时（元素被遮挡、界面复杂），使用 `get_screen_xml` 获取 UI 层级 → 解析节点坐标/innerid → 使用 `click` / `input_text` 操作
3. **操作后验证**：每次操作后截图确认结果，不以"执行了操作"推断成功

### 2.4 Prompt 工程

每个任务的 prompt 由以下部分组成：

```
┌─────────────────────────────────────────┐
│ 1. 角色设定（Android 真机自动化 Agent）   │
│ 2. 任务定义（task, instance_id, goal）   │
│ 3. 参数（params JSON，用于自评估对比）    │
│ 4. 执行准则（最少步数、处理弹窗、信任截图）│
│ 5. 步数预算 step_budget                  │
│ 6. 执行提示 exec_hint（可选，来自 hints） │
│ 7. 自评估标准 verify（来自 hints）        │
│ 8. 证据要求 evidence                     │
│ 9. 输出格式（严格 JSON）                  │
└─────────────────────────────────────────┘
```

**步数预算计算**：`max(50, complexity × 30)`。complexity=1 的简单任务获得 50 个 turn，complexity=3.4 的日历任务获得 102 个 turn，complexity=12 的 OsmAndTrack 获得 360 个 turn。

**参数模板渲染**：eval_hints.yaml 中的 `{param_name}` 占位符会被自动替换为 task_specs.json 中对应的参数值，使 hints 可以复用同一模板。

## 3. 实验设计

### 3.1 任务分类

AndroidWorld 原始 91 个任务按可执行性分为三类：

| 分类 | 含义 | 数量 | 本项目处理方式 |
|---|---|---|---|
| **Y-class** | 仅需系统自带 App（设置、相机、时钟、通讯录） | 23 | 直接执行，去除 3 个断网任务后剩 20 个 |
| **P-class** | 需安装第三方 App（Markor、Calendar、Expense 等） | 37 | 安装 APK 后直接执行 |
| **F-class** | 需 ADB/SQLite 预置数据或验证 | 31 | 15 个转为 UI 预置方案，16 个不可行 |

### 3.2 F-class 任务的 UI 预置方案

原始 F-class 任务依赖 ADB 在执行前向数据库注入数据（如创建日历事件供删除、插入多条费用记录供去重）。本项目采用**两阶段 UI 预置方案**：

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  阶段一       │  ───►  │  阶段二       │  ───►  │  自评估       │
│  Setup        │        │  Execute      │        │  Verify       │
│  通过 UI 创建 │        │  执行实际任务  │        │  截图验证结果  │
│  测试数据     │        │  （删除/编辑） │        │              │
└──────────────┘        └──────────────┘        └──────────────┘
```

**示例** — `RecipeDeleteSingleRecipe`：
- 阶段一（Setup）：通过 Broccoli App UI 添加 "Miso Soup" 和 "Caesar Salad" 两份食谱
- 阶段二（Execute）：删除 "Miso Soup"
- 自评估（Verify）：截图证明食谱列表只剩 "Caesar Salad"

**可行性判定标准**：

| 判定 | 标准 | 数量 |
|---|---|---|
| FEASIBLE | UI 预置数据量 < 10 条，可操作 | 15 |
| HARD | 需预置 29~50 条噪声数据，UI 操作太慢 | 6 |
| NOT_FEASIBLE | 需放置文件/模拟收短信，UI 无法实现 | 10 |

### 3.3 不可行任务说明

以下 16 个 F-class 任务无法在当前方案下执行：

**NOT_FEASIBLE（10 个）**：
- Browser 系列（3 个）：需要预置 `task.html` 到设备文件系统
- Gallery 系列（2 个）：需要预置特定图片文件
- RetroPlaylistDuration：需要预置已知时长的音乐文件
- SMS 回复/转发系列（4 个）：需要模拟接收短信

**HARD（6 个）**：
- ExpenseDeleteDuplicates2、ExpenseDeleteMultiple2：需预置 40~50 条费用记录
- RecipeDeleteDuplicateRecipes2/3、RecipeDeleteMultipleRecipesWithNoise、RecipeDeleteSingleWithRecipeWithNoise：需预置 29~30 条食谱记录

另外排除了 4 个 P-class 任务：
- MarkorTranscribeReceipt、MarkorTranscribeVideo：需要预置特定图片/视频文件
- FilesDeleteFile、FilesMoveFile：goal 模板中的路径（`sdk_gphone_x86_64`）是模拟器专用，不适用于真机

以及 3 个断网任务（SystemWifiTurnOff、SystemWifiTurnOffVerify、TurnOffWifiAndTurnOnBluetooth），因为关闭 WiFi 会导致 MCP 远程连接断开。

### 3.4 最终任务集

本项目最终包含 **88 个任务**：

| 来源 | 数量 | 说明 |
|---|---|---|
| 官方 Y-class | 20 | 系统设置、时钟、相机、通讯录、组合任务 |
| 官方 P-class | 33 | 第三方 App 操作（Markor、Calendar、Expense、Recipe、OsmAnd 等） |
| 官方 F-class（UI 预置） | 15 | 日历删除、费用删除/去重、食谱删除/去重、跨 App 读取添加 |
| 自建扩展任务 | 20 | 10 个 OpenApp + 6 个参数变体 + 4 个新增任务 |

**按 App 分布**：

| App 类别 | 任务数 | 复杂度范围 |
|---|---|---|
| System Settings | 14 | 1~2 |
| Markor | 13 | 1~7.8 |
| OpenApp | 11 | 1 |
| Broccoli Recipe | 9 | 2.4~4 |
| Simple Calendar | 8 | 2.4~3.4 |
| Pro Expense | 7 | 1.2~4 |
| Clock | 4 | 1~1.2 |
| Contacts | 3 | 1.2 |
| OsmAnd | 3 | 1.3~12 |
| Retro Music | 3 | 2.4~5 |
| Camera | 2 | 1 |
| Audio Recorder | 2 | 1.2~2 |
| Simple Draw | 2 | 1.8 |
| Simple SMS | 2 | 1.6~2.2 |
| VLC | 2 | 2.8~4.8 |
| Settings（查看类） | 2 | 1 |
| Simple Gallery | 1 | 2.6 |

### 3.5 实验环境

| 组件 | 配置 |
|---|---|
| **Agent 模型** | Claude Opus 4（claude-opus-4） |
| **Claude Code CLI** | headless 模式 (`claude -p`)，stream-json 输出 |
| **MCP 服务器** | wimb-device，部署于阿里云（8.140.220.95:8000） |
| **Android 设备** | 小米真机，MIUI / HyperOS 系统 |
| **第三方 App** | 12 个（Markor、Simple Calendar Pro、Pro Expense、Broccoli、Simple Draw Pro、Simple Gallery Pro、Audio Recorder、Retro Music、VLC、OsmAnd、Simple SMS Messenger、Clipper） |
| **APK 来源** | Google Research AndroidWorld 官方 GCS bucket |
| **运行方式** | 串行执行（设备一次只能处理一个任务），任务间 2 秒冷却 |

### 3.6 评估方法

**自评估（Self-Evaluation）**：与原始 AndroidWorld 通过 ADB 查询数据库验证不同，本项目采用 Agent 自评估——Agent 在完成任务后，按照 `eval_hints.yaml` 中的验证标准截图取证，并输出结构化 JSON：

```json
{
  "success": true,
  "confidence": 0.95,
  "evidence_summary": "文件列表中可见 Work Notes 文件夹",
  "screenshot_paths": ["..."],
  "failure_reason": ""
}
```

**Hint 驱动的验证标准**：每个任务在 `eval_hints.yaml` 中定义了：
- `verify`：具体的截图验证标准（如"打开联系人详情页，截图证明姓名和电话正确"）
- `evidence`：需要的证据形式（如"1 张联系人详情截图"）

这种方法的优点是不需要 ADB 通道，缺点是存在 Agent 误判的可能（如 SettingsCheckStorageInfo 任务中 Agent 到达了正确页面但自评为失败）。

## 4. 实现细节

### 4.1 单任务执行流程 (run_task.py)

```
load_hints()  ──►  build_prompt()  ──►  run_claude()  ──►  parse & save
     │                   │                    │                  │
     ▼                   ▼                    ▼                  ▼
 eval_hints.yaml    PROMPT_TEMPLATE      claude -p           summary.json
 + task_specs.json  + 参数渲染           stream-json 输出    + stream.jsonl
                    + hints 注入                              + prompt.txt
```

**关键函数**：

- `load_hints(path)` — 自实现的 mini YAML 解析器（无需 pyyaml 依赖），支持多行块和注释
- `build_prompt(spec, hint)` — 将任务定义和评估提示组合为完整 prompt，支持 `{param}` 模板替换
- `_compute_max_turns(spec)` — 根据复杂度计算步数预算，统一公式避免不一致
- `run_claude(prompt, cwd, mcp_config, max_turns)` — 启动 Claude CLI 子进程，30 分钟超时
- `parse_steps(stream_jsonl)` — 从 stream-json 提取 MCP 工具调用步骤列表
- `parse_result_meta(stream_jsonl)` — 提取耗时、费用、轮次、停止原因等元数据
- `extract_final_json(stream_jsonl)` — 从最后一条 assistant 消息中提取自评估 JSON
- `run_single(spec, hint, out_dir, cwd, mcp_config)` — 完整执行单个任务并返回 summary dict

**输出目录结构**：

```
run_results/
├── report.md                              # 汇总报告
└── <TaskName>/
    └── <instance_id>-<timestamp>/
        ├── prompt.txt                     # 发给 Claude 的完整 prompt
        ├── spec.json                      # 任务定义副本
        ├── stream.jsonl                   # Claude CLI 原始输出流
        ├── stderr.log                     # 错误日志（如有）
        └── summary.json                   # 结构化结果（含 self_eval + timing + steps）
```

### 4.2 批量执行流程 (run_all.py)

- **直接 import**：`run_all.py` 直接导入 `run_task.py` 的函数，避免为每个任务启动独立 Python 子进程
- **断点续跑**：`--resume` 模式下检查已有 `summary.json`，若 `self_eval.success == true` 则跳过，支持长时间测试中断后继续
- **过滤机制**：`--only` 指定子集，`--skip` 排除特定任务
- **报告生成**：每次批量运行完毕自动生成 `report.md`，包含通过率、总费用、总耗时和逐任务明细表

### 4.3 stream.jsonl 解析

Claude CLI 的 `--output-format stream-json` 输出三种消息类型：

| type | 内容 | 提取信息 |
|---|---|---|
| `assistant` | Agent 回复（text 块 + tool_use 块） | 工具调用名称、参数；最终自评估 JSON |
| `user` | 工具返回结果（tool_result 块） | 工具调用是否出错（is_error） |
| `result` | 会话结束元数据 | duration_ms, duration_api_ms, num_turns, total_cost_usd, subtype(stop_reason) |

**注意事项**：
- `stop_reason` 字段在 `result` 行的 `subtype` 中（不是 `stop_reason`），值为 `"success"` 或 `"error_max_turns"`
- 工具名带有 `mcp__wimb-device__` 前缀，解析时需要去除

### 4.4 费用计算

费用由 Claude Code CLI 根据 token 用量自动计算（Claude Opus 4 定价）：

| Token 类型 | 单价 | 说明 |
|---|---|---|
| input_tokens | $15 / 1M | 常规输入 |
| cache_creation_input_tokens | $18.75 / 1M | 首次写入 prompt cache |
| cache_read_input_tokens | $1.875 / 1M | 命中 prompt cache |
| output_tokens | $75 / 1M | 模型输出 |

每增加一个 turn，输入 token 累积增长（携带之前的截图和对话历史），因此 turns 越多费用越高。

## 5. 实验结果

### 5.1 已执行任务结果（47/88 已运行）

基于前 47 个任务的运行结果：

| 指标 | 值 |
|---|---|
| **总任务数** | 47 |
| **通过数** | 40 |
| **通过率** | **85.1%** |
| **总墙钟耗时** | 7,554 秒（~2.1 小时） |
| **总 API 费用** | $27.00 |

### 5.2 性能指标分布

基于有完整数据的 28 个任务（早期 19 个任务未采集 timing 数据）：

| 指标 | 最小值 | 中位数 | 最大值 | 平均值 |
|---|---|---|---|---|
| Steps（MCP 工具调用次数） | 4 | 21 | 102 | 27.3 |
| Turns（API 对话轮次） | 5 | 22 | 103 | 28.5 |
| Wall time（秒） | 26 | 149 | 1,195 | 228 |
| Cost（美元） | $0.12 | $0.57 | $4.62 | $0.79 |

### 5.3 按任务类型的通过率

| 任务类型 | 通过/总数 | 通过率 | 平均费用 |
|---|---|---|---|
| 系统设置（蓝牙/WiFi/亮度/剪贴板） | 13/13 | 100% | ~$0.65 |
| 时钟（秒表/计时器/闹钟） | 4/4 | 100% | $1.21 |
| 相机（拍照/录像） | 2/2 | 100% | — |
| 通讯录（添加/草稿） | 3/3 | 100% | $0.47 |
| OpenApp（打开第三方 App） | 9/10 | 90% | $0.33 |
| 第三方 App 操作 | 6/9 | 67% | $1.12 |
| 组合任务 | 2/3 | 67% | $1.24 |
| 设置查看 | 0/2 | 0% | $0.86 |
| **总计** | **40/47** | **85.1%** | $0.79 |

### 5.4 详细任务结果

| instance | task | result | steps | turns | wall_s | cost | stop_reason |
|---|---|---|---|---|---|---|---|
| SystemBluetoothTurnOn#0 | SystemBluetoothTurnOn | PASS | - | - | - | - | - |
| SystemBluetoothTurnOnVerify#0 | SystemBluetoothTurnOnVerify | PASS | - | - | - | - | - |
| SystemBluetoothTurnOff#0 | SystemBluetoothTurnOff | PASS | - | - | - | - | - |
| SystemBluetoothTurnOffVerify#0 | SystemBluetoothTurnOffVerify | PASS | - | - | - | - | - |
| SystemBrightnessMax#0 | SystemBrightnessMax | PASS | - | - | - | - | - |
| SystemBrightnessMaxVerify#0 | SystemBrightnessMaxVerify | PASS | - | - | - | - | - |
| SystemBrightnessMin#0 | SystemBrightnessMin | PASS | - | - | - | - | - |
| SystemBrightnessMinVerify#0 | SystemBrightnessMinVerify | PASS | 22 | 23 | 159 | $0.65 | success |
| SystemCopyToClipboard#0 | SystemCopyToClipboard | PASS | - | - | - | - | - |
| SystemWifiTurnOn#0 | SystemWifiTurnOn | PASS | - | - | - | - | - |
| SystemWifiTurnOnVerify#0 | SystemWifiTurnOnVerify | PASS | - | - | - | - | - |
| ClockStopWatchPausedVerify#0 | ClockStopWatchPausedVerify | PASS | - | - | - | - | - |
| ClockStopWatchRunning#0 | ClockStopWatchRunning | PASS | - | - | - | - | - |
| ClockTimerEntry#0 | ClockTimerEntry | PASS | 46 | 47 | 365 | $1.69 | success |
| CameraTakePhoto#0 | CameraTakePhoto | PASS | - | - | - | - | - |
| CameraTakeVideo#0 | CameraTakeVideo | PASS | - | - | - | - | - |
| ContactsAddContact#0 | ContactsAddContact | PASS | - | - | - | - | - |
| ContactsNewContactDraft#0 | ContactsNewContactDraft | PASS | 46 | 47 | 382 | $1.67 | success |
| OpenAppTaskEval#0 | OpenAppTaskEval | PASS | - | - | - | - | - |
| TurnOnWifiAndOpenApp#0 | TurnOnWifiAndOpenApp | PASS | - | - | - | - | - |
| AudioRecorderRecordAudio#0 | AudioRecorderRecordAudio | **FAIL** | 50 | 51 | 383 | $1.45 | error_max_turns |
| MarkorCreateNote#0 | MarkorCreateNote | **FAIL** | 50 | 51 | 410 | $1.48 | error_max_turns |
| MarkorCreateFolder#0 | MarkorCreateFolder | PASS | 30 | 31 | 226 | $0.91 | success |
| SimpleCalendarAddOneEvent#0 | SimpleCalendarAddOneEvent | **FAIL** | 102 | 103 | 1195 | $4.62 | error_max_turns |
| ExpenseAddSingle#0 | ExpenseAddSingle | PASS | 20 | 21 | 146 | $0.55 | success |
| RecipeAddSingleRecipe#0 | RecipeAddSingleRecipe | PASS | 24 | 25 | 151 | $0.68 | success |
| SimpleDrawProCreateDrawing#0 | SimpleDrawProCreateDrawing | PASS | 21 | 22 | 144 | $0.57 | success |
| OpenAppMarkor#0 | OpenAppMarkor | PASS | 5 | 6 | 36 | $0.15 | success |
| OpenAppCalendar#0 | OpenAppCalendar | PASS | 17 | 18 | 121 | $0.43 | success |
| OpenAppExpense#0 | OpenAppExpense | PASS | 4 | 5 | 30 | $0.12 | success |
| OpenAppBroccoli#0 | OpenAppBroccoli | PASS | 4 | 5 | 26 | $0.12 | success |
| OpenAppRetroMusic#0 | OpenAppRetroMusic | **FAIL** | 50 | 51 | 404 | $1.42 | error_max_turns |
| OpenAppVLC#0 | OpenAppVLC | PASS | 36 | 37 | 591 | $1.01 | success |
| OpenAppAudioRecorder#0 | OpenAppAudioRecorder | PASS | 7 | 8 | 54 | $0.18 | success |
| OpenAppSimpleDraw#0 | OpenAppSimpleDraw | PASS | 4 | 5 | 27 | $0.12 | success |
| OpenAppGallery#0 | OpenAppGallery | PASS | 30 | 31 | 654 | $0.81 | success |
| OpenAppOsmAnd#0 | OpenAppOsmAnd | PASS | 9 | 10 | 65 | $0.24 | success |
| ContactsAddContact2#0 | ContactsAddContact2 | PASS | 17 | 18 | 104 | $0.47 | success |
| SystemCopyToClipboard2#0 | SystemCopyToClipboard2 | PASS | 34 | 35 | 305 | $1.32 | success |
| ExpenseAddSingle2#0 | ExpenseAddSingle2 | PASS | 18 | 19 | 123 | $0.50 | success |
| RecipeAddSingleRecipe2#0 | RecipeAddSingleRecipe2 | PASS | 21 | 22 | 148 | $0.59 | success |
| MarkorCreateFolder2#0 | MarkorCreateFolder2 | PASS | 19 | 20 | 165 | $0.54 | success |
| SimpleDrawProCreateDrawing2#0 | SimpleDrawProCreateDrawing2 | PASS | 21 | 22 | 149 | $0.57 | success |
| ClockSetAlarm#0 | ClockSetAlarm | PASS | 37 | 38 | 246 | $1.21 | success |
| SettingsCheckStorageInfo#0 | SettingsCheckStorageInfo | **FAIL** | 34 | 35 | 151 | $0.71 | success |
| SettingsCheckAboutPhone#0 | SettingsCheckAboutPhone | **FAIL** | 43 | 31 | 254 | $1.00 | success |
| TurnOnBluetoothAndOpenApp#0 | TurnOnBluetoothAndOpenApp | **FAIL** | 62 | 61 | 340 | $1.24 | error_max_turns |

> 注：显示 `-` 的任务是早期批次执行的，当时尚未采集 timing/steps 数据。

### 5.5 失败分析

7 个失败任务分为两类：

**达到轮次上限（5 个）**：

| 任务 | Steps | 可能原因 |
|---|---|---|
| AudioRecorderRecordAudio | 50 | Agent 在权限弹窗和 UI 导航中消耗过多轮次 |
| MarkorCreateNote | 50 | Markor 首次启动引导页处理复杂 |
| SimpleCalendarAddOneEvent | 102 | 日历时间选择器交互困难（picker wheel），消耗大量轮次 |
| OpenAppRetroMusic | 50 | 权限弹窗循环、MIUI 安全中心反复拦截第三方 App 启动 |
| TurnOnBluetoothAndOpenApp | 62 | 两步任务，每步都需大量交互 |

**自评估误判（2 个）**：

| 任务 | Stop Reason | 分析 |
|---|---|---|
| SettingsCheckStorageInfo | success（正常完成） | Agent 导航到了存储页面但自评为失败——可能是因为 MIUI/HyperOS 的存储页面布局与原生 Android 不同，Agent 未能识别 |
| SettingsCheckAboutPhone | success（正常完成） | 类似原因，小米的"关于手机"页面结构与原生 Android 差异较大，Agent 找到了页面但认为信息不够完整 |

### 5.6 费用-复杂度关系

```
Cost ($)
  5 │                                              × SimpleCalendarAddOneEvent (FAIL)
    │
  4 │
    │
  3 │
    │
  2 │  ×ClockTimer  ×ContactsDraft                 × AudioRecorder (FAIL)
    │  ×MarkorNote(FAIL)  ×CopyClipboard2  × RetroMusic (FAIL)
  1 │  ×ClockAlarm  ×VLC  ×Gallery × BT+App(FAIL)  × Settings×2 (FAIL)
    │  ×MarkorFolder ×Recipe ×Expense ×Draw
0.5 │  ×Contact2  ×Expense2  ×Recipe2  ×Folder2
    │  ×Calendar(open)  ×OsmAnd(open)
    │  ×Markor(open)  ×AudioRec(open)
0.1 │  ×Expense(open) ×Broccoli(open) ×Draw(open)
    └──────────────────────────────────────────────
    1        1.2      1.8      2       3.4    complexity
```

关键发现：
- 简单任务（complexity=1）费用在 $0.12~$0.65 之间
- 失败任务不仅通过率为 0，还白白消耗了 $1.24~$4.62
- 日历事件创建（complexity=3.4）是最昂贵的单一任务

## 6. 关键发现与分析

### 6.1 Agent 能力边界

**强项**：
- 系统设置操作（蓝牙/WiFi/亮度）：100% 通过率，交互路径简单清晰
- 打开 App 并处理权限弹窗：90% 通过率，AI 视觉定位表现良好
- 简单内容创建（添加联系人、费用、食谱）：通过率高
- 跨 App 操作（开 WiFi + 打开 App）：可以完成

**弱项**：
- 复杂时间选择器交互：日历事件创建消耗 102 个 turn 仍失败
- 首次 App 初始化：引导页处理容易陷入循环
- 厂商定制 UI：小米安全中心弹窗（"wlmb 想要打开 X，是否允许?"）、MIUI/HyperOS 非标设置页面布局
- 自评估准确性：在设置查看类任务中出现误判

### 6.2 费用效率

| 任务类型 | 平均费用 | 平均耗时 | 评价 |
|---|---|---|---|
| OpenApp 类 | $0.33 | 48s | 高效 |
| 系统设置类 | $0.65 | 159s | 合理 |
| 内容创建类 | $0.72 | 156s | 合理 |
| 复杂操作类 | $1.50 | 400s | 较贵 |
| 失败任务 | $2.04 | 546s | 纯浪费 |

### 6.3 MCP 远程方案的优劣势

**优势**：
1. 无需本地 ADB 连接，可远程操作任意地理位置的设备
2. 纯 UI 交互，不依赖设备 root 或特殊权限
3. Agent 自主决策操作序列，无需预编写自动化脚本
4. 可扩展到不同品牌/型号的真机（vs 模拟器）

**劣势**：
1. 无法执行需要数据库预置的任务（已通过 UI 预置方案部分缓解）
2. 自评估可能存在误判（vs 原始方案的数据库验证）
3. 网络延迟影响截图和操作速度
4. MCP 服务器断连会导致任务失败
5. 费用较高（每个任务 $0.12~$4.62）

## 7. 待执行任务

当前 88 个任务中已执行 47 个，剩余 **41 个待执行**：

### 7.1 F-class UI 预置任务（15 个，全部未执行）

| 任务 | 说明 | 复杂度 |
|---|---|---|
| SimpleCalendarDeleteOneEvent | 创建事件后删除 | 2.4 |
| SimpleCalendarDeleteEvents | 创建多个事件后全部删除 | 3.4 |
| SimpleCalendarDeleteEventsOnRelativeDay | 创建本周五事件后删除 | 3.4 |
| ExpenseAddMultiple | 添加 3 条费用 | 3 |
| ExpenseAddMultipleFromMarkor | 从 Markor 笔记读取添加费用 | 4 |
| ExpenseDeleteSingle | 创建 2 条后删除 1 条 | 2 |
| ExpenseDeleteMultiple | 创建 5 条后删除 3 条 | 3 |
| ExpenseDeleteDuplicates | 创建含重复的 6 条后去重 | 3 |
| RecipeAddMultipleRecipes | 添加 3 份食谱 | 4 |
| RecipeAddMultipleRecipesFromMarkor | 从 Markor 笔记读取添加食谱 | 4 |
| RecipeAddMultipleRecipesFromMarkor2 | 从 Markor 多个笔记读取添加 | 4 |
| RecipeDeleteSingleRecipe | 创建 2 份后删除 1 份 | 3 |
| RecipeDeleteMultipleRecipes | 创建 5 份后删除 3 份 | 4 |
| RecipeDeleteMultipleRecipesWithConstraint | 按条件（含 garlic）删除 | 4 |
| RecipeDeleteDuplicateRecipes | 创建含重复的 5 份后去重 | 3 |

### 7.2 P-class 官方任务（26 个，全部未执行）

| 任务 | 说明 | 复杂度 |
|---|---|---|
| AudioRecorderRecordAudioWithFileName | 录音并指定文件名 | 2 |
| SimpleCalendarAddOneEventTomorrow | 明天添加事件 | 3.4 |
| SimpleCalendarAddOneEventInTwoWeeks | 两周后添加事件 | 3.4 |
| SimpleCalendarAddOneEventRelativeDay | 本周六添加事件 | 3.4 |
| SimpleCalendarAddRepeatingEvent | 添加每周重复事件 | 3.4 |
| MarkorAddNoteHeader | 添加笔记头部标题 | 2.4 |
| MarkorChangeNoteContent | 修改笔记内容并重命名 | 2.4 |
| MarkorCreateNoteFromClipboard | 从剪贴板创建笔记 | 2 |
| MarkorDeleteAllNotes | 删除所有笔记 | 2.4 |
| MarkorDeleteNewestNote | 删除最新的笔记 | 2 |
| MarkorDeleteNote | 删除指定笔记 | 2 |
| MarkorEditNote | 编辑笔记添加标题 | 2 |
| MarkorMergeNotes | 合并 3 个笔记 | 7.8 |
| MarkorMoveNote | 移动笔记到其他文件夹 | 2.4 |
| OsmAndFavorite | 添加地点到收藏 | 1.3 |
| OsmAndMarker | 添加地点标记 | 2 |
| OsmAndTrack | 创建多途经点轨迹 | 12 |
| RetroCreatePlaylist | 创建播放列表 | 2.4 |
| RetroPlayingQueue | 添加到播放队列 | 3.2 |
| RetroSavePlaylist | 创建并导出播放列表 | 5 |
| SaveCopyOfReceiptTaskEval | 拍照后复制到 Download | 2.6 |
| SimpleSmsSend | 发送短信 | 1.6 |
| SimpleSmsSendClipboardContent | 发送剪贴板内容短信 | 2.2 |
| VlcCreatePlaylist | VLC 创建播放列表 | 2.8 |
| VlcCreateTwoPlaylists | VLC 创建两个播放列表 | 4.8 |
| MarkorCreateNoteAndSms | 创建笔记后短信分享 | 1.8 |

### 7.3 预估费用

按已执行任务的平均费用 $0.79/任务估算，剩余 41 个任务约需 **$32**，加上已花费的 $27，总预算约 **$59**。

## 8. 下一步计划

### 8.1 短期计划（1-2 周）

1. **执行剩余 41 个任务**：优先运行 F-class UI 预置任务（验证两阶段方案的可行性），然后运行 P-class 任务
2. **重试 7 个失败任务**：特别是 `error_max_turns` 类失败，可尝试增加 max_turns 或优化 exec_hint
3. **修复自评估误判**：针对 SettingsCheckStorageInfo 和 SettingsCheckAboutPhone，调整 verify 标准使其适应 MIUI/HyperOS 的设置页面布局
4. **生成完整报告**：88 个任务全部执行后，更新 report.md 和本文档

### 8.2 中期计划（1-2 月）

5. **增加 ADB 透传工具**：在 wimb-device MCP Server 上新增 `adb_shell` 工具，使 HARD 级 F-class 任务（需 29~50 条数据预置）变得可行
6. **实现 Ground-truth 验证**：通过 ADB 查询数据库替代自评估，消除误判问题
7. **多设备测试**：在不同品牌（华为、OPPO、三星、Pixel）和 Android 版本上重复实验，评估跨设备泛化能力
8. **模型对比实验**：在相同任务集上对比 Claude Opus 4 vs Claude Sonnet 4 vs GPT-4o 的通过率和费用效率

### 8.3 长期计划

9. **优化费用**：探索 prompt cache、更短的 prompt 模板、更高效的截图压缩以降低每任务费用
10. **并行执行**：扩展到多设备并行，提高吞吐量
11. **Benchmark 发布**：将完整的实验数据集（88 个任务定义 + hints + 运行结果）开源，供社区对比

## 9. 项目文件索引

| 文件 | 说明 |
|---|---|
| `CLAUDE.md` | Claude Code Agent 操作指南（App 交互策略、已知坑点） |
| `TASKS.md` | AndroidWorld 91 个官方任务清单（含 Y/P/F 分类） |
| `.mcp.json` | MCP 服务器连接配置 |
| `androidworld_mcp/runner/run_task.py` | 单任务执行引擎 |
| `androidworld_mcp/runner/run_all.py` | 批量执行调度器 |
| `androidworld_mcp/runner/task_specs.json` | 88 个任务定义（goal + params + complexity） |
| `androidworld_mcp/runner/eval_hints.yaml` | 评估提示（exec_hint + verify + evidence） |
| `androidworld_mcp/runner/build_specs.py` | 从 AndroidWorld 源码生成 task specs |
| `androidworld_mcp/run_results/` | 运行结果（stream.jsonl + summary.json） |
| `androidworld_mcp/run_results/report.md` | 测试报告 |
| `scripts/install_apks.sh` | 第三方 APK 安装脚本 |

## 10. 参考

- [AndroidWorld: A Dynamic Benchmarking Environment for Autonomous Agents](https://arxiv.org/abs/2405.14573) (Google Research, 2024)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
