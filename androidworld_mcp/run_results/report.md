# AndroidWorld 自动化测试报告

通过 40/47（85.1%）  |  总耗时 7554s  |  总费用 $27.00

## 字段说明

| 字段 | 含义 |
|---|---|
| **steps** | 实际调用的 MCP 工具次数。每调用一次设备操作工具（如 `press_home`、`get_screenshot`、`ai_click`）计为一步 |
| **turns** | Claude API 对话轮次数。一个 turn = 一次 assistant 回复 + 后续 user 消息。一个 turn 内可能包含多个工具调用，因此 steps 通常 ≥ turns |
| **wall_s** | 整个任务的墙钟耗时（秒），从 `claude` CLI 启动到退出的总时间 |
| **cost** | 该任务消耗的 Claude API 费用（美元），由 Claude Code CLI 根据 token 用量自动计算 |
| **stop_reason** | 任务结束原因。`success` = 正常完成；`error_max_turns` = 达到最大轮次上限被强制终止 |

## 费用计算方式

cost 由 Claude Code CLI 在 `stream.jsonl` 的 `result` 行中以 `total_cost_usd` 字段给出，计算公式为各类 token 数量 × 对应单价：

| Token 类型 | 单价（Claude Opus 4） | 说明 |
|---|---|---|
| input_tokens | $15 / 1M | 常规输入 token |
| cache_creation_input_tokens | $18.75 / 1M | 首次写入 prompt cache 的 token |
| cache_read_input_tokens | $1.875 / 1M | 命中 prompt cache 的 token（大幅降低成本） |
| output_tokens | $75 / 1M | 模型生成的输出 token |

每增加一个 turn，输入 token 会累积增长（因为每轮都携带之前的截图和对话历史），所以 turns 越多费用越高。例如 SimpleCalendarAddOneEvent 跑了 103 turns，花费 $4.62；而简单的 OpenAppExpense 仅 5 turns，花费 $0.12。

> 注：显示 `-` 的行是早期批次执行的任务，当时尚未采集 timing/steps 数据。

## 任务结果

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
| AudioRecorderRecordAudio#0 | AudioRecorderRecordAudio | FAIL | 50 | 51 | 383 | $1.45 | error_max_turns |
| MarkorCreateNote#0 | MarkorCreateNote | FAIL | 50 | 51 | 410 | $1.48 | error_max_turns |
| MarkorCreateFolder#0 | MarkorCreateFolder | PASS | 30 | 31 | 226 | $0.91 | success |
| SimpleCalendarAddOneEvent#0 | SimpleCalendarAddOneEvent | FAIL | 102 | 103 | 1195 | $4.62 | error_max_turns |
| ExpenseAddSingle#0 | ExpenseAddSingle | PASS | 20 | 21 | 146 | $0.55 | success |
| RecipeAddSingleRecipe#0 | RecipeAddSingleRecipe | PASS | 24 | 25 | 151 | $0.68 | success |
| SimpleDrawProCreateDrawing#0 | SimpleDrawProCreateDrawing | PASS | 21 | 22 | 144 | $0.57 | success |
| OpenAppMarkor#0 | OpenAppMarkor | PASS | 5 | 6 | 36 | $0.15 | success |
| OpenAppCalendar#0 | OpenAppCalendar | PASS | 17 | 18 | 121 | $0.43 | success |
| OpenAppExpense#0 | OpenAppExpense | PASS | 4 | 5 | 30 | $0.12 | success |
| OpenAppBroccoli#0 | OpenAppBroccoli | PASS | 4 | 5 | 26 | $0.12 | success |
| OpenAppRetroMusic#0 | OpenAppRetroMusic | FAIL | 50 | 51 | 404 | $1.42 | error_max_turns |
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
| SettingsCheckStorageInfo#0 | SettingsCheckStorageInfo | FAIL | 34 | 35 | 151 | $0.71 | success |
| SettingsCheckAboutPhone#0 | SettingsCheckAboutPhone | FAIL | 43 | 31 | 254 | $1.00 | success |
| TurnOnBluetoothAndOpenApp#0 | TurnOnBluetoothAndOpenApp | FAIL | 62 | 61 | 340 | $1.24 | error_max_turns |
