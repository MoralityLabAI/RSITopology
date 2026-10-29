#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${RUN_ROOT:-/workspace/asmp9_physical_v0343}"
REPO_ROOT="${REPO_ROOT:-${RUN_ROOT}/repo}"
OUTPUT_DIR="${OUTPUT_DIR:-${RUN_ROOT}/output}"
REGISTRATION="${REGISTRATION:-${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/burned_pilot_registration_v0_34_3.json}"
UNIT_NAME="${UNIT_NAME:-asmp9-physical-v0343}"
GPU_MEMORY_LIMIT_MB="${GPU_MEMORY_LIMIT_MB:-1600}"
GPU_TEMPERATURE_LIMIT_C="${GPU_TEMPERATURE_LIMIT_C:-88}"
GPU_CLEAN_START_CEILING_MB="${GPU_CLEAN_START_CEILING_MB:-64}"
POLL_SECONDS="${POLL_SECONDS:-0.5}"

if [[ -e "${OUTPUT_DIR}" ]] && find "${OUTPUT_DIR}" -mindepth 1 -print -quit | grep -q .; then
  echo "refusing nonempty output directory: ${OUTPUT_DIR}" >&2
  exit 2
fi
mkdir -p "${OUTPUT_DIR}"

WRAPPER_SHA256="$(sha256sum "$0" | awk '{print $1}')"
BASELINE_GPU_MB="$(
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits |
    head -n 1 | tr -d ' '
)"
if (( BASELINE_GPU_MB > GPU_CLEAN_START_CEILING_MB )); then
  echo "unclean GPU start: ${BASELINE_GPU_MB} MB" >&2
  exit 3
fi

MOUNT_SOURCE="$(findmnt -no SOURCE "${RUN_ROOT}" | head -n 1)"
PARENT_NAME="$(lsblk -no PKNAME "${MOUNT_SOURCE}" 2>/dev/null | head -n 1 || true)"
if [[ -n "${PARENT_NAME}" ]]; then
  BLOCK_DEVICE="/dev/${PARENT_NAME}"
else
  BLOCK_DEVICE="${MOUNT_SOURCE}"
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "${OUTPUT_DIR}/workload_started_utc.txt"
printf 'timestamp_utc,temperature_c,memory_used_mb,power_w\n' \
  > "${OUTPUT_DIR}/gpu_telemetry.csv"

RUNNER=(
  /usr/bin/python3
  "${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/run_burned_pilot_prime_v0_34_3.py"
  --registration "${REGISTRATION}"
  --output-dir "${OUTPUT_DIR}"
  --execution-class burned_pilot
)

set +e
systemd-run \
  --unit="${UNIT_NAME}" \
  --collect \
  --wait \
  --pipe \
  -p MemoryMax=4096M \
  -p MemorySwapMax=0 \
  -p CPUQuota=50% \
  -p "IOReadBandwidthMax=${BLOCK_DEVICE} 50M" \
  -p "IOWriteBandwidthMax=${BLOCK_DEVICE} 50M" \
  -p RuntimeMaxSec=1800 \
  -E "LD_LIBRARY_PATH=/workspace/llama.cpp/build-sm89/bin" \
  -E "ASMP9_V034_HARD_CAP_ACTIVE=${WRAPPER_SHA256}" \
  "${RUNNER[@]}" \
  > "${OUTPUT_DIR}/guarded_runner_stdout.log" \
  2> "${OUTPUT_DIR}/guarded_runner_stderr.log" &
SUPERVISOR_PID=$!

PEAK_GPU_MB="${BASELINE_GPU_MB}"
PEAK_TEMPERATURE_C=0
ABORT_REASON=""
while kill -0 "${SUPERVISOR_PID}" 2>/dev/null; do
  SAMPLE="$(
    nvidia-smi \
      --query-gpu=timestamp,temperature.gpu,memory.used,power.draw \
      --format=csv,noheader,nounits | head -n 1
  )"
  printf '%s\n' "${SAMPLE}" >> "${OUTPUT_DIR}/gpu_telemetry.csv"
  TEMPERATURE="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $2); print int($2)}')"
  MEMORY_USED="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $3); print int($3)}')"
  (( MEMORY_USED > PEAK_GPU_MB )) && PEAK_GPU_MB="${MEMORY_USED}"
  (( TEMPERATURE > PEAK_TEMPERATURE_C )) && PEAK_TEMPERATURE_C="${TEMPERATURE}"
  GPU_DELTA_MB=$(( MEMORY_USED - BASELINE_GPU_MB ))

  if (( TEMPERATURE >= GPU_TEMPERATURE_LIMIT_C )); then
    ABORT_REASON="hard_temperature_abort"
  elif (( GPU_DELTA_MB > GPU_MEMORY_LIMIT_MB )); then
    ABORT_REASON="gpu_memory_abort"
  fi
  if [[ -n "${ABORT_REASON}" ]]; then
    printf '%s\n' "${ABORT_REASON}" > "${OUTPUT_DIR}/resource_guard_abort.txt"
    systemctl kill --kill-who=all "${UNIT_NAME}.service" 2>/dev/null || true
    kill "${SUPERVISOR_PID}" 2>/dev/null || true
    wait "${SUPERVISOR_PID}" 2>/dev/null
    RUNNER_STATUS=90
    break
  fi
  sleep "${POLL_SECONDS}"
done

if [[ -z "${RUNNER_STATUS:-}" ]]; then
  wait "${SUPERVISOR_PID}"
  RUNNER_STATUS=$?
fi
set -e

date -u +%Y-%m-%dT%H:%M:%SZ > "${OUTPUT_DIR}/workload_ended_utc.txt"
printf '%s\n' "${RUNNER_STATUS}" > "${OUTPUT_DIR}/guarded_runner_exit_code.txt"

"${REPO_ROOT}/scripts/post_run_prime_asmp9_v0343.sh" \
  "${OUTPUT_DIR}" "${UNIT_NAME}"

export ABORT_REASON BASELINE_GPU_MB PEAK_GPU_MB PEAK_TEMPERATURE_C
export RUNNER_STATUS WRAPPER_SHA256 BLOCK_DEVICE
python3 - "${OUTPUT_DIR}/wrapper_summary.json" <<'PY'
import json
import os
from pathlib import Path
import sys

baseline = int(os.environ["BASELINE_GPU_MB"])
peak = int(os.environ["PEAK_GPU_MB"])
payload = {
    "schema_version": "asmp9_prime_wrapper_summary_v0_34_3",
    "status": "completed" if int(os.environ["RUNNER_STATUS"]) == 0 else "aborted",
    "abort_reason": os.environ["ABORT_REASON"] or None,
    "exit_code": int(os.environ["RUNNER_STATUS"]),
    "wrapper_sha256": os.environ["WRAPPER_SHA256"],
    "block_device": os.environ["BLOCK_DEVICE"],
    "gpu_baseline_used_mb": baseline,
    "peak_gpu_total_used_mb": peak,
    "peak_gpu_delta_mb": peak - baseline,
    "peak_gpu_temperature_c": int(os.environ["PEAK_TEMPERATURE_C"]),
    "caps": {
        "memory_mb": 4096,
        "swap_bytes": 0,
        "cpu_percent": 50,
        "io_mb_s": 50,
        "timeout_seconds": 1800,
        "gpu_allowance_mb": 1600,
        "gpu_clean_start_ceiling_mb": 64,
        "hard_abort_temperature_c": 88,
    },
}
Path(sys.argv[1]).write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
PY

exit "${RUNNER_STATUS}"

