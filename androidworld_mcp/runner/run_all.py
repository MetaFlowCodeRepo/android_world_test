"""批量跑 task_specs.json 里的所有 instance，串行执行（手机一次只能一项）。

用法：
  python androidworld_mcp/runner/run_all.py \
      --specs androidworld_mcp/runner/task_specs.json \
      --hints androidworld_mcp/runner/eval_hints.yaml \
      --out-dir androidworld_mcp/run_results

  # 子集 / 跳过：
  --only ClockTimerEntry,CameraTakePhoto       仅这些任务
  --skip SystemWifiTurnOff,SystemWifiTurnOffVerify   跳过（首次测试时建议跳过断网类）
  --resume                                     已有 summary.json 且 success=true 则跳过

跑完会在 out-dir 下生成 report.md 汇总通过率。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import time
from typing import Any

from run_task import load_hints, find_instance, run_single


def _load_latest_summary(out_dir: str, instance_id: str, task: str) -> dict[str, Any] | None:
    """读取某 instance 最新一次 run 的 summary.json（如果存在）。"""
    task_dir = os.path.join(out_dir, task)
    if not os.path.isdir(task_dir):
        return None
    prefix = instance_id.replace("#", "_") + "-"
    for sub in sorted(os.listdir(task_dir), reverse=True):
        if not sub.startswith(prefix):
            continue
        sj = os.path.join(task_dir, sub, "summary.json")
        if os.path.isfile(sj):
            try:
                return json.load(open(sj))
            except Exception:
                pass
    return None


def already_passed(summary: dict[str, Any] | None) -> bool:
    if summary is None:
        return False
    return (summary.get("self_eval") or {}).get("success") is True


def _fmt_seconds(ms: int | float | None) -> str:
    if ms is None:
        return "-"
    return f"{ms / 1000:.0f}"


def _fmt_cost(usd: float | None) -> str:
    if usd is None:
        return "-"
    return f"${usd:.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", required=True)
    ap.add_argument("--hints", required=True)
    ap.add_argument("--out-dir", default="androidworld_mcp/run_results")
    ap.add_argument("--only", default="", help="逗号分隔的任务名子集")
    ap.add_argument("--skip", default="", help="逗号分隔的任务名跳过列表")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--cooldown", type=float, default=2.0,
                    help="两个 instance 之间停几秒（让设备回到稳态）")
    ap.add_argument("--cwd", default=None,
                    help="claude 进程工作目录；默认是项目根（包含 .mcp.json 的目录）")
    ap.add_argument("--mcp-config", default=None,
                    help="默认是 <cwd>/.mcp.json")
    args = ap.parse_args()

    only = {s for s in args.only.split(",") if s}
    skip = {s for s in args.skip.split(",") if s}
    specs = json.load(open(args.specs))

    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, "..", ".."))
    cwd = args.cwd or project_root
    mcp_config = args.mcp_config or os.path.join(cwd, ".mcp.json")
    if not os.path.isfile(mcp_config):
        raise SystemExit(f"找不到 MCP config: {mcp_config}")

    hints = load_hints(args.hints)

    # rows: list of summary dicts (with extra "note" key)
    rows: list[dict[str, Any]] = []

    for spec in specs:
        t = spec["task"]
        iid = spec["instance_id"]
        if only and t not in only:
            continue
        if t in skip:
            print(f"[skip] {iid} (in --skip)")
            continue

        existing = _load_latest_summary(args.out_dir, iid, t) if args.resume else None
        if args.resume and already_passed(existing):
            print(f"[skip] {iid} (already passed)")
            rows.append({**existing, "_note": "cached"})
            continue

        hint = hints.get(t)
        if not hint:
            print(f"[skip] {iid} (no hint in eval_hints.yaml)")
            continue

        print(f"\n========== {iid} ==========")
        ts = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        inst_out_dir = os.path.join(args.out_dir, t, f"{iid.replace('#','_')}-{ts}")

        summary = run_single(spec, hint, inst_out_dir, cwd, mcp_config)
        rows.append({**summary, "_note": "ok" if (summary.get("self_eval") or {}).get("success") else "fail"})

        time.sleep(args.cooldown)

    # --- 生成报告 ---
    os.makedirs(args.out_dir, exist_ok=True)
    report = os.path.join(args.out_dir, "report.md")

    passed = sum(1 for r in rows if (r.get("self_eval") or {}).get("success") is True)
    total = len(rows)
    total_cost = sum(r.get("cost_usd") or 0 for r in rows)
    total_wall = sum((r.get("timing") or {}).get("wall_ms") or 0 for r in rows)

    with open(report, "w") as f:
        f.write(f"# AndroidWorld 自动化跑结果\n\n")
        f.write(f"通过 {passed}/{total}（{passed/total*100:.1f}%）" if total else "无任务")
        f.write(f"  |  总耗时 {total_wall/1000:.0f}s  |  总费用 ${total_cost:.2f}\n\n")
        f.write("| instance | task | result | steps | turns | wall_s | cost | stop_reason |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for r in rows:
            ok = (r.get("self_eval") or {}).get("success") is True
            wall = (r.get("timing") or {}).get("wall_ms")
            f.write(
                f"| {r.get('instance_id','')} "
                f"| {r.get('task','')} "
                f"| {'PASS' if ok else 'FAIL'} "
                f"| {r.get('num_steps', '-')} "
                f"| {r.get('num_turns', '-')} "
                f"| {_fmt_seconds(wall)} "
                f"| {_fmt_cost(r.get('cost_usd'))} "
                f"| {r.get('stop_reason', '-')} |\n"
            )
    print(f"\n[done] 通过 {passed}/{total} → {report}")


if __name__ == "__main__":
    main()
