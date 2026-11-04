#!/usr/bin/env bash
set -euo pipefail

AUTHORIZATION="${1:?authorization JSON required}"
SELF="$(realpath "$0")"
UNIT_PREFIX="${UNIT_PREFIX:-asmp9-dynamic-v067}"
GPU_CLEAN_START_CEILING_MB="${GPU_CLEAN_START_CEILING_MB:-64}"
GPU_TEMPERATURE_LIMIT_C="${GPU_TEMPERATURE_LIMIT_C:-88}"
POLL_SECONDS="${POLL_SECONDS:-0.5}"

eval "$(
python3 - "${AUTHORIZATION}" "${SELF}" <<'PY'
import hashlib
import json
from pathlib import Path
import shlex
import sys

authorization_path = Path(sys.argv[1]).resolve()
self_path = Path(sys.argv[2]).resolve()
authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
if authorization["schema_version"] != "asmp9_physical_dynamic_bridge_authorization_v0_67":
    raise SystemExit("unexpected authorization schema")

def digest(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

wrapper = authorization["hard_cap_wrapper"]
cleanup = authorization["cleanup_script"]
registration_item = authorization["registration"]
if Path(wrapper["path"]).resolve() != self_path or digest(self_path) != wrapper["sha256"]:
    raise SystemExit("executing wrapper differs from authorization")
if digest(cleanup["path"]) != cleanup["sha256"]:
    raise SystemExit("cleanup differs from authorization")
if digest(registration_item["path"]) != registration_item["sha256"]:
    raise SystemExit("registration differs from authorization")
registration = json.loads(Path(registration_item["path"]).read_text(encoding="utf-8"))
if registration["phase"] != "construction" or registration["outcomes_read"] is not False:
    raise SystemExit("authorization is not a prereveal construction registration")
protocol_item = registration["protocol"]
if digest(protocol_item["path"]) != protocol_item["sha256"]:
    raise SystemExit("protocol differs from registration")
protocol = json.loads(Path(protocol_item["path"]).read_text(encoding="utf-8"))
caps = protocol["resource_contract"]
if int(caps["swap_bytes"]) != 0:
    raise SystemExit("nonzero swap is forbidden")

values = {
    "REGISTRATION": registration_item["path"],
    "CLEANUP": cleanup["path"],
    "WRAPPER_OUTPUT": authorization["wrapper_output_dir"],
    "RESULT_DIR": authorization["capture_parameters"]["result_dir"],
    "ANALYSIS_DIR": authorization["capture_parameters"]["analysis_dir"],
    "MEMORY_MB": int(caps["memory_mb"]),
    "MINIMUM_FREE_MEMORY_MB": int(caps["minimum_free_memory_mb"]),
    "CPU_PERCENT": int(caps["cpu_percent"]),
    "IO_MB_S": int(caps["io_mb_s"]),
    "TIMEOUT_SECONDS": int(caps["timeout_seconds"]),
    "GPU_ALLOWANCE_MB": int(caps["gpu_allowance_mb"]),
}
for key, value in values.items():
    print(f"{key}={shlex.quote(str(value))}")
PY
)"

mkdir -p "${WRAPPER_OUTPUT}" "${RESULT_DIR}" "${ANALYSIS_DIR}"
ATTEMPT_ID="$(date -u +%Y%m%dT%H%M%SZ)-$$"
ATTEMPT_DIR="${WRAPPER_OUTPUT}/attempts/${ATTEMPT_ID}"
mkdir -p "${ATTEMPT_DIR}"

FREE_MEMORY_MB="$(awk '/MemAvailable:/ {printf "%d", $2 / 1024}' /proc/meminfo)"
if (( FREE_MEMORY_MB < MINIMUM_FREE_MEMORY_MB )); then
  echo "insufficient free RAM: ${FREE_MEMORY_MB}<${MINIMUM_FREE_MEMORY_MB} MB" >&2
  exit 2
fi
BASELINE_GPU_MB="$(
  nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits |
    head -n 1 | tr -d ' '
)"
if (( BASELINE_GPU_MB > GPU_CLEAN_START_CEILING_MB )); then
  echo "unclean GPU start: ${BASELINE_GPU_MB} MB" >&2
  exit 3
fi
SYSTEMD_STATE="$(systemctl is-system-running 2>/dev/null || true)"
if ! command -v systemd-run >/dev/null \
  || [[ "${SYSTEMD_STATE}" != "running" && "${SYSTEMD_STATE}" != "degraded" ]]; then
  echo "systemd resource controller unavailable" >&2
  exit 4
fi

MOUNT_SOURCE="$(findmnt -T "$(dirname "${RESULT_DIR}")" -no SOURCE | head -n 1)"
PARENT_NAME="$(lsblk -no PKNAME "${MOUNT_SOURCE}" 2>/dev/null | head -n 1 || true)"
if [[ -n "${PARENT_NAME}" ]]; then
  BLOCK_DEVICE="/dev/${PARENT_NAME}"
elif [[ "${MOUNT_SOURCE}" == /dev/* ]]; then
  BLOCK_DEVICE="${MOUNT_SOURCE}"
else
  echo "cannot identify block device for I/O cap: ${MOUNT_SOURCE}" >&2
  exit 5
fi

mapfile -d '' -t RUNNER_COMMAND < <(
  python3 - "${AUTHORIZATION}" <<'PY'
import json
from pathlib import Path
import sys
for item in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["exact_inner_command"]:
    sys.stdout.buffer.write(str(item).encode("utf-8") + b"\0")
PY
)

printf 'timestamp_utc,temperature_c,memory_used_mb,power_w\n' \
  > "${ATTEMPT_DIR}/gpu_telemetry.csv"
date -u +%Y-%m-%dT%H:%M:%SZ > "${ATTEMPT_DIR}/workload_started_utc.txt"

set +e
systemd-run \
  --unit="${UNIT_PREFIX}-runner" \
  --collect \
  --wait \
  --pipe \
  -p "MemoryMax=${MEMORY_MB}M" \
  -p MemorySwapMax=0 \
  -p "CPUQuota=${CPU_PERCENT}%" \
  -p "IOReadBandwidthMax=${BLOCK_DEVICE} ${IO_MB_S}M" \
  -p "IOWriteBandwidthMax=${BLOCK_DEVICE} ${IO_MB_S}M" \
  -p "RuntimeMaxSec=${TIMEOUT_SECONDS}" \
  "${RUNNER_COMMAND[@]}" \
  > "${ATTEMPT_DIR}/runner_stdout.log" \
  2> "${ATTEMPT_DIR}/runner_stderr.log" &
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
  printf '%s\n' "${SAMPLE}" >> "${ATTEMPT_DIR}/gpu_telemetry.csv"
  TEMPERATURE="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $2); print int($2)}')"
  MEMORY_USED="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $3); print int($3)}')"
  (( MEMORY_USED > PEAK_GPU_MB )) && PEAK_GPU_MB="${MEMORY_USED}"
  (( TEMPERATURE > PEAK_TEMPERATURE_C )) && PEAK_TEMPERATURE_C="${TEMPERATURE}"
  GPU_DELTA_MB=$(( MEMORY_USED - BASELINE_GPU_MB ))
  if (( TEMPERATURE >= GPU_TEMPERATURE_LIMIT_C )); then
    ABORT_REASON="hard_temperature_abort"
  elif (( GPU_DELTA_MB > GPU_ALLOWANCE_MB )); then
    ABORT_REASON="gpu_memory_abort"
  fi
  if [[ -n "${ABORT_REASON}" ]]; then
    printf '%s\n' "${ABORT_REASON}" > "${ATTEMPT_DIR}/resource_guard_abort.txt"
    systemctl kill --kill-who=all "${UNIT_PREFIX}-runner.service" 2>/dev/null || true
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

ANALYSIS_STATUS=not_run
if (( RUNNER_STATUS == 0 )); then
  RUNNER_PYTHON="${RUNNER_COMMAND[0]}"
  REPO_ROOT="$(git -C "$(dirname "${SELF}")" rev-parse --show-toplevel)"
  set +e
  systemd-run \
    --unit="${UNIT_PREFIX}-analysis" \
    --collect \
    --wait \
    --pipe \
    -p "MemoryMax=${MEMORY_MB}M" \
    -p MemorySwapMax=0 \
    -p "CPUQuota=${CPU_PERCENT}%" \
    -p "RuntimeMaxSec=${TIMEOUT_SECONDS}" \
    "${RUNNER_PYTHON}" \
    "${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_dynamic_bridge_v0_67/analyze_bridge.py" \
    --registration "${REGISTRATION}" \
    --result-dir "${RESULT_DIR}" \
    --output-dir "${ANALYSIS_DIR}" \
    > "${ATTEMPT_DIR}/analysis_stdout.log" \
    2> "${ATTEMPT_DIR}/analysis_stderr.log"
  ANALYSIS_EXIT=$?
  set -e
  ANALYSIS_STATUS="$([[ ${ANALYSIS_EXIT} -eq 0 ]] && echo completed || echo failed)"
else
  ANALYSIS_EXIT=99
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "${ATTEMPT_DIR}/workload_ended_utc.txt"
bash "${CLEANUP}" "${ATTEMPT_DIR}" "${UNIT_PREFIX}"

export ABORT_REASON BASELINE_GPU_MB PEAK_GPU_MB PEAK_TEMPERATURE_C
export RUNNER_STATUS ANALYSIS_EXIT ANALYSIS_STATUS BLOCK_DEVICE ATTEMPT_ID
python3 - "${ATTEMPT_DIR}/wrapper_summary.json" <<'PY'
import json
import os
from pathlib import Path
import sys

baseline = int(os.environ["BASELINE_GPU_MB"])
payload = {
    "schema_version": "asmp9_prime_wrapper_summary_v0_67",
    "attempt_id": os.environ["ATTEMPT_ID"],
    "status": (
        "completed"
        if int(os.environ["RUNNER_STATUS"]) == 0
        and int(os.environ["ANALYSIS_EXIT"]) == 0
        else "aborted"
    ),
    "abort_reason": os.environ["ABORT_REASON"] or None,
    "runner_exit_code": int(os.environ["RUNNER_STATUS"]),
    "analysis_exit_code": int(os.environ["ANALYSIS_EXIT"]),
    "analysis_status": os.environ["ANALYSIS_STATUS"],
    "block_device": os.environ["BLOCK_DEVICE"],
    "gpu_baseline_used_mb": baseline,
    "peak_gpu_total_used_mb": int(os.environ["PEAK_GPU_MB"]),
    "peak_gpu_delta_mb": int(os.environ["PEAK_GPU_MB"]) - baseline,
    "peak_gpu_temperature_c": int(os.environ["PEAK_TEMPERATURE_C"]),
}
Path(sys.argv[1]).write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
PY

if (( RUNNER_STATUS != 0 )); then
  exit "${RUNNER_STATUS}"
fi
exit "${ANALYSIS_EXIT}"
