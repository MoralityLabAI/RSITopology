#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${RUN_ROOT:-/workspace/asmp9_physical_v0343}"
REPO_ROOT="${REPO_ROOT:-${RUN_ROOT}/repo}"
CAPTURE_DIR="${CAPTURE_DIR:-${RUN_ROOT}/output}"
ANALYSIS_DIR="${ANALYSIS_DIR:-${RUN_ROOT}/analysis}"
REGISTRATION="${REGISTRATION:-${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/burned_pilot_registration_v0_34_4.json}"
UNIT_NAME="${UNIT_NAME:-asmp9-analysis-v0344}"

if [[ ! -s "${CAPTURE_DIR}/pilot_records.jsonl" ]] ||
   [[ ! -s "${CAPTURE_DIR}/summary.json" ]]; then
  echo "complete capture inputs are absent" >&2
  exit 2
fi
if [[ -e "${ANALYSIS_DIR}" ]] &&
   find "${ANALYSIS_DIR}" -mindepth 1 -print -quit | grep -q .; then
  echo "refusing nonempty analysis directory: ${ANALYSIS_DIR}" >&2
  exit 3
fi
mkdir -p "${ANALYSIS_DIR}"

WRAPPER_SHA256="$(sha256sum "$0" | awk '{print $1}')"
MOUNT_SOURCE="$(findmnt -T "${RUN_ROOT}" -no SOURCE | head -n 1)"
PARENT_NAME="$(lsblk -no PKNAME "${MOUNT_SOURCE}" 2>/dev/null | head -n 1 || true)"
if [[ -n "${PARENT_NAME}" ]]; then
  BLOCK_DEVICE="/dev/${PARENT_NAME}"
else
  BLOCK_DEVICE="${MOUNT_SOURCE}"
fi

date -u +%Y-%m-%dT%H:%M:%SZ > "${ANALYSIS_DIR}/analysis_started_utc.txt"
RUNNER=(
  /usr/bin/python3
  "${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_acquisition_v0_34/analyze_burned_pilot_prime_v0_34_4.py"
  --registration "${REGISTRATION}"
  --output-dir "${CAPTURE_DIR}"
  --analysis-json "${ANALYSIS_DIR}/BURNED_PILOT_ANALYSIS_v0_34_4.json"
  --report "${ANALYSIS_DIR}/BURNED_PILOT_REPORT_v0_34_4.md"
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
  -p RuntimeMaxSec=600 \
  -E "ASMP9_V034_ANALYSIS_CAP_ACTIVE=${WRAPPER_SHA256}" \
  "${RUNNER[@]}" \
  > "${ANALYSIS_DIR}/guarded_analysis_stdout.log" \
  2> "${ANALYSIS_DIR}/guarded_analysis_stderr.log"
ANALYSIS_STATUS=$?
set -e

date -u +%Y-%m-%dT%H:%M:%SZ > "${ANALYSIS_DIR}/analysis_ended_utc.txt"
printf '%s\n' "${ANALYSIS_STATUS}" \
  > "${ANALYSIS_DIR}/guarded_analysis_exit_code.txt"

export ANALYSIS_STATUS WRAPPER_SHA256 BLOCK_DEVICE
python3 - "${ANALYSIS_DIR}/analysis_wrapper_summary.json" <<'PY'
import json
import os
from pathlib import Path
import resource
import sys

payload = {
    "schema_version": "asmp9_prime_analysis_wrapper_summary_v0_34_4",
    "status": "completed" if int(os.environ["ANALYSIS_STATUS"]) == 0 else "aborted",
    "exit_code": int(os.environ["ANALYSIS_STATUS"]),
    "wrapper_sha256": os.environ["WRAPPER_SHA256"],
    "block_device": os.environ["BLOCK_DEVICE"],
    "process_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    "caps": {
        "memory_mb": 4096,
        "swap_bytes": 0,
        "cpu_percent": 50,
        "io_mb_s": 50,
        "timeout_seconds": 600,
    },
}
Path(sys.argv[1]).write_text(
    json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n",
    encoding="utf-8",
)
PY

exit "${ANALYSIS_STATUS}"
