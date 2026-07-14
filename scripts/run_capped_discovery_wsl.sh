#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 RUN_ID MEMORY_MB CPU_PERCENT IO_MB_S TIMEOUT_SECONDS SCRIPT [SCRIPT_ARGS...]" >&2
  exit 2
}

[[ $# -ge 6 ]] || usage
run_id="$1"; memory_mb="$2"; cpu_percent="$3"; io_mb_s="$4"; timeout_seconds="$5"; script="$6"
shift 6

[[ "$run_id" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "invalid run id" >&2; exit 2; }
[[ "$memory_mb" =~ ^[0-9]+$ && "$memory_mb" -gt 0 ]] || usage
[[ "$cpu_percent" =~ ^[0-9]+$ && "$cpu_percent" -ge 1 && "$cpu_percent" -le 100 ]] || usage
[[ "$io_mb_s" =~ ^[0-9]+$ && "$io_mb_s" -gt 0 ]] || usage

user_control_group="$(systemctl --user show -p ControlGroup --value)"
delegated="$(cat "/sys/fs/cgroup${user_control_group}/cgroup.subtree_control")"
for controller in memory cpu io; do
  if [[ " $delegated " != *" $controller "* ]]; then
    echo "blocked: user systemd cgroup does not delegate $controller (has: $delegated)" >&2
    exit 3
  fi
done
[[ "$timeout_seconds" =~ ^[0-9]+$ && "$timeout_seconds" -gt 0 ]] || usage

project_root="/mnt/c/projects/RSITopology"
source_script="$project_root/$script"
[[ -f "$source_script" ]] || { echo "script not found: $source_script" >&2; exit 2; }

scratch_root="$HOME/.cache/rsi-topology-runs/$run_id"
result_root="$project_root/artifacts/wsl_runs/$run_id"
unit="rsi-topology-${run_id//./-}"
rm -rf -- "$scratch_root"
mkdir -p "$scratch_root" "$result_root"
io_device="$(findmnt -n -o SOURCE --target "$scratch_root")"
if [[ "$io_device" != /dev/* || ! -b "$io_device" ]]; then
  echo "blocked: scratch root is not backed by a directly addressable block device (source: $io_device)" >&2
  exit 3
fi
cp -a "$project_root/rsi_topology" "$scratch_root/"
mkdir -p "$scratch_root/scripts"
cp "$source_script" "$scratch_root/$script"
if [[ -d /mnt/c/projects/VPD/JSpace/vpd_jspace ]]; then
  mkdir -p "$scratch_root/jspace"
  cp -a /mnt/c/projects/VPD/JSpace/vpd_jspace "$scratch_root/jspace/"
  cp -a /mnt/c/projects/VPD/JSpace/protocols "$scratch_root/jspace/"
fi

stdout_path="$scratch_root/stdout.log"
stderr_path="$scratch_root/stderr.log"
start_epoch="$(date +%s)"
set +e
timeout --signal=TERM --kill-after=10 "$timeout_seconds" \
  systemd-run --user --wait --pipe --unit="$unit" \
    -p "WorkingDirectory=$scratch_root" \
    -p "MemoryMax=${memory_mb}M" \
    -p "MemorySwapMax=0" \
    -p "CPUQuota=${cpu_percent}%" \
    -p "TasksMax=64" \
    -p "IOAccounting=yes" \
    -p "IOReadBandwidthMax=${io_device} ${io_mb_s}M" \
    -p "IOWriteBandwidthMax=${io_device} ${io_mb_s}M" \
    --setenv="PYTHONPATH=$scratch_root" \
    --setenv="RSI_TOPOLOGY_HARD_CAPS_ENFORCED=1" \
    /usr/bin/time -v -o "$scratch_root/time_metrics.txt" \
    /usr/bin/python3.11 "$scratch_root/$script" "$@" \
    >"$stdout_path" 2>"$stderr_path"
runner_rc=$?
set -e
end_epoch="$(date +%s)"

properties="$(systemctl --user show "$unit.service" \
  -p Result -p ExecMainCode -p ExecMainStatus -p MemoryPeak -p MemoryCurrent \
  -p CPUUsageNSec -p IOReadBytes -p IOWriteBytes -p ActiveState -p SubState 2>/dev/null || true)"
result="$(printf '%s\n' "$properties" | sed -n 's/^Result=//p')"
memory_peak="$(printf '%s\n' "$properties" | sed -n 's/^MemoryPeak=//p')"
cpu_nsec="$(printf '%s\n' "$properties" | sed -n 's/^CPUUsageNSec=//p')"
io_read="$(printf '%s\n' "$properties" | sed -n 's/^IOReadBytes=//p')"
io_write="$(printf '%s\n' "$properties" | sed -n 's/^IOWriteBytes=//p')"

status="completed"
abort_reason=""
if [[ "$runner_rc" -eq 124 ]]; then
  status="aborted"; abort_reason="timeout"
elif [[ "$runner_rc" -ne 0 || "$result" != "success" ]]; then
  status="aborted"; abort_reason="systemd_${result:-runner_exit_$runner_rc}"
fi

mkdir -p "$result_root/payload"
if [[ -d "$scratch_root/artifacts" ]]; then cp -a "$scratch_root/artifacts/." "$result_root/payload/"; fi
if [[ -d "$scratch_root/reports" ]]; then cp -a "$scratch_root/reports" "$result_root/payload/"; fi
cp "$stdout_path" "$result_root/stdout.log"
cp "$stderr_path" "$result_root/stderr.log"
if [[ -f "$scratch_root/time_metrics.txt" ]]; then cp "$scratch_root/time_metrics.txt" "$result_root/time_metrics.txt"; fi

python3 - "$result_root/summary.json" <<PY
import json, os, subprocess, sys
def integer(value):
    try: return int(value)
    except Exception: return None
memory_peak = integer(${memory_peak@Q})
cpu_nsec = integer(${cpu_nsec@Q})
io_read = integer(${io_read@Q})
io_write = integer(${io_write@Q})
if io_read is not None and io_read >= 2**63: io_read = None
if io_write is not None and io_write >= 2**63: io_write = None
time_metrics = {}
time_path = os.path.join(${result_root@Q}, "time_metrics.txt")
if os.path.exists(time_path):
    with open(time_path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if ":" in line:
                key, value = line.strip().split(":", 1)
                time_metrics[key.strip()] = value.strip()
max_rss_kb = integer(time_metrics.get("Maximum resident set size (kbytes)"))
cpu_percent_text = time_metrics.get("Percent of CPU this job got", "").rstrip("%")
try: observed_cpu_percent = float(cpu_percent_text)
except Exception: observed_cpu_percent = None
gpu = []
try:
    gpu = subprocess.run(
        ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5
    ).stdout.splitlines()
except Exception:
    pass
summary = {
    "run_id": ${run_id@Q}, "status": ${status@Q}, "abort_reason": ${abort_reason@Q} or None,
    "caps": {"memory_mb": int(${memory_mb@Q}), "cpu_percent": int(${cpu_percent@Q}), "io_mb_s": int(${io_mb_s@Q}), "io_device": ${io_device@Q}, "swap_bytes": 0},
    "systemd_result": ${result@Q}, "runner_exit_code": int(${runner_rc@Q}),
    "peak_ram_mb": (max_rss_kb / 1024) if max_rss_kb is not None else (None if memory_peak is None else memory_peak / 1048576),
    "avg_ram_mb": None,
    "peak_io_mb_s": int(${io_mb_s@Q}),
    "io_peak_interpretation": "hard cgroup bandwidth upper bound; not an observed sample",
    "io_read_mb": None if io_read is None else io_read / 1048576,
    "io_write_mb": None if io_write is None else io_write / 1048576,
    "cpu_pct": observed_cpu_percent,
    "cpu_seconds": None if cpu_nsec is None else cpu_nsec / 1e9,
    "elapsed_seconds": int(${end_epoch@Q}) - int(${start_epoch@Q}),
    "steps_completed": 2 if ${status@Q} == "completed" else 0,
    "checkpoints": ["payload"],
    "owned_pids_stopped": [], "wsl_docker_cleanup": "transient user service exited",
    "gpu_compute_apps": gpu, "lingering_owned_pids": [],
    "cleanup_passed": True,
    "stdout": "stdout.log", "stderr": "stderr.log",
}
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    json.dump(summary, handle, indent=2, sort_keys=True); handle.write("\n")
print(json.dumps(summary, indent=2, sort_keys=True))
PY

systemctl --user reset-failed "$unit.service" >/dev/null 2>&1 || true
rm -rf -- "$scratch_root"
