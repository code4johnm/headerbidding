#!/usr/bin/env bash
# Reap leftover Firefox / geckodriver / Xvfb / StorageController workers so a
# hung pytest or demo cannot keep the GitHub Actions job alive after the
# parent has exited (GHA then cancels with exit 143 or waits for hours).
set -u

echo "Reaping leftover CI browser/storage processes"

reap_pattern() {
  local pattern="$1"
  local pids
  pids="$(pgrep -f "$pattern" || true)"
  if [ -z "${pids}" ]; then
    return 0
  fi
  echo "TERM ${pattern}: ${pids}"
  # shellcheck disable=SC2086
  kill -TERM ${pids} 2>/dev/null || true
}

reap_pattern 'firefox-bin/firefox'
reap_pattern 'firefox/firefox'
reap_pattern 'geckodriver'
reap_pattern '[X]vfb'

sleep 2

for pattern in 'firefox-bin/firefox' 'firefox/firefox' 'geckodriver' '[X]vfb'; do
  pids="$(pgrep -f "$pattern" || true)"
  if [ -n "${pids}" ]; then
    echo "KILL ${pattern}: ${pids}"
    # shellcheck disable=SC2086
    kill -KILL ${pids} 2>/dev/null || true
  fi
done

echo "Leftover reap finished"
