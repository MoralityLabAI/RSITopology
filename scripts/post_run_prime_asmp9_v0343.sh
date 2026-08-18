#!/usr/bin/env bash
set -euo pipefail

OUTPUT_DIR="${1:?output directory required}"
UNIT_NAME="${2:?systemd unit name required}"
mkdir -p "${OUTPUT_DIR}"

systemctl kill --kill-who=all "${UNIT_NAME}.service" 2>/dev/null || true
sleep 1

GPU_APPS="$(
  nvidia-smi \
    --query-compute-apps=pid,process_name,used_memory \
    --format=csv,noheader,nounits 2>/dev/null || true
)"
GPU_STATE="$(
  nvidia-smi \
    --query-gpu=temperature.gpu,memory.used,utilization.gpu \
    --format=csv,noheader,nounits 2>/dev/null | head -n 1 || true
)"
MEM_AVAILABLE_KB="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
OWNED_UNIT_ACTIVE=false
if systemctl is-active --quiet "${UNIT_NAME}.service"; then
  OWNED_UNIT_ACTIVE=true
fi

export GPU_APPS GPU_STATE MEM_AVAILABLE_KB OWNED_UNIT_ACTIVE
python3 - "${OUTPUT_DIR}/cleanup_summary.json" <<'PY'
import json
import os
from pathlib import Path
import sys

apps = [line.strip() for line in os.environ["GPU_APPS"].splitlines() if line.strip()]
payload = {
    "schema_version": "asmp9_prime_cleanup_summary_v0_34_3",
    "cleanup_passed": not apps and os.environ["OWNED_UNIT_ACTIVE"] == "false",
    "lingering_gpu_compute_apps": apps,
    "owned_unit_active_after_cleanup": os.environ["OWNED_UNIT_ACTIVE"] == "true",
    "gpu_state_after_cleanup": os.environ["GPU_STATE"].strip(),
    "memory_available_kb_after_cleanup": int(os.environ["MEM_AVAILABLE_KB"]),
}
Path(sys.argv[1]).write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
PY

