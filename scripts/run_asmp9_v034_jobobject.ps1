param(
  [Parameter(Mandatory=$true)][string]$RegistrationPath,
  [ValidateSet("smoke","burned_pilot")][string]$ExecutionClass = "smoke",
  [string]$OutputDir = "",
  [int]$SmokeRowsPerType = 2
)

$ErrorActionPreference = "Stop"
$registrationPath = (Resolve-Path -LiteralPath $RegistrationPath).Path
$spec = Get-Content -LiteralPath $registrationPath -Raw | ConvertFrom-Json
if ($spec.schema_version -ne "asmp9_physical_acquisition_burned_pilot_registration_v0_34_2") {
  throw "Unsupported ASMP-9 run-spec schema"
}
$caps = $spec.resource_caps
foreach ($field in @(
  "memory_mb","cpu_percent","io_mb_s","io_sustained_samples",
  "timeout_seconds","gpu_allowance_mb","checkpoint_every_seconds",
  "hard_abort_temperature_c","gpu_clean_start_ceiling_mb"
)) {
  if ([double]$caps.$field -le 0) { throw "Missing positive cap: $field" }
}
if ([int]$caps.swap_bytes -ne 0) { throw "Only zero registered swap is accepted" }

$registeredWrapper = $spec.implementation.hard_cap_wrapper
$currentWrapperPath = [System.IO.Path]::GetFullPath($PSCommandPath)
$currentWrapperHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $currentWrapperPath).Hash.ToLowerInvariant()
$repoRoot = (Resolve-Path -LiteralPath (Join-Path (Split-Path -Parent $PSCommandPath) "..")).Path
$registeredWrapperPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot ([string]$registeredWrapper.path)))
if ($registeredWrapperPath -ne $currentWrapperPath) { throw "Registered wrapper path differs" }
if ([string]$registeredWrapper.sha256 -ne $currentWrapperHash) { throw "Registered wrapper hash differs" }

$runnerInfo = $spec.implementation.runner
$runnerPath = [System.IO.Path]::GetFullPath((Join-Path $repoRoot ([string]$runnerInfo.path)))
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $runnerPath).Hash.ToLowerInvariant() -ne [string]$runnerInfo.sha256) {
  throw "Registered runner hash differs"
}
$python = [string]$spec.environment.python_executable
if (-not (Test-Path -LiteralPath $python)) { throw "Registered Python executable missing" }

if ($ExecutionClass -eq "burned_pilot") {
  if ($OutputDir) { throw "Full burned pilot must use the registered output directory" }
  $runDir = [System.IO.Path]::GetFullPath([string]$spec.capture_parameters.output_dir)
  $command = @($spec.exact_inner_command | ForEach-Object { [string]$_ })
} else {
  if (-not $OutputDir) { throw "Smoke execution requires -OutputDir" }
  if ($SmokeRowsPerType -le 0) { throw "SmokeRowsPerType must be positive" }
  $runDir = [System.IO.Path]::GetFullPath($OutputDir)
  $command = @(
    $python,
    $runnerPath,
    "--registration", $registrationPath,
    "--output-dir", $runDir,
    "--execution-class", "smoke",
    "--smoke-rows-per-type", "$SmokeRowsPerType"
  )
}
if ($command.Count -lt 2 -or $command[0] -ne $python -or $command[1] -ne $runnerPath) {
  throw "Inner command is not the registered runner"
}
$arguments = @($command | Select-Object -Skip 1)

New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$wrapperDir = Join-Path $runDir "wrapper"
New-Item -ItemType Directory -Force -Path $wrapperDir | Out-Null
$eventsPath = Join-Path $wrapperDir "events.jsonl"
$summaryPath = Join-Path $wrapperDir "summary.json"
$stdoutPath = Join-Path $wrapperDir "stdout.log"
$stderrPath = Join-Path $wrapperDir "stderr.log"
$pidPath = Join-Path $wrapperDir "owned_pids.json"
$cleanupPath = Join-Path $wrapperDir "cleanup_summary.json"
$cleanupScript = [string]$spec.cleanup_script.path
if (-not (Test-Path -LiteralPath $cleanupScript)) { throw "Registered cleanup script missing" }
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $cleanupScript).Hash.ToLowerInvariant() -ne [string]$spec.cleanup_script.sha256) {
  throw "Registered cleanup script hash differs"
}

function Write-WrapperEvent([hashtable]$Value) {
  $Value.ts_utc = [DateTime]::UtcNow.ToString("o")
  Add-Content -LiteralPath $eventsPath -Value ($Value | ConvertTo-Json -Compress -Depth 8) -Encoding UTF8
}

function Get-ProcessTree([int]$RootId) {
  $all = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Select-Object ProcessId,ParentProcessId,ReadTransferCount,WriteTransferCount)
  $seen = New-Object System.Collections.Generic.HashSet[int]
  $queue = New-Object System.Collections.Generic.Queue[int]
  if ($RootId -gt 0 -and $seen.Add($RootId)) { $queue.Enqueue($RootId) }
  while ($queue.Count -gt 0) {
    $current = $queue.Dequeue()
    foreach ($child in ($all | Where-Object { [int]$_.ParentProcessId -eq $current })) {
      if ($seen.Add([int]$child.ProcessId)) { $queue.Enqueue([int]$child.ProcessId) }
    }
  }
  return @($all | Where-Object { $seen.Contains([int]$_.ProcessId) })
}

function Get-TreeMetrics([int]$RootId) {
  $tree = @(Get-ProcessTree $RootId)
  $privateBytes = 0.0
  $ioBytes = 0.0
  $ids = @()
  foreach ($item in $tree) {
    $ids += [int]$item.ProcessId
    $ioBytes += [double]$item.ReadTransferCount + [double]$item.WriteTransferCount
    $process = Get-Process -Id ([int]$item.ProcessId) -ErrorAction SilentlyContinue
    if ($process) { $privateBytes += [double]$process.PrivateMemorySize64 }
  }
  return [ordered]@{ ids=$ids; private_mb=$privateBytes/1MB; io_bytes=$ioBytes }
}

function Get-GpuSnapshot {
  $used = 0.0
  $temperature = 0.0
  if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $line = @(& nvidia-smi --query-gpu=memory.used,temperature.gpu --format=csv,noheader,nounits 2>$null)[0]
    $parts = $line -split ","
    if ($parts.Count -ge 2) {
      [void][double]::TryParse($parts[0].Trim(), [ref]$used)
      [void][double]::TryParse($parts[1].Trim(), [ref]$temperature)
    }
  }
  return [ordered]@{ total_used_mb=$used; temperature_c=$temperature }
}

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class Asmp9V034Job {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CreateJobObject(IntPtr a, string n);
  [DllImport("kernel32.dll")] public static extern bool AssignProcessToJobObject(IntPtr j, IntPtr p);
  [DllImport("kernel32.dll")] public static extern bool SetInformationJobObject(IntPtr j, int t, IntPtr i, uint s);
  [DllImport("kernel32.dll")] public static extern bool QueryInformationJobObject(IntPtr j, int t, IntPtr i, uint s, IntPtr r);
  [DllImport("kernel32.dll")] public static extern bool TerminateJobObject(IntPtr j, uint c);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
  public const int Extended = 9, Cpu = 15;
  public const uint ProcessMemory = 0x100, JobMemory = 0x200, KillOnClose = 0x2000;
  public const uint CpuEnable = 0x1, CpuHardCap = 0x4;
  [StructLayout(LayoutKind.Sequential)] public struct IO_COUNTERS { public ulong ReadOperationCount,WriteOperationCount,OtherOperationCount,ReadTransferCount,WriteTransferCount,OtherTransferCount; }
  [StructLayout(LayoutKind.Sequential)] public struct BASIC { public long ProcessTime,JobTime; public uint Flags; public UIntPtr MinSet,MaxSet; public uint Active; public UIntPtr Affinity; public uint Priority,Scheduling; }
  [StructLayout(LayoutKind.Sequential)] public struct EXTENDED { public BASIC Basic; public IO_COUNTERS Io; public UIntPtr ProcessMemoryLimit,JobMemoryLimit,PeakProcessMemoryUsed,PeakJobMemoryUsed; }
  [StructLayout(LayoutKind.Sequential)] public struct CPU { public uint Flags,Rate; }
  public static bool ConfigureMemory(IntPtr job, ulong bytes) {
    var info = new EXTENDED();
    info.Basic.Flags = ProcessMemory | JobMemory | KillOnClose;
    info.ProcessMemoryLimit = new UIntPtr(bytes); info.JobMemoryLimit = new UIntPtr(bytes);
    int size = Marshal.SizeOf(info); IntPtr ptr = Marshal.AllocHGlobal(size);
    try { Marshal.StructureToPtr(info, ptr, false); return SetInformationJobObject(job, Extended, ptr, (uint)size); }
    finally { Marshal.FreeHGlobal(ptr); }
  }
  public static bool ConfigureCpu(IntPtr job, uint rate) {
    var info = new CPU(); info.Flags = CpuEnable | CpuHardCap; info.Rate = rate;
    int size = Marshal.SizeOf(info); IntPtr ptr = Marshal.AllocHGlobal(size);
    try { Marshal.StructureToPtr(info, ptr, false); return SetInformationJobObject(job, Cpu, ptr, (uint)size); }
    finally { Marshal.FreeHGlobal(ptr); }
  }
}
'@

$memoryBytes = [UInt64]([double]$caps.memory_mb * 1MB)
$cpuRate = [UInt32]([double]$caps.cpu_percent * 100)
$job = [Asmp9V034Job]::CreateJobObject([IntPtr]::Zero, "asmp9-v034-$([guid]::NewGuid())")
if ($job -eq [IntPtr]::Zero) { throw "CreateJobObject failed" }
$proc = $null
$status = "failed_before_start"
$abortReason = $null
$exitCode = $null
$peakRam = 0.0
$peakIo = 0.0
$peakGpu = 0.0
$peakGpuTotal = 0.0
$peakTemperature = 0.0
$ramSamples = New-Object System.Collections.Generic.List[double]
$cpuSamples = New-Object System.Collections.Generic.List[double]
$gpuBaseline = [ordered]@{ total_used_mb=0.0; temperature_c=0.0 }
$started = Get-Date
try {
  if (-not [Asmp9V034Job]::ConfigureMemory($job, $memoryBytes)) { throw "Failed to set memory cap" }
  if (-not [Asmp9V034Job]::ConfigureCpu($job, $cpuRate)) { throw "Failed to set CPU cap" }
  $gpuBaseline = Get-GpuSnapshot
  if ([double]$gpuBaseline.total_used_mb -gt [double]$caps.gpu_clean_start_ceiling_mb) {
    throw "GPU is not clean at start: $($gpuBaseline.total_used_mb) MB used"
  }
  Write-WrapperEvent @{event="start";execution_class=$ExecutionClass;caps=$caps;command=$command}
  $env:ASMP9_V034_HARD_CAP_ACTIVE = $currentWrapperHash
  $proc = Start-Process -FilePath $python -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
  if (-not [Asmp9V034Job]::AssignProcessToJobObject($job, $proc.Handle)) { throw "AssignProcessToJobObject failed" }
  @{root_pid=$proc.Id;owned_pids=@($proc.Id);execution_class=$ExecutionClass} |
    ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $pidPath -Encoding UTF8
  $status = "running"
  $previousTree = Get-TreeMetrics $proc.Id
  $previousCpu = $proc.TotalProcessorTime.TotalSeconds
  $previousTime = Get-Date
  $ioBreaches = 0
  while (-not $proc.HasExited) {
    Start-Sleep -Seconds 1
    $proc.Refresh()
    if ($proc.HasExited) { break }
    $now = Get-Date
    $elapsed = [math]::Max(($now - $previousTime).TotalSeconds, 0.001)
    $tree = Get-TreeMetrics $proc.Id
    $ioRate = [math]::Max(0.0, ($tree.io_bytes - $previousTree.io_bytes) / 1MB / $elapsed)
    $cpuNow = $proc.TotalProcessorTime.TotalSeconds
    $cpuPct = 100.0 * [math]::Max(0.0, $cpuNow - $previousCpu) / $elapsed / [Environment]::ProcessorCount
    $gpu = Get-GpuSnapshot
    $gpuDelta = [math]::Max(
      0.0,
      [double]$gpu.total_used_mb - [double]$gpuBaseline.total_used_mb
    )
    $peakRam = [math]::Max($peakRam, [double]$tree.private_mb)
    $peakIo = [math]::Max($peakIo, $ioRate)
    $peakGpu = [math]::Max($peakGpu, $gpuDelta)
    $peakGpuTotal = [math]::Max($peakGpuTotal, [double]$gpu.total_used_mb)
    $peakTemperature = [math]::Max($peakTemperature, [double]$gpu.temperature_c)
    $ramSamples.Add([double]$tree.private_mb)
    $cpuSamples.Add($cpuPct)
    if ($ioRate -gt [double]$caps.io_mb_s) { $ioBreaches++ } else { $ioBreaches = 0 }
    if ($ioBreaches -ge [int]$caps.io_sustained_samples) { $abortReason = "sustained_io_cap_exceeded" }
    if ($gpuDelta -gt [double]$caps.gpu_allowance_mb) { $abortReason = "gpu_allowance_exceeded" }
    if ([double]$gpu.temperature_c -ge [double]$caps.hard_abort_temperature_c) { $abortReason = "hard_temperature_abort" }
    if (($now - $started).TotalSeconds -gt [double]$caps.timeout_seconds) { $abortReason = "timeout" }
    if ($abortReason) {
      [void][Asmp9V034Job]::TerminateJobObject($job, 3)
      break
    }
    $previousTree = $tree
    $previousCpu = $cpuNow
    $previousTime = $now
  }
  $proc.WaitForExit()
  $exitCode = $proc.ExitCode
  if ($abortReason) { $status = "aborted" }
  elseif ($exitCode -eq 0) { $status = "completed" }
  else { $status = "failed"; $abortReason = "exit_code_$exitCode" }
} catch {
  $status = "wrapper_failed"
  $abortReason = "wrapper_exception:$($_.Exception.Message)"
  if ($job -ne [IntPtr]::Zero) { [void][Asmp9V034Job]::TerminateJobObject($job, 3) }
} finally {
  Remove-Item Env:\ASMP9_V034_HARD_CAP_ACTIVE -ErrorAction SilentlyContinue
  if ($proc -and -not $proc.HasExited) { [void][Asmp9V034Job]::TerminateJobObject($job, 3) }
  if ($job -ne [IntPtr]::Zero) { [void][Asmp9V034Job]::CloseHandle($job) }
  & $cleanupScript -RunId "asmp9-v034-$ExecutionClass" -PidFile $pidPath -StopOwnedProcesses -SummaryPath $cleanupPath -WaitSeconds 1 | Out-Null
  $cleanup = if (Test-Path -LiteralPath $cleanupPath) { Get-Content $cleanupPath -Raw | ConvertFrom-Json } else { $null }
  if ($status -eq "completed" -and ($null -eq $cleanup -or $cleanup.cleanup_passed -ne $true)) {
    $status = "cleanup_failed"
  }
  $summary = [ordered]@{
    schema_version = "asmp9_v034_jobobject_summary_v0_1"
    execution_class = $ExecutionClass
    status = $status
    abort_reason = $abortReason
    exit_code = $exitCode
    caps = $caps
    memory_cap_set = $true
    cpu_cap_set = $true
    peak_ram_mb = [math]::Round($peakRam,3)
    avg_ram_mb = $(if ($ramSamples.Count) {[math]::Round(($ramSamples | Measure-Object -Average).Average,3)} else {0})
    peak_io_mb_s = [math]::Round($peakIo,3)
    cpu_pct = $(if ($cpuSamples.Count) {[math]::Round(($cpuSamples | Measure-Object -Average).Average,3)} else {0})
    peak_gpu_mb = [math]::Round($peakGpu,3)
    gpu_memory_accounting = "whole-device delta from registered clean-start ceiling"
    gpu_baseline_used_mb = [math]::Round([double]$gpuBaseline.total_used_mb,3)
    peak_gpu_total_used_mb = [math]::Round($peakGpuTotal,3)
    peak_gpu_temperature_c = [math]::Round($peakTemperature,1)
    elapsed_seconds = [math]::Round(((Get-Date)-$started).TotalSeconds,3)
    cleanup_summary = $cleanupPath
    cleanup_passed = [bool]($cleanup -ne $null -and $cleanup.cleanup_passed -eq $true)
    owned_pid_file = $pidPath
    stdout = $stdoutPath
    stderr = $stderrPath
  }
  $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
  Write-WrapperEvent @{event=$status;abort_reason=$abortReason;summary=$summaryPath}
  $summary | ConvertTo-Json -Depth 8
}
if ($status -eq "completed") { exit 0 }
exit 3
