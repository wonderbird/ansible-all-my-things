#!/usr/bin/env bash
# Spike B — Step 1: clone OCI image, wait for cloud-init, stop.
# Run on macOS host. Takes ~17 min (cloud-init on first boot).
# Output: stopped spike-source VM ready for step 2.
set -euo pipefail

VM="spike-source"
IMAGE="ghcr.io/cirruslabs/ubuntu:24.04"

cleanup() {
  echo "Interrupted — cleaning up $VM..."
  tart stop "$VM" 2>/dev/null || true
  tart delete "$VM" 2>/dev/null || true
  exit 1
}
trap cleanup INT TERM

echo "=== Spike B Step 1: build pre-built source image ==="
echo "Cloning $IMAGE → $VM ..."
tart clone "$IMAGE" "$VM"

echo "Starting $VM (cloud-init will run — expect ~17 min)..."
START=$(date +%s)
tart run "$VM" --no-graphics &
TART_PID=$!

echo "Polling for IP..."
until IP=$(tart ip "$VM" 2>/dev/null) && [ -n "$IP" ]; do sleep 5; done
echo "Got IP $IP after $(( $(date +%s) - START ))s"

echo "Polling for SSH on port 22..."
until nc -z "$IP" 22 2>/dev/null; do sleep 5; done
echo "SSH ready in $(( $(date +%s) - START ))s at $IP"

echo "Stopping $VM..."
tart stop "$VM"
wait "$TART_PID" 2>/dev/null || true

echo ""
echo "=== Step 1 complete. Run step2-measure-clones.sh next. ==="
