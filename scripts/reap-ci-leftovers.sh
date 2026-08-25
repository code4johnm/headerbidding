#!/usr/bin/env bash
# Reap leftover browsers / display servers / Python+Node children so a hung
# pytest, demo, or xpi build cannot keep the GitHub Actions job alive
# (30m/6h cancel, exit 143). Safe on success and failure.
# Does not kill the Actions runner Node process.
set -u

echo "Reaping leftover CI browser/storage/node processes"

SELF="$$"
PARENT="${PPID:-}"

is_protected() {
  local pid="$1"
  [ -z "$pid" ] && return 0
  [ "$pid" = "$SELF" ] && return 0
  [ "$pid" = "$PARENT" ] && return 0
  [ "$pid" = "1" ] && return 0
  local cmd
  cmd="$(ps -p "$pid" -o args= 2>/dev/null || true)"
  case "$cmd" in
    ""|*Runner.Worker*|*Runner.Listener*|*actions/runner*)
      return 0
      ;;
  esac
  return 1
}

collect_pids() {
  local pattern="$1"
  local pid
  pgrep -f "$pattern" 2>/dev/null | while read -r pid; do
    if ! is_protected "$pid"; then
      echo "$pid"
    fi
  done
}

unique_pids() {
  sort -u | grep -E '^[0-9]+$' || true
}

signal_pids() {
  local sig="$1"
  local pid cmd
  while read -r pid; do
    [ -z "$pid" ] && continue
    if is_protected "$pid"; then
      continue
    fi
    if ! kill -0 "$pid" 2>/dev/null; then
      continue
    fi
    cmd="$(ps -p "$pid" -o args= 2>/dev/null || true)"
    echo "${sig} pid=${pid} ${cmd}"
    kill -s "$sig" "$pid" 2>/dev/null || true
  done
}

PIDS="$(
  {
    collect_pids 'firefox-bin/firefox'
    collect_pids 'firefox/firefox'
    collect_pids 'geckodriver'
    collect_pids '[X]vfb'
    collect_pids 'chromium'
    collect_pids 'chromedriver'
    collect_pids 'google-chrome'
    collect_pids 'StorageController'
    collect_pids 'python -m pytest'
    collect_pids 'pytest --splits'
    collect_pids 'demo.py --headless'
    collect_pids 'tsc -p tsconfig'
    collect_pids 'webpack'
    collect_pids 'web-ext'
  } | unique_pids
)"

if [ -z "${PIDS}" ]; then
  echo "No leftover CI processes found"
  exit 0
fi

echo "${PIDS}" | signal_pids TERM
sleep 2
echo "${PIDS}" | signal_pids KILL
echo "Leftover reap finished"
