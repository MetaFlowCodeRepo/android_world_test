"""根据 AndroidWorld 任务类生成 task_specs.json。

每个 spec 包含：
  task        类名
  goal        把 generate_random_params() 灌入 template 后的自然语言指令
  params      生成出来的参数（字典）
  app_names   任务涉及的 app 名（adb_utils 里的 short name）
  complexity  AndroidWorld 给的复杂度分

用法：
  cd /Users/zhp/android_world_test
  PYTHONPATH=android_world python androidworld_mcp/runner/build_specs.py \
      --tasks-file androidworld_mcp/runner/y_class_tasks.txt \
      --out androidworld_mcp/runner/task_specs.json \
      --seed 42 --n-per-task 1
"""

from __future__ import annotations

import argparse
import importlib
import json
import os
import random
import sys
from typing import Any


# AndroidWorld 任务名 → 模块路径（绕开 registry.py 的整套导入）
TASK_MODULES = {
    # composite
    "TurnOffWifiAndTurnOnBluetooth": "android_world.task_evals.composite.system",
    "TurnOnWifiAndOpenApp":          "android_world.task_evals.composite.system",
    # camera
    "CameraTakePhoto":               "android_world.task_evals.single.camera",
    "CameraTakeVideo":               "android_world.task_evals.single.camera",
    # clock
    "ClockStopWatchPausedVerify":    "android_world.task_evals.single.clock",
    "ClockStopWatchRunning":         "android_world.task_evals.single.clock",
    "ClockTimerEntry":               "android_world.task_evals.single.clock",
    # contacts
    "ContactsAddContact":            "android_world.task_evals.single.contacts",
    "ContactsNewContactDraft":       "android_world.task_evals.single.contacts",
    # system
    "OpenAppTaskEval":               "android_world.task_evals.single.system",
    "SystemBluetoothTurnOff":        "android_world.task_evals.single.system",
    "SystemBluetoothTurnOffVerify":  "android_world.task_evals.single.system",
    "SystemBluetoothTurnOn":         "android_world.task_evals.single.system",
    "SystemBluetoothTurnOnVerify":   "android_world.task_evals.single.system",
    "SystemBrightnessMax":           "android_world.task_evals.single.system",
    "SystemBrightnessMaxVerify":     "android_world.task_evals.single.system",
    "SystemBrightnessMin":           "android_world.task_evals.single.system",
    "SystemBrightnessMinVerify":     "android_world.task_evals.single.system",
    "SystemCopyToClipboard":         "android_world.task_evals.single.system",
    "SystemWifiTurnOff":             "android_world.task_evals.single.system",
    "SystemWifiTurnOffVerify":       "android_world.task_evals.single.system",
    "SystemWifiTurnOn":              "android_world.task_evals.single.system",
    "SystemWifiTurnOnVerify":        "android_world.task_evals.single.system",
}


def load_task_class(name: str):
    mod_path = TASK_MODULES.get(name)
    if not mod_path:
        raise KeyError(f"未登记的任务: {name}（请在 build_specs.TASK_MODULES 添加）")
    mod = importlib.import_module(mod_path)
    return getattr(mod, name)


def build_one_spec(name: str) -> dict[str, Any]:
    cls = load_task_class(name)
    try:
        params = cls.generate_random_params()
    except Exception as e:
        params = {"_param_gen_error": str(e)}
    template = getattr(cls, "template", "")
    try:
        goal = template.format(**params) if params and "_param_gen_error" not in params else template
    except Exception:
        goal = template
    return {
        "task":       name,
        "goal":       goal,
        "params":     params,
        "app_names":  list(getattr(cls, "app_names", ())),
        "complexity": getattr(cls, "complexity", None),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks-file", required=True,
                    help="一行一个任务类名，# 开头算注释")
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--n-per-task", type=int, default=1,
                    help=">1 时每个任务生成多份参数")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    names: list[str] = []
    with open(args.tasks_file) as f:
        for line in f:
            s = line.strip()
            if s and not s.startswith("#"):
                names.append(s)

    specs: list[dict[str, Any]] = []
    for name in names:
        for i in range(args.n_per_task):
            try:
                spec = build_one_spec(name)
            except Exception as e:
                print(f"[warn] {name}: {e}", file=sys.stderr)
                continue
            spec["instance_id"] = f"{name}#{i}"
            specs.append(spec)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)
    print(f"[ok] wrote {len(specs)} specs → {args.out}")


if __name__ == "__main__":
    main()
