#!/usr/bin/env bash
#
# Download AndroidWorld 第三方 APK 并通过本地 adb 安装到目标真机。
#
# 使用：
#   ./install_apks.sh                # 自动选第一个 device
#   ./install_apks.sh -s <serial>    # 指定序列号
#   SKIP_DOWNLOAD=1 ./install_apks.sh   # 仅安装（用现有缓存）
#   ONLY="markor calendar" ./install_apks.sh  # 仅安装名字里含关键字的 apk
#
# 先决条件：
#   - 真机已开发者模式 + USB 调试，或已 adb connect
#   - 真机系统设置里允许"USB 安装"（OPPO/小米需手动打开）
#

set -uo pipefail

CACHE="${CACHE:-$HOME/android_world_apks}"
BUCKET="https://storage.googleapis.com/gresearch/android_world"

ADB_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    -s) ADB_ARGS+=(-s "$2"); shift 2 ;;
    *)  echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ---------- 选 VLC 的 APK（按真机架构） ----------
detect_vlc_apk() {
  local abi
  abi=$(adb "${ADB_ARGS[@]}" shell getprop ro.product.cpu.abi 2>/dev/null | tr -d '\r')
  case "$abi" in
    arm64-v8a|armeabi*) echo "org.videolan.vlc_13050408.apk" ;;
    x86_64|x86)         echo "org.videolan.vlc_13050407.apk" ;;
    *)                  echo "org.videolan.vlc_13050408.apk" ;;
  esac
}

# ---------- APK 清单（不含 VLC，VLC 走架构判断） ----------
APKS=(
  androidworld.apk
  clipper.apk
  net.gsantner.markor_146.apk
  com.simplemobiletools.calendar.pro_238.apk
  com.simplemobiletools.draw.pro_79.apk
  com.simplemobiletools.gallery.pro_396.apk
  com.simplemobiletools.smsmessenger_85.apk
  com.dimowner.audiorecorder_926.apk
  com.arduia.expense_11.apk
  com.flauschcode.broccoli_1020600.apk
  net.osmand-4.6.13.apk
  code.name.monkey.retromusic_10603.apk
)

# ---------- 检查 adb ----------
if ! command -v adb >/dev/null 2>&1; then
  echo "[error] adb 未安装。Mac: brew install android-platform-tools" >&2
  exit 1
fi

devices=$(adb "${ADB_ARGS[@]}" devices | awk 'NR>1 && $2=="device" {print $1}')
if [[ -z "$devices" ]]; then
  echo "[error] 未发现 adb device。先 USB 连接或 adb connect <ip>:5555" >&2
  adb "${ADB_ARGS[@]}" devices >&2
  exit 1
fi
echo "[info] target device(s):"
echo "$devices" | sed 's/^/  - /'

VLC_APK=$(detect_vlc_apk)
APKS+=("$VLC_APK")
echo "[info] VLC for this device: $VLC_APK"

# ---------- 下载 ----------
mkdir -p "$CACHE"
cd "$CACHE"

if [[ -z "${SKIP_DOWNLOAD:-}" ]]; then
  for f in "${APKS[@]}"; do
    if [[ -n "${ONLY:-}" ]] && ! echo "$f" | grep -qiE "$(echo "$ONLY" | tr ' ' '|')"; then
      continue
    fi
    if [[ -f "$f" ]]; then
      echo "[skip] $f (cached)"
    else
      echo "[get ] $f"
      curl -fL --progress-bar -o "$f.part" "$BUCKET/$f" && mv "$f.part" "$f" \
        || { echo "[fail] download $f"; rm -f "$f.part"; }
    fi
  done
fi

# ---------- 安装 ----------
ok=0; fail=0; skipped=0
for f in "${APKS[@]}"; do
  if [[ -n "${ONLY:-}" ]] && ! echo "$f" | grep -qiE "$(echo "$ONLY" | tr ' ' '|')"; then
    continue
  fi
  if [[ ! -f "$CACHE/$f" ]]; then
    echo "[miss] $f 不在缓存，跳过"
    skipped=$((skipped+1))
    continue
  fi
  echo "[apk ] adb install -r -g $f"
  if adb "${ADB_ARGS[@]}" install -r -g "$CACHE/$f" >/tmp/apkout.$$ 2>&1; then
    echo "       ok"
    ok=$((ok+1))
  else
    echo "       fail:"
    sed 's/^/       | /' /tmp/apkout.$$
    fail=$((fail+1))
  fi
  rm -f /tmp/apkout.$$
done

echo
echo "[done] ok=$ok fail=$fail skipped=$skipped"
echo "[hint] 如果 install 报 INSTALL_FAILED_USER_RESTRICTED，请到手机设置里允许 USB 安装"
echo "[hint] OsmAnd 首次启动需要联网下载离线地图，OsmAnd 任务跑前先手动初始化一次"
