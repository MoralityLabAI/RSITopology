param(
  [Parameter(Mandatory = $true)]
  [string]$AuthorizationPath
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Get-Sha256 {
  param([string]$Path)
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Write-CanonicalJson {
  param([string]$Path, $Value)
  $parent = Split-Path -Parent $Path
  if ($parent -and -not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
  $json = $Value | ConvertTo-Json -Depth 12 -Compress
  [System.IO.File]::WriteAllText(
    $Path,
    $json + "`n",
    [System.Text.UTF8Encoding]::new($false)
  )
}

function Add-JsonEvent {
  param([string]$Path, [string]$Event, [hashtable]$Fields = @{})
  $payload = [ordered]@{
    ts_utc = (Get-Date).ToUniversalTime().ToString("o")
    event = $Event
  }
  foreach ($entry in $Fields.GetEnumerator()) {
    $payload[$entry.Key] = $entry.Value
  }
  $json = $payload | ConvertTo-Json -Depth 8 -Compress
  [System.IO.File]::AppendAllText(
    $Path,
    $json + "`n",
    [System.Text.UTF8Encoding]::new($false)
  )
}

function Get-FreeMemoryMb {
  $os = Get-CimInstance Win32_OperatingSystem
  return [int]([double]$os.FreePhysicalMemory / 1024)
}

function Get-PageFileUsageMb {
  $rows = @(Get-CimInstance Win32_PageFileUsage -ErrorAction SilentlyContinue)
  if ($rows.Count -eq 0) { return 0 }
  return [int](($rows | Measure-Object CurrentUsage -Sum).Sum)
}

function Get-GpuState {
  $line = & nvidia-smi `
    --query-gpu=temperature.gpu,memory.used,utilization.gpu,power.draw `
    --format=csv,noheader,nounits 2>$null |
    Select-Object -First 1
  if (-not $line) { throw "nvidia-smi returned no GPU row" }
  $parts = $line -split ","
  if ($parts.Count -ne 4) { throw "unexpected nvidia-smi GPU row: $line" }
  return [ordered]@{
    temperature_c = [int]$parts[0].Trim()
    memory_used_mb = [int]$parts[1].Trim()
    utilization_pct = [int]$parts[2].Trim()
    power_w = [double]$parts[3].Trim()
  }
}

function Get-GpuComputeApps {
  $rows = @(& nvidia-smi `
    --query-compute-apps=pid,process_name,used_memory `
    --format=csv,noheader,nounits 2>$null)
  return @($rows | Where-Object {
    $_ -and $_.Trim().Length -gt 0 -and $_ -notmatch "\[N/A\]"
  })
}

function Convert-ToCommandLineArgument {
  param([string]$Value)
  if ($Value -match "[`r`n`0]") {
    throw "unsafe command argument"
  }
  return '"' + $Value.Replace('\', '\').Replace('"', '\"') + '"'
}

if (-not ("Asmp9JobObjectV0682" -as [type])) {
  Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class Asmp9JobObjectV0682 {
  [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  public static extern IntPtr CreateJobObject(IntPtr attributes, string name);

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool SetInformationJobObject(
    IntPtr job, int infoClass, IntPtr info, uint infoLength
  );

  [DllImport("kernel32.dll", SetLastError = true)]
  public static extern bool TerminateJobObject(IntPtr job, uint exitCode);

  [DllImport("kernel32.dll")]
  public static extern bool CloseHandle(IntPtr handle);

  public const int ExtendedLimitInformation = 9;
  public const int CpuRateControlInformation = 15;
  public const uint JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200;
  public const uint JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000;
  public const uint CPU_RATE_ENABLE = 0x1;
  public const uint CPU_RATE_HARD_CAP = 0x4;

  [StructLayout(LayoutKind.Sequential)]
  public struct IO_COUNTERS {
    public ulong ReadOperationCount;
    public ulong WriteOperationCount;
    public ulong OtherOperationCount;
    public ulong ReadTransferCount;
    public ulong WriteTransferCount;
    public ulong OtherTransferCount;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct BASIC_LIMIT_INFORMATION {
    public long PerProcessUserTimeLimit;
    public long PerJobUserTimeLimit;
    public uint LimitFlags;
    public UIntPtr MinimumWorkingSetSize;
    public UIntPtr MaximumWorkingSetSize;
    public uint ActiveProcessLimit;
    public long Affinity;
    public uint PriorityClass;
    public uint SchedulingClass;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct EXTENDED_LIMIT_INFORMATION {
    public BASIC_LIMIT_INFORMATION BasicLimitInformation;
    public IO_COUNTERS IoInfo;
    public UIntPtr ProcessMemoryLimit;
    public UIntPtr JobMemoryLimit;
    public UIntPtr PeakProcessMemoryUsed;
    public UIntPtr PeakJobMemoryUsed;
  }

  [StructLayout(LayoutKind.Sequential)]
  public struct CPU_RATE_CONTROL_INFORMATION {
    public uint ControlFlags;
    public uint CpuRate;
  }

  public static void ThrowLastError(string message) {
    throw new Win32Exception(Marshal.GetLastWin32Error(), message);
  }
}
'@
}

function Set-JobLimits {
  param(
    [IntPtr]$Job,
    [int]$MemoryMb,
    [int]$CpuPercent
  )
  $limits = New-Object Asmp9JobObjectV0682+EXTENDED_LIMIT_INFORMATION
  $limits.BasicLimitInformation.LimitFlags = (
    [Asmp9JobObjectV0682]::JOB_OBJECT_LIMIT_JOB_MEMORY -bor
    [Asmp9JobObjectV0682]::JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
  )
  $limits.JobMemoryLimit = [UIntPtr]([uint64]$MemoryMb * 1MB)
  $size = [Runtime.InteropServices.Marshal]::SizeOf($limits)
  $pointer = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)
  try {
    [Runtime.InteropServices.Marshal]::StructureToPtr(
      $limits, $pointer, $false
    )
    $ok = [Asmp9JobObjectV0682]::SetInformationJobObject(
      $Job,
      [Asmp9JobObjectV0682]::ExtendedLimitInformation,
      $pointer,
      [uint32]$size
    )
    if (-not $ok) {
      [Asmp9JobObjectV0682]::ThrowLastError("failed to set memory limits")
    }
  } finally {
    [Runtime.InteropServices.Marshal]::FreeHGlobal($pointer)
  }

  $cpu = New-Object Asmp9JobObjectV0682+CPU_RATE_CONTROL_INFORMATION
  $cpu.ControlFlags = (
    [Asmp9JobObjectV0682]::CPU_RATE_ENABLE -bor
    [Asmp9JobObjectV0682]::CPU_RATE_HARD_CAP
  )
  $cpu.CpuRate = [uint32]($CpuPercent * 100)
  $size = [Runtime.InteropServices.Marshal]::SizeOf($cpu)
  $pointer = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)
  try {
    [Runtime.InteropServices.Marshal]::StructureToPtr(
      $cpu, $pointer, $false
    )
    $ok = [Asmp9JobObjectV0682]::SetInformationJobObject(
      $Job,
      [Asmp9JobObjectV0682]::CpuRateControlInformation,
      $pointer,
      [uint32]$size
    )
    if (-not $ok) {
      [Asmp9JobObjectV0682]::ThrowLastError("failed to set CPU limits")
    }
  } finally {
    [Runtime.InteropServices.Marshal]::FreeHGlobal($pointer)
  }
}

function Invoke-GuardedPhase {
  param(
    [string]$Name,
    [object[]]$Command,
    [string]$AttemptDir,
    [string]$EventsPath,
    [string]$OwnedPidPath,
    [int]$BaselineGpuMb,
    [int]$BaselinePageFileMb,
    $Caps
  )
  $job = [Asmp9JobObjectV0682]::CreateJobObject(
    [IntPtr]::Zero,
    "asmp9-v0682-$Name-$([Guid]::NewGuid().ToString('N'))"
  )
  if ($job -eq [IntPtr]::Zero) {
    [Asmp9JobObjectV0682]::ThrowLastError("failed to create Job Object")
  }
  Set-JobLimits -Job $job -MemoryMb $Caps.memory_mb `
    -CpuPercent $Caps.cpu_percent

  $stdoutPath = Join-Path $AttemptDir "$Name.stdout.log"
  $stderrPath = Join-Path $AttemptDir "$Name.stderr.log"
  $process = $null
  $abortReason = $null
  $peakGpuMb = $BaselineGpuMb
  $peakTemperature = 0
  $peakWorkingSetMb = 0.0
  $ioBreachSamples = 0
  $pageFileIncreaseMb = 0
  $started = Get-Date
  try {
    $info = [Diagnostics.ProcessStartInfo]::new()
    $info.FileName = [string]$Command[0]
    $info.Arguments = (
      @($Command | Select-Object -Skip 1 | ForEach-Object {
        Convert-ToCommandLineArgument ([string]$_)
      }) -join " "
    )
    $info.WorkingDirectory = (git rev-parse --show-toplevel).Trim()
    $info.UseShellExecute = $false
    $info.CreateNoWindow = $true
    $info.RedirectStandardOutput = $true
    $info.RedirectStandardError = $true
    $process = [Diagnostics.Process]::new()
    $process.StartInfo = $info
    if (-not $process.Start()) { throw "failed to start $Name" }
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    if (-not [Asmp9JobObjectV0682]::AssignProcessToJobObject(
      $job, $process.Handle
    )) {
      try { $process.Kill() } catch {}
      [Asmp9JobObjectV0682]::ThrowLastError(
        "failed to assign $Name to Job Object"
      )
    }
    $owned = @{ owned_pids = @([int]$process.Id) }
    Write-CanonicalJson -Path $OwnedPidPath -Value $owned
    Add-JsonEvent -Path $EventsPath -Event "phase_start" -Fields @{
      phase = $Name
      pid = [int]$process.Id
    }

    $lastIo = [double]0
    $lastSample = Get-Date
    while (-not $process.HasExited) {
      Start-Sleep -Seconds ([double]$Caps.poll_seconds)
      $process.Refresh()
      $now = Get-Date
      $elapsed = ($now - $started).TotalSeconds
      $workingSetMb = [double]$process.WorkingSet64 / 1MB
      $peakWorkingSetMb = [math]::Max($peakWorkingSetMb, $workingSetMb)
      $gpu = Get-GpuState
      $peakGpuMb = [math]::Max(
        $peakGpuMb, [int]$gpu.memory_used_mb
      )
      $peakTemperature = [math]::Max(
        $peakTemperature, [int]$gpu.temperature_c
      )
      $freeMb = Get-FreeMemoryMb
      $pageFileNow = Get-PageFileUsageMb
      $pageFileIncreaseMb = [math]::Max(
        $pageFileIncreaseMb,
        $pageFileNow - $BaselinePageFileMb
      )
      $cim = Get-CimInstance Win32_Process -Filter (
        "ProcessId=$($process.Id)"
      ) -ErrorAction SilentlyContinue
      $ioTotal = if ($cim) {
        [double]$cim.ReadTransferCount + [double]$cim.WriteTransferCount
      } else {
        $lastIo
      }
      $seconds = [math]::Max(0.001, ($now - $lastSample).TotalSeconds)
      $ioMbS = [math]::Max(0.0, ($ioTotal - $lastIo) / 1MB / $seconds)
      if ($ioMbS -gt [double]$Caps.io_mb_s) {
        $ioBreachSamples += 1
      } else {
        $ioBreachSamples = 0
      }
      Add-Content -LiteralPath (Join-Path $AttemptDir "telemetry.csv") -Value (
        "{0},{1},{2:F3},{3},{4},{5:F3},{6},{7}" -f
        $now.ToUniversalTime().ToString("o"),
        $Name,
        $elapsed,
        $gpu.temperature_c,
        $gpu.memory_used_mb,
        $ioMbS,
        $freeMb,
        $pageFileNow
      )
      if ($elapsed -gt [double]$Caps.timeout_seconds) {
        $abortReason = "wall_timeout"
      } elseif (
        ([int]$gpu.memory_used_mb - $BaselineGpuMb) -gt
        [int]$Caps.gpu_allowance_mb
      ) {
        $abortReason = "gpu_memory_abort"
      } elseif (
        [int]$gpu.temperature_c -ge [int]$Caps.temperature_limit_c
      ) {
        $abortReason = "gpu_temperature_abort"
      } elseif (
        $freeMb -lt [int]$Caps.minimum_runtime_free_memory_mb
      ) {
        $abortReason = "host_free_memory_abort"
      } elseif (
        $ioBreachSamples -ge [int]$Caps.io_sustained_samples
      ) {
        $abortReason = "sustained_io_abort"
      }
      if ($abortReason) {
        Add-JsonEvent -Path $EventsPath -Event "resource_abort" -Fields @{
          phase = $Name
          reason = $abortReason
        }
        [void][Asmp9JobObjectV0682]::TerminateJobObject($job, 90)
        break
      }
      $lastIo = $ioTotal
      $lastSample = $now
    }
    $process.WaitForExit()
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    [IO.File]::WriteAllText(
      $stdoutPath, $stdout, [Text.UTF8Encoding]::new($false)
    )
    [IO.File]::WriteAllText(
      $stderrPath, $stderr, [Text.UTF8Encoding]::new($false)
    )
    $exitCode = if ($abortReason) { 90 } else { $process.ExitCode }
    $status = if ($exitCode -eq 0) { "completed" } else { "aborted" }
    Add-JsonEvent -Path $EventsPath -Event "phase_finish" -Fields @{
      phase = $Name
      status = $status
      exit_code = $exitCode
      abort_reason = $abortReason
    }
    return [ordered]@{
      phase = $Name
      status = $status
      exit_code = $exitCode
      abort_reason = $abortReason
      elapsed_seconds = ((Get-Date) - $started).TotalSeconds
      peak_gpu_total_mb = $peakGpuMb
      peak_gpu_delta_mb = $peakGpuMb - $BaselineGpuMb
      peak_temperature_c = $peakTemperature
      peak_working_set_mb = $peakWorkingSetMb
      page_file_increase_mb = $pageFileIncreaseMb
      stdout_path = $stdoutPath
      stderr_path = $stderrPath
    }
  } finally {
    if ($process -and -not $process.HasExited) {
      [void][Asmp9JobObjectV0682]::TerminateJobObject($job, 91)
      $process.WaitForExit()
    }
    if ($job -ne [IntPtr]::Zero) {
      [void][Asmp9JobObjectV0682]::CloseHandle($job)
    }
  }
}

$authorizationPath = (Resolve-Path -LiteralPath $AuthorizationPath).Path
$authorization = Get-Content -LiteralPath $authorizationPath -Raw |
  ConvertFrom-Json
if (
  $authorization.schema_version -ne
  "asmp9_context_quotient_authorization_v0_68_2_windows"
) {
  throw "unexpected authorization schema"
}
$selfPath = $MyInvocation.MyCommand.Path
if (
  (Get-Sha256 $selfPath) -ne
  ([string]$authorization.hard_cap_wrapper.sha256).ToLowerInvariant()
) {
  throw "wrapper hash differs from authorization"
}
if (
  (Get-Sha256 $authorization.cleanup_script.path) -ne
  ([string]$authorization.cleanup_script.sha256).ToLowerInvariant()
) {
  throw "cleanup hash differs from authorization"
}
if (
  (Get-Sha256 $authorization.registration.path) -ne
  ([string]$authorization.registration.sha256).ToLowerInvariant()
) {
  throw "registration hash differs from authorization"
}
$registration = Get-Content -LiteralPath $authorization.registration.path -Raw |
  ConvertFrom-Json
if (
  $registration.status -ne "registered_prereveal" -or
  $registration.outcomes_read -ne $false -or
  $registration.phase -ne "confirmation" -or
  $registration.execution_contract_version -notin @(
    "local_windows_v0_68_2",
    "local_windows_v0_68_2_1"
  )
) {
  throw "registration is not the local prereveal confirmation"
}
$registeredCaps = $registration.resource_contract | ConvertTo-Json -Compress
$authorizedCaps = $authorization.resource_caps | ConvertTo-Json -Compress
if ($registeredCaps -ne $authorizedCaps) {
  throw "authorization resource caps differ from registration"
}
$caps = $authorization.resource_caps
$wrapperRoot = [string]$authorization.wrapper_output_dir
New-Item -ItemType Directory -Path $wrapperRoot -Force | Out-Null
$attemptId = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ") +
  "-$PID"
$attemptDir = Join-Path $wrapperRoot "attempts\$attemptId"
New-Item -ItemType Directory -Path $attemptDir -Force | Out-Null
$eventsPath = Join-Path $attemptDir "events.jsonl"
$ownedPidPath = Join-Path $attemptDir "owned_pids.json"
$summaryPath = Join-Path $attemptDir "wrapper_summary.json"
$cleanupSummaryPath = Join-Path $attemptDir "cleanup_summary.json"
[IO.File]::WriteAllText(
  (Join-Path $attemptDir "telemetry.csv"),
  "timestamp_utc,phase,elapsed_seconds,temperature_c,gpu_memory_used_mb,io_mb_s,free_memory_mb,page_file_usage_mb`n",
  [Text.UTF8Encoding]::new($false)
)

$baselineGpu = Get-GpuState
$baselinePageFileMb = Get-PageFileUsageMb
$freeMb = Get-FreeMemoryMb
$apps = @(Get-GpuComputeApps)
if ($freeMb -lt [int]$caps.minimum_free_memory_mb) {
  throw "insufficient free RAM: $freeMb MB"
}
if ([int]$baselineGpu.memory_used_mb -gt [int]$caps.gpu_clean_start_ceiling_mb) {
  throw "unclean GPU start: $($baselineGpu.memory_used_mb) MB"
}
if ($apps.Count -gt 0) {
  throw "GPU compute applications present at start: $($apps -join '; ')"
}

Add-JsonEvent -Path $eventsPath -Event "wrapper_start" -Fields @{
  attempt_id = $attemptId
  authorization_sha256 = Get-Sha256 $authorizationPath
  registration_sha256 = Get-Sha256 $authorization.registration.path
  baseline_gpu_mb = [int]$baselineGpu.memory_used_mb
  baseline_temperature_c = [int]$baselineGpu.temperature_c
  baseline_page_file_mb = $baselinePageFileMb
}

$runnerResult = $null
$analysisResult = $null
$cleanupResult = $null
$wrapperStatus = "aborted"
try {
  $runnerResult = Invoke-GuardedPhase `
    -Name "runner" `
    -Command @($authorization.exact_runner_command) `
    -AttemptDir $attemptDir `
    -EventsPath $eventsPath `
    -OwnedPidPath $ownedPidPath `
    -BaselineGpuMb ([int]$baselineGpu.memory_used_mb) `
    -BaselinePageFileMb $baselinePageFileMb `
    -Caps $caps
  if ($runnerResult.exit_code -eq 0) {
    $analysisResult = Invoke-GuardedPhase `
      -Name "analysis" `
      -Command @($authorization.exact_analysis_command) `
      -AttemptDir $attemptDir `
      -EventsPath $eventsPath `
      -OwnedPidPath $ownedPidPath `
      -BaselineGpuMb ([int]$baselineGpu.memory_used_mb) `
      -BaselinePageFileMb $baselinePageFileMb `
      -Caps $caps
  }
  if (
    $runnerResult.exit_code -eq 0 -and
    $analysisResult -and $analysisResult.exit_code -eq 0
  ) {
    $wrapperStatus = "completed"
  }
} finally {
  & powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File $authorization.cleanup_script.path `
    -RunId $authorization.run_id `
    -PidFile $ownedPidPath `
    -SummaryPath $cleanupSummaryPath `
    -StopOwnedProcesses
  if (Test-Path -LiteralPath $cleanupSummaryPath) {
    $cleanupResult = Get-Content -LiteralPath $cleanupSummaryPath -Raw |
      ConvertFrom-Json
  }
  $pageFileIncrease = [math]::Max(
    $(if ($runnerResult) { $runnerResult.page_file_increase_mb } else { 0 }),
    $(if ($analysisResult) { $analysisResult.page_file_increase_mb } else { 0 })
  )
  $cleanupValid = (
    $cleanupResult -and
    $cleanupResult.cleanup_passed -eq $true -and
    $pageFileIncrease -le 0
  )
  if (-not $cleanupValid) {
    $wrapperStatus = "cleanup_invalid"
  }
  $summary = [ordered]@{
    schema_version = "asmp9_context_quotient_windows_wrapper_v0_68_2"
    attempt_id = $attemptId
    run_id = $authorization.run_id
    status = $wrapperStatus
    registration_sha256 = Get-Sha256 $authorization.registration.path
    authorization_sha256 = Get-Sha256 $authorizationPath
    caps = $caps
    baseline = [ordered]@{
      gpu = $baselineGpu
      free_memory_mb = $freeMb
      page_file_usage_mb = $baselinePageFileMb
    }
    runner = $runnerResult
    analysis = $analysisResult
    page_file_increase_mb = $pageFileIncrease
    cleanup = $cleanupResult
  }
  Write-CanonicalJson -Path $summaryPath -Value $summary
  Add-JsonEvent -Path $eventsPath -Event "wrapper_finish" -Fields @{
    status = $wrapperStatus
    cleanup_valid = $cleanupValid
  }
}

if ($wrapperStatus -ne "completed") { exit 90 }
exit 0
