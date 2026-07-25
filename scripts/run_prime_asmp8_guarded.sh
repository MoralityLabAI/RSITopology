#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${RUN_ROOT:-/workspace/asmp8_stratified_v0_1}"
OUTPUT_DIR="${OUTPUT_DIR:-${RUN_ROOT}/output}"
UNIT_NAME="${UNIT_NAME:-asmp8-stratified-v0-1}"
GPU_MEMORY_LIMIT_MB="${GPU_MEMORY_LIMIT_MB:-1600}"
GPU_TEMPERATURE_LIMIT_C="${GPU_TEMPERATURE_LIMIT_C:-88}"
POLL_SECONDS="${POLL_SECONDS:-0.5}"
BLOCK_DEVICE="${BLOCK_DEVICE:-/dev/vda}"

if [[ -e "${OUTPUT_DIR}" ]] && find "${OUTPUT_DIR}" -mindepth 1 -print -quit | grep -q .; then
    echo "refusing nonempty output directory: ${OUTPUT_DIR}" >&2
    exit 2
fi

mkdir -p "${OUTPUT_DIR}"
STARTED_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' "${STARTED_UTC}" > "${OUTPUT_DIR}/workload_started_utc.txt"
printf 'timestamp_utc,temperature_c,memory_used_mb,power_w\n' > "${OUTPUT_DIR}/gpu_telemetry.csv"

RUNNER=(
    /usr/bin/python3 "${RUN_ROOT}/scripts/run_qwen08_stratified_audits.py"
    --run-id asmp8-qwen08-stratified-completion-measurement-prime-spot-v0-1-20260725
    --server-path /workspace/llama.cpp/build/bin/llama-server
    --model-path "${RUN_ROOT}/model/Qwen3.5-0.8B-Q4_K_M.gguf"
    --prompt-manifest "${RUN_ROOT}/input/qwen08_controller_task_prompt_manifest_v0_1.json"
    --output-dir "${OUTPUT_DIR}"
    --stability-repeats 32
    --event-every 18
    --context-size 768
    --batch-size 512
    --ubatch-size 256
    --gpu-layers 99
    --threads 2
    --port 8822
    --thermal-pause-temperature 84
    --thermal-resume-temperature 82
    --thermal-poll-seconds 0.5
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
    -p RuntimeMaxSec=7200 \
    -E "LD_LIBRARY_PATH=/workspace/llama.cpp/build/bin" \
    "${RUNNER[@]}" \
    > "${OUTPUT_DIR}/guarded_runner_stdout.log" \
    2> "${OUTPUT_DIR}/guarded_runner_stderr.log" &
SUPERVISOR_PID=$!

while kill -0 "${SUPERVISOR_PID}" 2>/dev/null; do
    SAMPLE="$(nvidia-smi --query-gpu=timestamp,temperature.gpu,memory.used,power.draw --format=csv,noheader,nounits | head -n 1)"
    printf '%s\n' "${SAMPLE}" >> "${OUTPUT_DIR}/gpu_telemetry.csv"

    TEMPERATURE="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $2); print int($2)}')"
    MEMORY_USED="$(printf '%s' "${SAMPLE}" | awk -F, '{gsub(/ /, "", $3); print int($3)}')"
    if (( TEMPERATURE >= GPU_TEMPERATURE_LIMIT_C || MEMORY_USED > GPU_MEMORY_LIMIT_MB )); then
        printf 'resource_guard_abort temperature_c=%s memory_used_mb=%s\n' \
            "${TEMPERATURE}" "${MEMORY_USED}" \
            > "${OUTPUT_DIR}/resource_guard_abort.txt"
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

ENDED_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '%s\n' "${ENDED_UTC}" > "${OUTPUT_DIR}/workload_ended_utc.txt"
printf '%s\n' "${RUNNER_STATUS}" > "${OUTPUT_DIR}/guarded_runner_exit_code.txt"

exit "${RUNNER_STATUS}"
