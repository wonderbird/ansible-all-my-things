#!/usr/bin/env bash
# Spike B — Step 2: clone spike-source 3 times, measure SSH-ready time each run.
# Run on macOS host after step1-build-source.sh completes.
set -euo pipefail

SOURCE="spike-source"
TEST_VM="spike-test"
RUNS=3

if ! tart list 2>/dev/null | awk 'NR>1 {print $2}' | grep -qx "$SOURCE"; then
  echo "ERROR: $SOURCE not found. Run step1-build-source.sh first."
  exit 1
fi

cleanup_test() {
  tart stop "$TEST_VM" 2>/dev/null || true
  tart delete "$TEST_VM" 2>/dev/null || true
}
trap cleanup_test INT TERM

echo "=== Spike B Step 2: measure SSH-ready time from pre-built clone ==="
echo "Source: $SOURCE"
echo ""

TIMES=()

for i in $(seq 1 $RUNS); do
  echo "--- Run $i of $RUNS ---"
  tart clone "$SOURCE" "$TEST_VM"

  START=$(date +%s)
  tart run "$TEST_VM" --no-graphics &
  TART_PID=$!

  until IP=$(tart ip "$TEST_VM" 2>/dev/null) && [ -n "$IP" ]; do sleep 2; done
  until nc -z "$IP" 22 2>/dev/null; do sleep 2; done
  ELAPSED=$(( $(date +%s) - START ))

  echo "Run $i: SSH ready in ${ELAPSED}s at $IP"
  TIMES+=("$ELAPSED")

  tart stop "$TEST_VM"
  wait "$TART_PID" 2>/dev/null || true
  tart delete "$TEST_VM"
  echo ""
done

echo "=== Results ==="
echo "Times (s): ${TIMES[*]}"

SORTED=($(printf '%s\n' "${TIMES[@]}" | sort -n))
MIN=${SORTED[0]}
MEDIAN=${SORTED[1]}
echo "Min: ${MIN}s   Median: ${MEDIAN}s"
echo ""

if [ "$MIN" -le 300 ]; then
  echo "TARGET MET: SSH-ready within 300s on pre-built image."
else
  echo "TARGET MISSED: SSH-ready exceeded 300s."
fi

echo ""
echo "Deleting $SOURCE..."
tart delete "$SOURCE"
echo "Done."
