# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个手机设备远程自动化工作区，非传统软件项目。通过 MCP（Model Context Protocol）连接远程 Android 手机，实现屏幕操作自动化。

## MCP 设备控制

工作区通过 `.mcp.json` 连接远程设备服务器 `http://8.140.220.95:8000/`。操作策略：

1. **优先视觉分析**：先调用 `get_screenshot` 截图，分析屏幕内容后，使用 `ai_click` / `ai_seq_click` / `ai_set_text` 进行操作。
2. **XML 兜底**：仅当视觉分析无法准确定位时（元素被遮挡、界面复杂），再用 `get_screen_xml` + `find_nodes` / `click_node` 等节点操作。
3. **操作后验证**：每次操作后建议再次截图确认结果。

## 截图处理

`get_screenshot` 返回的截图可能超出 token 限制。处理方式：
- 将 base64 结果通过 Python 保存为 `.jpg` 文件，再用 Read 工具查看
- 使用 `quality: 15` 降低图片大小

## 常用 App 操作流程

### 京东搜索商品

1. **打开京东**：`open_app` → 包名 `com.jingdong.app.mall`，等待屏幕稳定后截图确认进入首页。
2. **点击搜索**：`ai_click` → text: `"搜索"`（首页右上角），会跳转到搜索结果页。
3. **输入搜索词**：京东搜索框是原生 `EditText`，可用 `ai_set_text`（element: `"搜索框"`）设置文本，或通过 `get_screen_xml` 获取 `innerid` 后用 `input_text` 输入。
4. **执行搜索**：`ai_click` → text: `"搜索"`。
5. **查看结果**：截图查看商品列表，使用 `swipe` 向上滑动查看更多。

> 京东为原生控件，操作顺畅；搜索结果直接展示价格、到手价、店铺、标签（自营/百亿补贴等）。

### 淘宝搜索商品

1. **打开淘宝**：`open_app` → 包名 `com.taobao.taobao`，等待屏幕稳定。
2. **处理弹窗**：淘宝频繁弹窗（会员特权、消费券、权限请求），每步操作后截图确认，用 `ai_click` 关闭。
3. **进入搜索页**：点击首页顶部搜索框（`ai_click` → icon: `"顶部搜索框"`）。
4. **输入搜索词**（三种方案按优先级排列）：
   - **方案一（推荐）**：历史搜索中有目标关键词时，直接 `ai_click` 点击历史记录。
   - **方案二（通用）**：通过 `get_screen_xml` 找到 `EditText`（uid: `searchEdit`）的 `innerid`，用 `input_text(innerid=xx, text="关键词")` 输入。
   - **方案三（备选）**：`ai_set_text(element="搜索输入框", text="关键词")`，成功率不稳定。
5. **执行搜索**：点击历史记录会自动搜索；手动输入后 `ai_click` → text: `"搜索"`。
6. **查看结果**：截图查看商品列表，用 `swipe` 上滑查看更多。

> **淘宝注意事项**：
> - `input_text` 需指定 `innerid`（从 XML 解析），不要传坐标。
> - `text` 参数中 `\n` 会被当作文本而非回车，不要用 `\n` 触发搜索。
> - 淘宝 `EditText` 的 `innerid` 不固定，每次需重新获取 XML。
> - `ai_set_text` 在淘宝中成功率不稳定，优先用 `input_text` + `innerid`。

### 抖音搜索 / 进入直播间 / 发评论

1. **打开抖音**：`open_app` → 包名 `com.ss.android.ugc.aweme`，等待屏幕稳定。
2. **进入搜索页**：`ai_click` → icon: `"右上角搜索图标"`。
3. **输入搜索词**：通过 `get_screen_xml` 找到 `EditText`（uid: `et_search_kw`）的 `innerid`，用 `input_text(innerid=xx, text="关键词")` 输入。
4. **执行搜索**：`ai_click` → text: `"搜索"`。
5. **进入直播间**：搜索结果中找到目标用户（显示"直播中"标记），`ai_click` → text: `"直播中"` 进入。
6. **发送评论**：
   - 点击底部 `"说点什么..."`（`ai_click`）打开评论输入框。
   - 通过 `get_screen_xml` 获取评论 `EditText` 的 `innerid`（与搜索框不同）。
   - `input_text(innerid=xx, text="评论内容")` 输入评论。
   - **发送按钮必须用坐标 `click` 点击**：从 XML 拿到 `text="发送"`（uid: `4us`）节点的 `top/bottom/left/right`，算中心点后调 `click(x, y)`。不要用 `ai_click(text="发送")`，VLM 在评论条的窄按钮上容易点到输入框或空白处，导致"键盘收起但评论未发出，文字作为草稿留在输入框"。
   - 验证：重新打开输入框若还保留原文字，即未发送成功；发送成功后再打开是空的，同时评论流会出现自己的昵称 + 内容。

> **抖音注意事项**：
> - 抖音搜索框是原生 `EditText`，`input_text` + `innerid` 可靠。
> - 搜索框和直播间评论框是不同的 `EditText`，切换场景后需重新获取 XML 拿新的 `innerid`。
> - 直播间评论的"发送"按钮用坐标 `click` 最可靠；`ai_click` 会静默失败（没有报错但消息没发出去）。

## 自定义 Skill

- `/call [电话号码]` — 打开拨号盘，通过 `ai_seq_click` 输入号码，确认后拨出电话。
