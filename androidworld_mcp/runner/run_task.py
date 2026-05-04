"""执行单个 AndroidWorld 任务并自评估。

工作流：
  1) 从 task_specs.json 找到对应 instance_id
  2) 从 eval_hints.yaml 拿对应任务的 hint
  3) 拼成 prompt，调用 `claude -p` （headless 模式），把 wimb-device MCP 工具暴露给它
  4) 解析 Claude 的 JSON 输出（success / evidence / notes），落盘到 run_results/

用法：
  python androidworld_mcp/runner/run_task.py \
      --specs androidworld_mcp/runner/task_specs.json \
      --hints androidworld_mcp/runner/eval_hints.yaml \
      --instance ClockTimerEntry#0 \
      --out-dir androidworld_mcp/run_results

  # 也可以传 --task ClockTimerEntry，自动取该任务的第一个 instance
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any


# ----------------- mini YAML loader（只支持本项目 hints 文件） -----------------

def load_hints(path: str) -> dict[str, dict[str, str]]:
    """读 eval_hints.yaml。只识别"顶级 key:" 和"  field: |" 多行块。"""
    out: dict[str, dict[str, str]] = {}
    cur_task: str | None = None
    cur_field: str | None = None
    cur_buf: list[str] = []

    def flush():
        nonlocal cur_field, cur_buf
        if cur_task and cur_field:
            out.setdefault(cur_task, {})[cur_field] = "".join(cur_buf).rstrip() + "\n"
        cur_field = None
        cur_buf = []

    with open(path) as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                # 空行 / 注释：注入到当前块（保留空行）
                if cur_field is not None:
                    cur_buf.append("\n")
                continue
            # 顶级任务名
            m = re.match(r"^([A-Za-z_][\w]*):\s*$", line)
            if m:
                flush()
                cur_task = m.group(1)
                out.setdefault(cur_task, {})
                continue
            # 二级字段："  field: |"  或  "  field: 单行值"
            m = re.match(r"^  ([a-z_]+):\s*(\|?)(.*)$", line)
            if m:
                flush()
                cur_field = m.group(1)
                if m.group(2) == "|":
                    cur_buf = []
                else:
                    val = m.group(3).strip()
                    if cur_task:
                        out[cur_task][cur_field] = val
                    cur_field = None
                continue
            # 多行块内容（缩进 4 空格起）
            if cur_field is not None and (line.startswith("    ") or line.startswith("\t")):
                cur_buf.append(line[4:] + "\n")
    flush()
    return out


# ----------------- prompt builder -----------------

PROMPT_TEMPLATE = """你正在 Android 真机上**自动执行**一项 AndroidWorld 测试任务。整个会话期间，
你只能通过 wimb-device MCP 工具操控设备（ai_click / ai_set_text / open_app / get_screenshot
/ get_screen_xml / press_back / press_home / swipe / wait_stable_screen 等）。

------ ⚠️ 第一步必须做：加载 deferred 工具 ------
wimb-device 的工具是 **deferred tools**，schema 没预加载，直接调用会 InputValidationError。
**会话的第一个动作就只能是这个 ToolSearch 调用**，把所有需要用到的设备工具一次性加载进来：

  ToolSearch(query="select:mcp__wimb-device__get_screenshot,mcp__wimb-device__ai_click,mcp__wimb-device__ai_set_text,mcp__wimb-device__ai_seq_click,mcp__wimb-device__open_app,mcp__wimb-device__press_home,mcp__wimb-device__press_back,mcp__wimb-device__get_screen_xml,mcp__wimb-device__input_text,mcp__wimb-device__click,mcp__wimb-device__swipe,mcp__wimb-device__wait_stable_screen,mcp__wimb-device__wait_screen_update", max_results=20)

加载成功后才开始执行任务。**不要**再用其它 ToolSearch 查询去乱搜，也不要把 ToolSearch 当作执行工具。

------ 任务定义 ------
任务名：{task}
实例编号：{instance_id}
goal（自然语言指令，作为 Agent 你必须完成它）：
  {goal}
参数（用于自评估对比，禁止把这些字段直接读出来当成功证据）：
  {params_json}

------ 执行准则 ------
1. press_home → get_screenshot 确认在主屏。
2. 用最少步数完成 goal。中途如遇权限弹窗、引导页一律允许/跳过。
3. 不要根据"我点了某个按钮"就推断成功 —— 必须看截图里实际的最终状态。
4. 步数预算：{step_budget} 步以内完成。

{exec_section}

------ 自评估（最后必须做） ------
{verify}

需要的证据形式：{evidence}

------ 输出 ------
最后一条文本消息**只输出**一份 JSON（不要 markdown 围栏、不要其它文字），结构：
{{
  "success": true | false,
  "confidence": 0.0 ~ 1.0,
  "evidence_summary": "一句话说明你看到的最终状态",
  "screenshot_paths": ["MCP 返回的截图本地缓存路径或描述"],
  "failure_reason": "如果 success=false，最可能的原因；否则为空字符串"
}}
"""


def _compute_max_turns(spec: dict[str, Any]) -> int:
    complexity = spec.get("complexity") or 1
    return max(100, int(complexity * 50))


def _render_with_params(text: str, params: dict[str, Any]) -> str:
    """把 hint 里的 {key} 用 spec.params 替换；params 没有的 key 原样保留。"""
    if not text:
        return text
    def repl(m):
        key = m.group(1)
        if key in params:
            return str(params[key])
        return m.group(0)
    return re.sub(r"\{([A-Za-z_][\w]*)\}", repl, text)


def build_prompt(spec: dict[str, Any], hint: dict[str, str]) -> str:
    params = spec.get("params") or {}
    exec_lines = []
    if hint.get("pre_check"):
        exec_lines.append("[执行前检查]\n" + _render_with_params(hint["pre_check"], params).rstrip())
    if hint.get("exec_hint"):
        exec_lines.append("[执行提示]\n" + _render_with_params(hint["exec_hint"], params).rstrip())
    exec_section = "\n\n".join(exec_lines) if exec_lines else ""

    return PROMPT_TEMPLATE.format(
        task=spec["task"],
        instance_id=spec["instance_id"],
        goal=spec["goal"],
        params_json=json.dumps(params, ensure_ascii=False),
        step_budget=_compute_max_turns(spec),
        exec_section=exec_section,
        verify=_render_with_params(hint.get("verify", "（未提供）"), params).rstrip(),
        evidence=_render_with_params(hint.get("evidence", "（未指定）"), params).rstrip(),
    )


# ----------------- stream.jsonl parsers -----------------

_MCP_PREFIX = "mcp__wimb-device__"


def parse_steps(stream_jsonl: str) -> list[dict[str, Any]]:
    """从 stream.jsonl 提取工具调用步骤列表。

    返回 [{step, tool, input, success, is_error}, ...]
    """
    # 先收集所有 tool_use 调用（按 id 索引）
    calls: dict[str, dict[str, Any]] = {}  # tool_use_id -> {tool, input}
    call_order: list[str] = []  # 保持顺序

    for line in stream_jsonl.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        if obj.get("type") == "assistant":
            for blk in obj.get("message", {}).get("content", []) or []:
                if blk.get("type") == "tool_use":
                    tid = blk["id"]
                    name = blk["name"]
                    if name.startswith(_MCP_PREFIX):
                        name = name[len(_MCP_PREFIX):]
                    calls[tid] = {"tool": name, "input": blk.get("input", {})}
                    call_order.append(tid)

        elif obj.get("type") == "user":
            for blk in obj.get("message", {}).get("content", []) or []:
                if blk.get("type") == "tool_result" and blk.get("tool_use_id") in calls:
                    tid = blk["tool_use_id"]
                    calls[tid]["is_error"] = bool(blk.get("is_error", False))
                    calls[tid]["success"] = not blk.get("is_error", False)

    steps = []
    for i, tid in enumerate(call_order, 1):
        c = calls[tid]
        steps.append({
            "step": i,
            "tool": c["tool"],
            "input": c["input"],
            "success": c.get("success", True),
            "is_error": c.get("is_error", False),
        })
    return steps


def parse_result_meta(stream_jsonl: str) -> dict[str, Any]:
    """从 stream.jsonl 的 result 行提取元数据。

    返回 {wall_ms, api_ms, num_turns, cost_usd, stop_reason}
    """
    for line in stream_jsonl.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") == "result":
            return {
                "wall_ms": obj.get("duration_ms"),
                "api_ms": obj.get("duration_api_ms"),
                "num_turns": obj.get("num_turns"),
                "cost_usd": obj.get("total_cost_usd"),
                "stop_reason": obj.get("subtype", "unknown"),  # "success" or "error_max_turns"
            }
    return {}


# ----------------- runner -----------------

def find_instance(specs: list[dict], task: str | None, instance_id: str | None):
    if instance_id:
        for s in specs:
            if s["instance_id"] == instance_id:
                return s
        raise SystemExit(f"未找到 instance_id={instance_id}")
    if task:
        for s in specs:
            if s["task"] == task:
                return s
        raise SystemExit(f"未找到 task={task}")
    raise SystemExit("必须传 --task 或 --instance")


def run_claude(prompt: str, cwd: str, mcp_config: str, max_turns: int) -> dict[str, Any]:
    """调用 claude headless，返回 {raw_stdout, parsed_result_json or None, returncode}"""
    if shutil.which("claude") is None:
        raise SystemExit("未找到 claude CLI。先安装 Claude Code（npm i -g @anthropic-ai/claude-code）")

    cmd = [
        "claude", "-p", prompt,
        "--mcp-config", mcp_config,
        "--allowed-tools", "mcp__wimb-device__*",
        "--permission-mode", "acceptEdits",   # 自动确认 MCP 工具
        "--output-format", "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--max-turns", str(max_turns),
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=3600, env=env)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as e:
        # 超时时把已收集的 partial stdout 返回，让上层照常落盘
        return {
            "returncode": -1,
            "stdout": (e.stdout or b"").decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""),
            "stderr": (e.stderr or b"").decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or ""),
            "timed_out": True,
        }


def extract_final_json(stream_jsonl: str) -> dict[str, Any] | None:
    """从 stream-json 输出里找最后一条 assistant 文本消息，提取 JSON。"""
    last_text = None
    for line in stream_jsonl.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Claude Code stream-json: {"type":"assistant", "message":{"content":[...]}}
        if obj.get("type") == "assistant":
            msg = obj.get("message", {})
            for blk in msg.get("content", []) or []:
                if blk.get("type") == "text":
                    last_text = blk.get("text", "")
        elif obj.get("type") == "result":
            # 终极兜底
            r = obj.get("result")
            if isinstance(r, str):
                last_text = r
    if not last_text:
        return None
    # 抽 JSON
    m = re.search(r"\{.*\}", last_text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def run_single(
    spec: dict[str, Any],
    hint: dict[str, str],
    out_dir: str,
    cwd: str,
    mcp_config: str,
) -> dict[str, Any]:
    """执行单个任务，返回 summary dict。

    out_dir: 该 instance 的输出目录（已含时间戳后缀），会自动创建。
    """
    prompt = build_prompt(spec, hint)
    max_turns = _compute_max_turns(spec)

    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "prompt.txt"), "w") as f:
        f.write(prompt)
    with open(os.path.join(out_dir, "spec.json"), "w") as f:
        json.dump(spec, f, ensure_ascii=False, indent=2)

    print(f"[run ] {spec['instance_id']}  max_turns={max_turns}  → {out_dir}")
    res = run_claude(prompt, cwd=cwd, mcp_config=mcp_config, max_turns=max_turns)

    with open(os.path.join(out_dir, "stream.jsonl"), "w") as f:
        f.write(res["stdout"])
    if res["stderr"]:
        with open(os.path.join(out_dir, "stderr.log"), "w") as f:
            f.write(res["stderr"])

    parsed = extract_final_json(res["stdout"])
    steps = parse_steps(res["stdout"])
    meta = parse_result_meta(res["stdout"])

    summary = {
        "instance_id": spec["instance_id"],
        "task": spec["task"],
        "params": spec.get("params"),
        "returncode": res["returncode"],
        "self_eval": parsed,
        "timing": {
            "wall_ms": meta.get("wall_ms"),
            "api_ms": meta.get("api_ms"),
        },
        "num_turns": meta.get("num_turns"),
        "cost_usd": meta.get("cost_usd"),
        "stop_reason": "subprocess_timeout" if res.get("timed_out") else meta.get("stop_reason", "unknown"),
        "num_steps": len(steps),
        "steps": steps,
    }
    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    if parsed and parsed.get("success") is True:
        print(f"[ok  ] success (conf={parsed.get('confidence')})")
    elif parsed:
        print(f"[fail] {parsed.get('failure_reason')}")
    else:
        print(f"[err ] 无法解析 Claude 输出（看 {out_dir}/stream.jsonl）")

    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", required=True)
    ap.add_argument("--hints", required=True)
    ap.add_argument("--task", default=None)
    ap.add_argument("--instance", default=None)
    ap.add_argument("--out-dir", default="androidworld_mcp/run_results")
    ap.add_argument("--cwd", default=None,
                    help="claude 进程工作目录；默认是项目根（包含 .mcp.json 的目录）")
    ap.add_argument("--mcp-config", default=None,
                    help="默认是 <cwd>/.mcp.json")
    args = ap.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cwd = args.cwd or project_root
    mcp_config = args.mcp_config or os.path.join(cwd, ".mcp.json")
    if not os.path.isfile(mcp_config):
        raise SystemExit(f"找不到 MCP config: {mcp_config}")

    specs = json.load(open(args.specs))
    hints = load_hints(args.hints)

    spec = find_instance(specs, args.task, args.instance)
    hint = hints.get(spec["task"])
    if not hint:
        raise SystemExit(f"eval_hints.yaml 缺少 {spec['task']} 的 hint")

    ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out_dir, spec["task"], f"{spec['instance_id'].replace('#','_')}-{ts}")

    summary = run_single(spec, hint, out_dir, cwd, mcp_config)
    ok = (summary.get("self_eval") or {}).get("success") is True
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
