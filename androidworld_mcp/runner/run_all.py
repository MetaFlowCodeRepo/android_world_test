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
import json
import os
import subprocess
import sys
import time


def already_passed(out_dir: str, instance_id: str, task: str) -> bool:
    task_dir = os.path.join(out_dir, task)
    if not os.path.isdir(task_dir):
        return False
    prefix = instance_id.replace("#", "_") + "-"
    for sub in sorted(os.listdir(task_dir), reverse=True):
        if not sub.startswith(prefix):
            continue
        sj = os.path.join(task_dir, sub, "summary.json")
        if os.path.isfile(sj):
            try:
                d = json.load(open(sj))
                if (d.get("self_eval") or {}).get("success") is True:
                    return True
            except Exception:
                pass
    return False


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
    args = ap.parse_args()

    only = {s for s in args.only.split(",") if s}
    skip = {s for s in args.skip.split(",") if s}
    specs = json.load(open(args.specs))

    here = os.path.dirname(os.path.abspath(__file__))
    run_one = os.path.join(here, "run_task.py")

    rows = []
    for spec in specs:
        t = spec["task"]
        iid = spec["instance_id"]
        if only and t not in only:
            continue
        if t in skip:
            print(f"[skip] {iid} (in --skip)")
            continue
        if args.resume and already_passed(args.out_dir, iid, t):
            print(f"[skip] {iid} (already passed)")
            rows.append((iid, t, True, "cached"))
            continue

        print(f"\n========== {iid} ==========")
        cmd = [
            sys.executable, run_one,
            "--specs", args.specs,
            "--hints", args.hints,
            "--instance", iid,
            "--out-dir", args.out_dir,
        ]
        rc = subprocess.call(cmd)
        rows.append((iid, t, rc == 0, "ok" if rc == 0 else "fail"))

        time.sleep(args.cooldown)

    # 汇总
    os.makedirs(args.out_dir, exist_ok=True)
    report = os.path.join(args.out_dir, "report.md")
    passed = sum(1 for r in rows if r[2])
    total = len(rows)
    with open(report, "w") as f:
        f.write(f"# AndroidWorld 自动化跑结果\n\n")
        f.write(f"通过 {passed}/{total}（{passed/total*100:.1f}%）\n\n")
        f.write("| instance | task | result | note |\n|---|---|---|---|\n")
        for iid, t, ok, note in rows:
            f.write(f"| {iid} | {t} | {'✅' if ok else '❌'} | {note} |\n")
    print(f"\n[done] 通过 {passed}/{total} → {report}")


if __name__ == "__main__":
    main()
