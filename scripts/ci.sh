#!/bin/bash
# Run the real pytest-split matrix. Bound pytest and reap leftover workers so
# a hang cannot burn the job timeout (GHA cancel / exit 143).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup_ci() {
  bash "${SCRIPT_DIR}/reap-ci-leftovers.sh" || true
}
trap cleanup_ci EXIT

# 25 minutes: below the job timeout so pytest reports a timeout instead of
# GitHub cancelling the job. Override with PYTEST_TIMEOUT_SECS if needed.
PYTEST_TIMEOUT_SECS="${PYTEST_TIMEOUT_SECS:-1500}"

run_pytest() {
  if [ -n "${GROUP:-}" ] && [ -n "${SPLITS:-}" ]; then
    # CI mode: use pytest-split for optimal distribution (keep all 7 groups)
    python -m pytest --splits "$SPLITS" --group "$GROUP" --splitting-algorithm least_duration --cov=openwpm --junit-xml=junit-report.xml --cov-report=xml -s -v --durations=10
  else
    # Local mode: run specific tests or all
    python -m pytest --cov=openwpm --junit-xml=junit-report.xml --cov-report=xml ${TESTS:-} -s -v --durations=10
  fi
}

if ! command -v timeout >/dev/null 2>&1; then
  run_pytest
  exit 0
fi

export -f run_pytest
# --foreground: deliver TERM/KILL to pytest (not a backgrounded child).
# --kill-after: reap a pytest that ignores TERM (StorageController hang).
set +e
timeout --foreground --signal=TERM --kill-after=30s "${PYTEST_TIMEOUT_SECS}s" \
  bash -c 'run_pytest'
status=$?
set -e
if [ "$status" -eq 124 ] || [ "$status" -eq 137 ]; then
  echo "::error::pytest timed out after ${PYTEST_TIMEOUT_SECS}s (status ${status}). Leftover workers will be reaped."
fi
exit "$status"
