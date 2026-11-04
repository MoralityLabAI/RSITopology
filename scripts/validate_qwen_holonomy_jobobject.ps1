param(
  [string]$OutputDir = "artifacts\hard_cap_validation\qwen_holonomy_jobobject_v0_1"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$wrapper = (Resolve-Path (Join-Path $PSScriptRoot "run_qwen_holonomy_jobobject.ps1")).Path
$probe = (Resolve-Path (Join-Path $PSScriptRoot "qwen_holonomy_cap_probe.py")).Path
$cleanup = "C:\Users\patri\.codex\skills\hrm-trainer\scripts\post_run_memory_cleanup.ps1"
$python = (Get-Command python).Source
$hostExe = (Get-Process -Id $PID).Path
$out = [System.IO.Path]::GetFullPath((Join-Path $root $OutputDir))
New-Item -ItemType Directory -Force -Path $out | Out-Null

function New-ProbeSpec([string]$Mode, [int]$MemoryMb, [int]$CpuPct, [int]$IoMbS, [int]$TimeoutSeconds) {
  $runDir = Join-Path $out $Mode
  New-Item -ItemType Directory -Force -Path $runDir | Out-Null
  $payload = Join-Path $runDir "probe_payload.bin"
  $spec = [ordered]@{
    schema_version = "qwen_holonomy_jobobject_probe_v0_1"
    run_id = "qwen-holonomy-cap-probe-$Mode"
    wrapper_output_dir = $runDir
    checkpoint_strategy = "one_probe"
    resource_caps = [ordered]@{
      memory_mb = $MemoryMb
      cpu_percent = $CpuPct
      io_mb_s = $IoMbS
      timeout_seconds = $TimeoutSeconds
      gpu_allowance_mb = 1
      checkpoint_every_seconds = 1
      swap_bytes = 0
    }
    cleanup_script = [ordered]@{
      path = $cleanup
      sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $cleanup).Hash.ToLower()
    }
    exact_inner_command = @($python, $probe, "--mode", $Mode, "--output", $payload)
  }
  $path = Join-Path $runDir "probe_spec.json"
  $spec | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $path -Encoding UTF8
  return $path
}

function Invoke-Probe([string]$Mode, [int]$MemoryMb, [int]$CpuPct, [int]$IoMbS, [int]$TimeoutSeconds) {
  $spec = New-ProbeSpec $Mode $MemoryMb $CpuPct $IoMbS $TimeoutSeconds
  & $hostExe -NoProfile -File $wrapper -RunSpecPath $spec | Out-Null
  $summaryPath = Join-Path (Split-Path $spec -Parent) "wrapper_summary.json"
  if (-not (Test-Path -LiteralPath $summaryPath)) { throw "Missing wrapper summary for $Mode" }
  return (Get-Content $summaryPath -Raw | ConvertFrom-Json)
}

$success = Invoke-Probe "success" 128 50 50 10
$memory = Invoke-Probe "memory" 96 50 50 15
$cpu = Invoke-Probe "cpu" 128 5 50 15
$io = Invoke-Probe "io" 256 50 2 15
$timeout = Invoke-Probe "timeout" 128 50 50 2

$checks = [ordered]@{
  success_path = ($success.status -eq "completed" -and $success.cleanup_passed)
  memory_cap_configured = ($memory.memory_cap_set -and $memory.cpu_cap_set -and [UInt64]$memory.queried_memory_limit_bytes -eq 96MB)
  memory_probe_terminated = ($memory.status -eq "failed" -and $memory.abort_reason -like "exit_code_*" -and [double]$memory.elapsed_seconds -lt 15 -and -not (Test-Path (Join-Path $out "memory\probe_payload.bin")))
  memory_probe_stayed_at_cap = ([double]$memory.peak_ram_mb -eq 0 -or [double]$memory.peak_ram_mb -le 120)
  cpu_cap_configured = ($cpu.memory_cap_set -and $cpu.cpu_cap_set -and [UInt32]$cpu.queried_cpu_rate -eq 500)
  cpu_probe_completed = ($cpu.status -eq "completed" -and $cpu.cleanup_passed)
  cpu_observed_below_margin = ([double]$cpu.cpu_pct -le 7.5)
  io_monitor_aborted = ($io.status -eq "aborted" -and $io.abort_reason -eq "sustained_io_cap_exceeded")
  timeout_aborted = ($timeout.status -eq "aborted" -and $timeout.abort_reason -eq "timeout")
  all_cleanup_passed = ($success.cleanup_passed -and $memory.cleanup_passed -and $cpu.cleanup_passed -and $io.cleanup_passed -and $timeout.cleanup_passed)
}
$passed = @($checks.Values | Where-Object { $_ -ne $true }).Count -eq 0
$receipt = [ordered]@{
  schema_version = "qwen_holonomy_hard_cap_validation_v0_1"
  hard_cap_validation_status = $(if ($passed) { "passed" } else { "failed" })
  created_utc = [DateTime]::UtcNow.ToString("o")
  wrapper = [ordered]@{path=$wrapper;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $wrapper).Hash.ToLower()}
  probe = [ordered]@{path=$probe;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $probe).Hash.ToLower()}
  cleanup = [ordered]@{path=$cleanup;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $cleanup).Hash.ToLower()}
  checks = $checks
  summaries = [ordered]@{
    success = $success
    memory = $memory
    cpu = $cpu
    io = $io
    timeout = $timeout
  }
  interpretation = "Windows Job Objects hard-cap aggregate/process commit and CPU. I/O and timeout are monitored fail-closed. The run registers zero deliberate swap use; Windows does not expose a process-local hard no-pagefile control through Job Objects."
}
$receiptPath = Join-Path $out "hard_cap_validation_receipt.json"
$receipt | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
$receipt | ConvertTo-Json -Depth 12
if (-not $passed) { exit 1 }
