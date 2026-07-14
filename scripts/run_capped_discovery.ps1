param(
  [Parameter(Mandatory=$true)][string]$RunId,
  [Parameter(Mandatory=$true)][int]$MemoryLimitMB,
  [Parameter(Mandatory=$true)][int]$CpuPercent,
  [Parameter(Mandatory=$true)][int]$IoLimitMBps,
  [Parameter(Mandatory=$true)][string]$CheckpointInterval,
  [Parameter(Mandatory=$true)][string]$ChunkStrategy,
  [Parameter(Mandatory=$true)][int]$TimeoutSeconds,
  [Parameter(Mandatory=$true)][string]$Script,
  [string[]]$ScriptArgs = @()
)

$ErrorActionPreference = "Stop"
if ($MemoryLimitMB -le 0 -or $CpuPercent -lt 1 -or $CpuPercent -gt 100 -or
    $IoLimitMBps -le 0 -or $TimeoutSeconds -le 0) {
  throw "Caps and timeout must be positive; CpuPercent must be in [1,100]."
}

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$scriptPath = (Resolve-Path -LiteralPath (Join-Path $root $Script)).Path
$runDir = Join-Path $root ("artifacts\capped_runs\" + $RunId)
New-Item -ItemType Directory -Path $runDir -Force | Out-Null
$eventPath = Join-Path $runDir "events.jsonl"
$summaryPath = Join-Path $runDir "summary.json"
$pidPath = Join-Path $runDir "owned_pids.json"
$stdoutPath = Join-Path $runDir "stdout.log"
$stderrPath = Join-Path $runDir "stderr.log"

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class RsiTopologyJob {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CreateJobObject(IntPtr a, string n);
  [DllImport("kernel32.dll")] public static extern bool AssignProcessToJobObject(IntPtr j, IntPtr p);
  [DllImport("kernel32.dll")] public static extern bool SetInformationJobObject(IntPtr j, int t, IntPtr i, uint s);
  public const int Extended = 9;
  public const int Cpu = 15;
  public const uint ProcessMemory = 0x00000100;
  public const uint JobMemory = 0x00000200;
  public const uint KillOnClose = 0x00002000;
  public const uint CpuEnable = 0x1;
  public const uint CpuHardCap = 0x4;
  [StructLayout(LayoutKind.Sequential)] public struct IO { public ulong a,b,c,d,e,f; }
  [StructLayout(LayoutKind.Sequential)] public struct Basic { public long a,b; public uint flags; public UIntPtr c,d; public uint e; public long f; public uint g,h; }
  [StructLayout(LayoutKind.Sequential)] public struct ExtendedInfo { public Basic basic; public IO io; public UIntPtr processMemory,jobMemory,peakProcess,peakJob; }
  [StructLayout(LayoutKind.Sequential)] public struct CpuInfo { public uint flags; public uint rate; }
}
'@

function Write-Event([hashtable]$Payload) {
  $Payload.ts = (Get-Date).ToUniversalTime().ToString("o")
  Add-Content -LiteralPath $eventPath -Value ($Payload | ConvertTo-Json -Compress -Depth 6) -Encoding UTF8
}

function Get-IoBytes([int]$ProcessId) {
  $item = Get-CimInstance Win32_Process -Filter "ProcessId=$ProcessId" -ErrorAction SilentlyContinue
  if ($null -eq $item) { return 0.0 }
  return [double]$item.ReadTransferCount + [double]$item.WriteTransferCount
}

function Get-CleanupReceipt([int]$OwnedPid) {
  $os = Get-CimInstance Win32_OperatingSystem
  $gpuApps = @()
  if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $gpuApps = @(& nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader,nounits 2>$null)
  }
  $processes = @(Get-Process | Where-Object { $_.Id -ne $PID })
  return [ordered]@{
    owned_pid = $OwnedPid
    lingering_owned_pids = @($(if (Get-Process -Id $OwnedPid -ErrorAction SilentlyContinue) { $OwnedPid }))
    available_ram_mb = [int]$os.FreePhysicalMemory / 1KB
    committed_gb = [math]::Round(((Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory).CommittedBytes / 1GB), 3)
    gpu_compute_apps = $gpuApps
    top_private_commit = @($processes | Sort-Object PrivateMemorySize64 -Descending | Select-Object -First 10 Id,ProcessName,PrivateMemorySize64,WorkingSet64)
    top_working_set = @($processes | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Id,ProcessName,WorkingSet64,PrivateMemorySize64)
  }
}

$job = [RsiTopologyJob]::CreateJobObject([IntPtr]::Zero, "rsi-topology-$RunId")
$limit = New-Object RsiTopologyJob+ExtendedInfo
$limit.basic.flags = [RsiTopologyJob]::ProcessMemory -bor [RsiTopologyJob]::JobMemory -bor [RsiTopologyJob]::KillOnClose
$limit.processMemory = [UIntPtr]([uint64]$MemoryLimitMB * 1MB)
$limit.jobMemory = [UIntPtr]([uint64]$MemoryLimitMB * 1MB)
$size = [Runtime.InteropServices.Marshal]::SizeOf($limit)
$pointer = [Runtime.InteropServices.Marshal]::AllocHGlobal($size)
[Runtime.InteropServices.Marshal]::StructureToPtr($limit, $pointer, $false)
if (-not [RsiTopologyJob]::SetInformationJobObject($job, [RsiTopologyJob]::Extended, $pointer, $size)) { throw "Failed to set memory cap" }
[Runtime.InteropServices.Marshal]::FreeHGlobal($pointer)

$cpu = New-Object RsiTopologyJob+CpuInfo
$cpu.flags = [RsiTopologyJob]::CpuEnable -bor [RsiTopologyJob]::CpuHardCap
$cpu.rate = [uint32]($CpuPercent * 100)
$cpuSize = [Runtime.InteropServices.Marshal]::SizeOf($cpu)
$cpuPointer = [Runtime.InteropServices.Marshal]::AllocHGlobal($cpuSize)
[Runtime.InteropServices.Marshal]::StructureToPtr($cpu, $cpuPointer, $false)
if (-not [RsiTopologyJob]::SetInformationJobObject($job, [RsiTopologyJob]::Cpu, $cpuPointer, $cpuSize)) { throw "Failed to set CPU cap" }
[Runtime.InteropServices.Marshal]::FreeHGlobal($cpuPointer)

$python = (Get-Command python).Source
$arguments = @($scriptPath) + $ScriptArgs
$process = $null
$status = "failed_before_start"
$abortReason = $null
$peakRamMB = 0.0
$peakIoMBs = 0.0
$cpuSamples = New-Object System.Collections.Generic.List[double]
$ramSamples = New-Object System.Collections.Generic.List[double]
$ownedStopped = @()
$started = Get-Date

try {
  Write-Event @{event="start";run_id=$RunId;caps=@{ram_mb=$MemoryLimitMB;cpu_pct=$CpuPercent;io_mb_s=$IoLimitMBps};checkpoint_interval=$CheckpointInterval;chunk_strategy=$ChunkStrategy}
  $process = Start-Process -FilePath $python -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
  if (-not [RsiTopologyJob]::AssignProcessToJobObject($job, $process.Handle)) { throw "Failed to assign process to Job Object" }
  @{root_pid=$process.Id;owned_pids=@($process.Id)} | ConvertTo-Json | Set-Content -LiteralPath $pidPath -Encoding UTF8
  $previousIo = Get-IoBytes $process.Id
  $previousCpu = $process.TotalProcessorTime.TotalSeconds
  $previousTime = Get-Date
  $ioBreaches = 0
  $status = "running"
  while (-not $process.HasExited) {
    Start-Sleep -Seconds 1
    $process.Refresh()
    $now = Get-Date
    $elapsed = [math]::Max(($now - $previousTime).TotalSeconds, 0.001)
    $io = Get-IoBytes $process.Id
    $ioRate = [math]::Max(0.0, ($io - $previousIo) / 1MB / $elapsed)
    $cpuNow = $process.TotalProcessorTime.TotalSeconds
    $logical = [Environment]::ProcessorCount
    $cpuObserved = 100.0 * [math]::Max(0.0, $cpuNow - $previousCpu) / $elapsed / $logical
    $ram = $process.PrivateMemorySize64 / 1MB
    $peakRamMB = [math]::Max($peakRamMB, $ram)
    $ramSamples.Add($ram)
    $peakIoMBs = [math]::Max($peakIoMBs, $ioRate)
    $cpuSamples.Add($cpuObserved)
    if ($ram -gt $MemoryLimitMB) { $abortReason = "observed_private_memory_cap_exceeded"; Stop-Process -Id $process.Id -Force; break }
    if ($ioRate -gt $IoLimitMBps) { $ioBreaches++ } else { $ioBreaches = 0 }
    if ($ioBreaches -ge 3) { $abortReason = "sustained_io_cap_exceeded"; Stop-Process -Id $process.Id -Force; break }
    if (($now - $started).TotalSeconds -gt $TimeoutSeconds) { $abortReason = "timeout"; Stop-Process -Id $process.Id -Force; break }
    $previousIo = $io
    $previousCpu = $cpuNow
    $previousTime = $now
  }
  $process.WaitForExit()
  if ($abortReason) { $status = "aborted" } elseif ($peakRamMB -gt $MemoryLimitMB) { $status = "aborted"; $abortReason = "observed_private_memory_cap_exceeded" } elseif ($process.ExitCode -eq 0) { $status = "completed" } else { $status = "failed"; $abortReason = "exit_code_$($process.ExitCode)" }
} finally {
  if ($process -and -not $process.HasExited) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    $ownedStopped += $process.Id
  }
  $cleanup = if ($process) { Get-CleanupReceipt $process.Id } else { @{} }
  $cleanup["cleanup_passed"] = (@($cleanup.lingering_owned_pids).Count -eq 0)
  if (-not $cleanup["cleanup_passed"] -and $status -eq "completed") { $status = "cleanup_failed" }
  $summary = [ordered]@{
    run_id=$RunId;status=$status;abort_reason=$abortReason;peak_ram_mb=[math]::Round($peakRamMB,3);
    avg_ram_mb=$(if ($ramSamples.Count) {[math]::Round(($ramSamples | Measure-Object -Average).Average,3)} else {0});peak_io_mb_s=[math]::Round($peakIoMBs,3);
    cpu_pct=$(if ($cpuSamples.Count) {[math]::Round(($cpuSamples | Measure-Object -Average).Average,3)} else {0});
    steps_completed=$(if ($status -eq "completed") {2} else {0});checkpoints=@();owned_pids_stopped=$ownedStopped;
    wsl_docker_cleanup="not_used";cleanup=$cleanup;event_log=$eventPath;stdout=$stdoutPath;stderr=$stderrPath
  }
  $summary | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
  Write-Event @{event=$status;abort_reason=$abortReason;summary=$summaryPath}
  $summary | ConvertTo-Json -Depth 8
}
