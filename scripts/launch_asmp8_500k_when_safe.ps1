param(
  [int]$MaximumWaitSeconds = 21600,
  [int]$PollSeconds = 30,
  [double]$MaximumStartTemperatureC = 65.0,
  [double]$GuardMaximumStartTemperatureC = -1.0,
  [double]$AbortTemperatureC = 78.0,
  [double]$MaximumSmokeTemperatureC = 74.0,
  [double]$MinimumSmokeProbabilityVariance = 0.0,
  [double]$MaximumIdleGpuMemoryMb = 128.0,
  [string]$AllowedComputeProcessPattern = "(?i)ChatGPT\.exe$",
  [string]$SmokeSpecPath = "",
  [string]$FullSpecPath = "",
  [string]$SmokeRunPath = "",
  [string]$FullRunPath = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$smokeSpec = if ($SmokeSpecPath) {
  [System.IO.Path]::GetFullPath($SmokeSpecPath)
} else {
  Join-Path $repoRoot "protocols\asmp8_qwen08_completion_audits_smoke_v0_2.json"
}
$fullSpec = if ($FullSpecPath) {
  [System.IO.Path]::GetFullPath($FullSpecPath)
} else {
  Join-Path $repoRoot "protocols\asmp8_qwen08_completion_audits_500k_v0_1.json"
}
$guardScript = Join-Path $repoRoot "scripts\run_guarded_cuda_benchmark.ps1"
$smokeRun = if ($SmokeRunPath) {
  [System.IO.Path]::GetFullPath($SmokeRunPath)
} else {
  "D:\Research_Engine\runs\asmp8_qwen08_completion_audits_smoke_v0_2"
}
$fullRun = if ($FullRunPath) {
  [System.IO.Path]::GetFullPath($FullRunPath)
} else {
  "D:\Research_Engine\runs\asmp8_qwen08_completion_audits_500k_v0_1"
}
$launcherDir = Join-Path $fullRun "launcher"
$eventsPath = Join-Path $launcherDir "launcher_events.jsonl"
$summaryPath = Join-Path $launcherDir "launcher_summary.json"
$deadline = (Get-Date).AddSeconds($MaximumWaitSeconds)
$effectiveGuardMaximumStartTemperatureC = if ($GuardMaximumStartTemperatureC -ge 0) {
  $GuardMaximumStartTemperatureC
} else {
  $MaximumStartTemperatureC
}

New-Item -ItemType Directory -Force -Path $launcherDir | Out-Null

function Write-AtomicJson([string]$Path, [object]$Value) {
  $temporary = "$Path.tmp"
  $Value | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $temporary -Encoding UTF8
  Move-Item -Force -LiteralPath $temporary -Destination $Path
}

function Write-LauncherEvent([hashtable]$Value) {
  $Value.ts_utc = [DateTime]::UtcNow.ToString("o")
  Add-Content -LiteralPath $eventsPath -Value ($Value | ConvertTo-Json -Compress -Depth 8) -Encoding UTF8
}

function Get-LaunchState {
  $line = & nvidia-smi --query-gpu=temperature.gpu,pstate,power.draw,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits 2>$null |
    Select-Object -First 1
  if (-not $line) {
    throw "nvidia-smi returned no launch-state sample"
  }
  $parts = @($line -split "," | ForEach-Object { $_.Trim() })
  $computeLines = @(
    & nvidia-smi --query-compute-apps=pid,process_name --format=csv,noheader,nounits 2>$null |
      Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
  )
  $foreignComputeLines = @(
    $computeLines | Where-Object {
      -not $AllowedComputeProcessPattern -or
      $_ -notmatch $AllowedComputeProcessPattern
    }
  )
  $os = Get-CimInstance Win32_OperatingSystem
  return [ordered]@{
    temperature_c = [double]$parts[0]
    pstate = [string]$parts[1]
    power_w = [double]$parts[2]
    memory_used_mb = [double]$parts[3]
    memory_free_mb = [double]$parts[4]
    utilization_percent = [double]$parts[5]
    compute_process_count = $computeLines.Count
    compute_processes = $computeLines
    foreign_compute_process_count = $foreignComputeLines.Count
    foreign_compute_processes = $foreignComputeLines
    free_physical_mb = [math]::Round(([double]$os.FreePhysicalMemory / 1024.0), 3)
  }
}

function Test-LaunchState([object]$State) {
  return (
    [double]$State.temperature_c -le $MaximumStartTemperatureC -and
    [double]$State.memory_used_mb -le $MaximumIdleGpuMemoryMb -and
    [double]$State.memory_free_mb -ge 2500.0 -and
    [double]$State.free_physical_mb -ge 8192.0 -and
    [int]$State.foreign_compute_process_count -eq 0
  )
}

function Wait-ForSafeState([string]$Phase) {
  while ((Get-Date) -lt $deadline) {
    try {
      $state = Get-LaunchState
      Write-LauncherEvent @{event="launch_gate_sample";phase=$Phase;state=$state}
      if (Test-LaunchState $state) {
        return $state
      }
    } catch {
      Write-LauncherEvent @{event="launch_gate_sample_failed";phase=$Phase;error=$_.Exception.Message}
    }
    Start-Sleep -Seconds $PollSeconds
  }
  return $null
}

function Invoke-GuardedRun([string]$SpecPath, [string]$RunPath, [string]$Phase) {
  $guardDir = Join-Path $RunPath "guard"
  New-Item -ItemType Directory -Force -Path $guardDir | Out-Null
  Write-LauncherEvent @{event="guarded_run_start";phase=$Phase;spec=$SpecPath;guard_dir=$guardDir}
  & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $guardScript `
    -RunSpecPath $SpecPath -GuardOutputDir $guardDir `
    -MaximumStartTemperatureC $effectiveGuardMaximumStartTemperatureC `
    -AbortTemperatureC $AbortTemperatureC `
    1>> (Join-Path $launcherDir "$Phase`_guard_stdout.log") `
    2>> (Join-Path $launcherDir "$Phase`_guard_stderr.log")
  $exitCode = $LASTEXITCODE
  Write-LauncherEvent @{event="guarded_run_exit";phase=$Phase;exit_code=$exitCode}
  return $exitCode
}

function Stop-Launcher([string]$Status, [string]$Reason, [object]$Details) {
  $summary = [ordered]@{
    schema_version = "asmp8_500k_safe_launcher_summary_v0_1"
    status = $Status
    reason = $Reason
    details = $Details
    completed_utc = [DateTime]::UtcNow.ToString("o")
    smoke_spec = $smokeSpec
    full_spec = $fullSpec
  }
  Write-AtomicJson $summaryPath $summary
  Write-LauncherEvent @{event="launcher_stop";status=$Status;reason=$Reason}
  $summary | ConvertTo-Json -Depth 10
  exit $(if ($Status -eq "completed") { 0 } else { 3 })
}

if (Test-Path -LiteralPath $summaryPath) {
  $priorSummary = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
  if ([string]$priorSummary.status -eq "completed") {
    $priorSummary | ConvertTo-Json -Depth 10
    exit 0
  }
  Write-LauncherEvent @{
    event = "launcher_resume_after_nonterminal_summary"
    prior_status = [string]$priorSummary.status
    prior_reason = [string]$priorSummary.reason
  }
}

Write-LauncherEvent @{
  event = "launcher_start"
  maximum_wait_seconds = $MaximumWaitSeconds
  poll_seconds = $PollSeconds
  maximum_start_temperature_c = $MaximumStartTemperatureC
  guard_maximum_start_temperature_c = $effectiveGuardMaximumStartTemperatureC
  abort_temperature_c = $AbortTemperatureC
  maximum_smoke_temperature_c = $MaximumSmokeTemperatureC
  minimum_smoke_probability_variance = $MinimumSmokeProbabilityVariance
  maximum_idle_gpu_memory_mb = $MaximumIdleGpuMemoryMb
  allowed_compute_process_pattern = $AllowedComputeProcessPattern
  smoke_spec = $smokeSpec
  full_spec = $fullSpec
  deadline_utc = $deadline.ToUniversalTime().ToString("o")
}

$smokeState = Wait-ForSafeState "smoke"
if ($null -eq $smokeState) {
  Stop-Launcher "launch_gate_timeout" "safe_state_not_reached_for_smoke" $null
}

$smokeSummaryPath = Join-Path $smokeRun "summary.json"
$smokeGuardPath = Join-Path $smokeRun "guard\guard_summary.json"
$smokeWrapperPath = Join-Path $smokeRun "wrapper\wrapper_summary.json"
if (-not (Test-Path -LiteralPath $smokeSummaryPath)) {
  $smokeExit = Invoke-GuardedRun $smokeSpec $smokeRun "smoke"
  if ($smokeExit -ne 0) {
    Stop-Launcher "smoke_failed" "guarded_smoke_exit_$smokeExit" $null
  }
}

if (
  -not (Test-Path -LiteralPath $smokeSummaryPath) -or
  -not (Test-Path -LiteralPath $smokeGuardPath) -or
  -not (Test-Path -LiteralPath $smokeWrapperPath)
) {
  Stop-Launcher "smoke_failed" "smoke_receipt_missing" $null
}

$smokeSummary = Get-Content -LiteralPath $smokeSummaryPath -Raw | ConvertFrom-Json
$smokeGuard = Get-Content -LiteralPath $smokeGuardPath -Raw | ConvertFrom-Json
$smokeWrapper = Get-Content -LiteralPath $smokeWrapperPath -Raw | ConvertFrom-Json
$probabilityCoverage = (
  [double]$smokeSummary.counts.probability_scores_returned /
  [double]$smokeSummary.counts.audits_completed
)
$smokePass = (
  [string]$smokeSummary.status -eq "completed" -and
  [string]$smokeGuard.status -eq "completed" -and
  [double]$smokeGuard.max_temperature_c -le $MaximumSmokeTemperatureC -and
  [bool]$smokeWrapper.cleanup_passed -and
  $probabilityCoverage -eq 1.0 -and
  [double]$smokeSummary.audit_statistics.returned_token_probability_variance -gt
    $MinimumSmokeProbabilityVariance
)
if (-not $smokePass) {
  Stop-Launcher "smoke_failed" "smoke_scientific_or_resource_gate_failed" @{
    probability_coverage = $probabilityCoverage
    smoke_status = $smokeSummary.status
    guard_status = $smokeGuard.status
    max_temperature_c = $smokeGuard.max_temperature_c
    cleanup_passed = $smokeWrapper.cleanup_passed
    probability_variance = $smokeSummary.audit_statistics.returned_token_probability_variance
  }
}
Write-LauncherEvent @{
  event = "smoke_pass"
  probability_coverage = $probabilityCoverage
  probability_variance = $smokeSummary.audit_statistics.returned_token_probability_variance
  max_temperature_c = $smokeGuard.max_temperature_c
}

$fullState = Wait-ForSafeState "full"
if ($null -eq $fullState) {
  Stop-Launcher "launch_gate_timeout" "safe_state_not_reached_for_full" $null
}

$fullExit = Invoke-GuardedRun $fullSpec $fullRun "full"
$fullSummaryPath = Join-Path $fullRun "summary.json"
$fullGuardPath = Join-Path $fullRun "guard\guard_summary.json"
$fullProgressPath = Join-Path $fullRun "progress.json"
$details = [ordered]@{
  guarded_exit_code = $fullExit
  full_summary_exists = (Test-Path -LiteralPath $fullSummaryPath)
  guard_summary_exists = (Test-Path -LiteralPath $fullGuardPath)
  progress_exists = (Test-Path -LiteralPath $fullProgressPath)
}
if (Test-Path -LiteralPath $fullProgressPath) {
  $details.progress = Get-Content -LiteralPath $fullProgressPath -Raw | ConvertFrom-Json
}
if ($fullExit -eq 0 -and (Test-Path -LiteralPath $fullSummaryPath)) {
  Stop-Launcher "completed" "full_500k_run_completed" $details
}
Stop-Launcher "full_stopped" "guarded_full_exit_$fullExit" $details
