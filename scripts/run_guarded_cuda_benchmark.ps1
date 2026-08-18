param(
  [Parameter(Mandatory=$true)][string]$RunSpecPath,
  [Parameter(Mandatory=$true)][string]$GuardOutputDir,
  [double]$MaximumStartTemperatureC = 65.0,
  [double]$AbortTemperatureC = 78.0,
  [double]$MinimumFreeGpuMb = 2500.0,
  [double]$MinimumFreePhysicalMb = 8192.0,
  [int]$PollMilliseconds = 500
)

$ErrorActionPreference = "Stop"
$specPath = (Resolve-Path -LiteralPath $RunSpecPath).Path
$guardDir = [System.IO.Path]::GetFullPath($GuardOutputDir)
New-Item -ItemType Directory -Force -Path $guardDir | Out-Null
$eventsPath = Join-Path $guardDir "guard_events.jsonl"
$summaryPath = Join-Path $guardDir "guard_summary.json"
$hostStdout = Join-Path $guardDir "guarded_wrapper_stdout.txt"
$hostStderr = Join-Path $guardDir "guarded_wrapper_stderr.txt"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$wrapper = Join-Path $PSScriptRoot "run_qwen_holonomy_jobobject.ps1"
$spec = Get-Content -LiteralPath $specPath -Raw | ConvertFrom-Json
$ownedPidPath = Join-Path ([string]$spec.wrapper_output_dir) "owned_pids.json"
$wrapperSummaryPath = Join-Path ([string]$spec.wrapper_output_dir) "wrapper_summary.json"

function Write-GuardEvent([hashtable]$Value) {
  $Value.ts_utc = [DateTime]::UtcNow.ToString("o")
  Add-Content -LiteralPath $eventsPath -Value ($Value | ConvertTo-Json -Compress -Depth 6) -Encoding UTF8
}

function Get-GpuSample {
  $line = & nvidia-smi --query-gpu=temperature.gpu,power.draw,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits 2>$null |
    Select-Object -First 1
  if (-not $line) { throw "nvidia-smi returned no GPU sample" }
  $parts = @($line -split "," | ForEach-Object { $_.Trim() })
  if ($parts.Count -lt 5) { throw "nvidia-smi GPU sample is incomplete" }
  return [ordered]@{
    temperature_c = [double]$parts[0]
    power_w = [double]$parts[1]
    memory_used_mb = [double]$parts[2]
    memory_free_mb = [double]$parts[3]
    utilization_percent = [double]$parts[4]
  }
}

$os = Get-CimInstance Win32_OperatingSystem
$freePhysicalMb = [double]$os.FreePhysicalMemory / 1024.0
$initial = Get-GpuSample
$started = Get-Date
$status = "preflight_failed"
$abortReason = $null
$wrapperExitCode = $null
$maxTemperature = [double]$initial.temperature_c
$maxPower = [double]$initial.power_w
$maxMemoryUsed = [double]$initial.memory_used_mb
$maxMemoryDelta = 0.0
$maxUtilization = [double]$initial.utilization_percent
$wrapperProcess = $null

try {
  Write-GuardEvent @{
    event = "preflight"
    run_id = [string]$spec.run_id
    gpu = $initial
    free_physical_mb = [math]::Round($freePhysicalMb, 3)
    last_boot_time = $os.LastBootUpTime.ToString("o")
  }
  if ([double]$initial.temperature_c -gt $MaximumStartTemperatureC) {
    throw "preflight_temperature_exceeded"
  }
  if ([double]$initial.memory_free_mb -lt $MinimumFreeGpuMb) {
    throw "preflight_free_gpu_below_minimum"
  }
  if ($freePhysicalMb -lt $MinimumFreePhysicalMb) {
    throw "preflight_free_physical_below_minimum"
  }
  $arguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $wrapper,
    "-RunSpecPath", $specPath
  )
  $wrapperProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden `
    -WorkingDirectory $repoRoot -RedirectStandardOutput $hostStdout -RedirectStandardError $hostStderr
  $status = "running"
  Write-GuardEvent @{event="wrapper_started";wrapper_pid=$wrapperProcess.Id}
  while (-not $wrapperProcess.HasExited) {
    Start-Sleep -Milliseconds $PollMilliseconds
    $wrapperProcess.Refresh()
    $sample = Get-GpuSample
    $maxTemperature = [math]::Max($maxTemperature, [double]$sample.temperature_c)
    $maxPower = [math]::Max($maxPower, [double]$sample.power_w)
    $maxMemoryUsed = [math]::Max($maxMemoryUsed, [double]$sample.memory_used_mb)
    $maxMemoryDelta = [math]::Max(
      $maxMemoryDelta,
      [math]::Max(0.0, [double]$sample.memory_used_mb - [double]$initial.memory_used_mb)
    )
    $maxUtilization = [math]::Max($maxUtilization, [double]$sample.utilization_percent)
    Write-GuardEvent @{event="sample";gpu=$sample}
    if ([double]$sample.temperature_c -ge $AbortTemperatureC) {
      $abortReason = "gpu_temperature_abort"
    }
    if ($abortReason) {
      if (Test-Path -LiteralPath $ownedPidPath) {
        $owned = Get-Content -LiteralPath $ownedPidPath -Raw | ConvertFrom-Json
        Stop-Process -Id ([int]$owned.root_pid) -Force -ErrorAction SilentlyContinue
      }
      break
    }
  }
  $wrapperProcess.WaitForExit()
  $wrapperProcess.Refresh()
  $wrapperExitCode = $wrapperProcess.ExitCode
  if ($null -eq $wrapperExitCode -and (Test-Path -LiteralPath $wrapperSummaryPath)) {
    $wrapperReceipt = Get-Content -LiteralPath $wrapperSummaryPath -Raw | ConvertFrom-Json
    if ($null -ne $wrapperReceipt.exit_code) {
      $wrapperExitCode = [int]$wrapperReceipt.exit_code
      Write-GuardEvent @{
        event = "wrapper_exit_code_recovered"
        source = "wrapper_summary"
        wrapper_exit_code = $wrapperExitCode
      }
    }
  }
  if ($abortReason) {
    $status = "aborted"
  } elseif ($wrapperExitCode -eq 0) {
    $status = "completed"
  } else {
    $status = "failed"
    $abortReason = "wrapper_exit_$wrapperExitCode"
  }
} catch {
  $status = "preflight_failed"
  $abortReason = $_.Exception.Message
} finally {
  if ($wrapperProcess -and -not $wrapperProcess.HasExited) {
    Stop-Process -Id $wrapperProcess.Id -Force -ErrorAction SilentlyContinue
  }
  $final = Get-GpuSample
  $summary = [ordered]@{
    schema_version = "guarded_cuda_benchmark_summary_v0_1"
    run_id = [string]$spec.run_id
    status = $status
    abort_reason = $abortReason
    wrapper_exit_code = $wrapperExitCode
    thresholds = [ordered]@{
      maximum_start_temperature_c = $MaximumStartTemperatureC
      abort_temperature_c = $AbortTemperatureC
      minimum_free_gpu_mb = $MinimumFreeGpuMb
      minimum_free_physical_mb = $MinimumFreePhysicalMb
    }
    initial_gpu = $initial
    final_gpu = $final
    free_physical_mb_at_start = [math]::Round($freePhysicalMb, 3)
    max_temperature_c = $maxTemperature
    max_power_w = $maxPower
    max_memory_used_mb = $maxMemoryUsed
    max_memory_delta_mb = $maxMemoryDelta
    max_utilization_percent = $maxUtilization
    elapsed_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
    wrapper_summary = $wrapperSummaryPath
    wrapper_summary_exists = (Test-Path -LiteralPath $wrapperSummaryPath)
  }
  $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
  Write-GuardEvent @{event=$status;abort_reason=$abortReason;summary=$summaryPath}
  $summary | ConvertTo-Json -Depth 8
}

if ($status -eq "completed") { exit 0 }
exit 3
