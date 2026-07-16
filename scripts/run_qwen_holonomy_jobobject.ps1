param(
  [Parameter(Mandatory=$true)][string]$RunSpecPath
)

$ErrorActionPreference = "Stop"
$specPath = (Resolve-Path -LiteralPath $RunSpecPath).Path
$spec = Get-Content -LiteralPath $specPath -Raw | ConvertFrom-Json
if ($spec.schema_version -notin @(
  "qwen_holonomy_state_capture_authorization_v0_1",
  "qwen_holonomy_geometry_analysis_authorization_v0_1",
  "qwen_holonomy_jobobject_probe_v0_1"
)) { throw "Unsupported run-spec schema" }
$caps = $spec.resource_caps
foreach ($field in @("memory_mb", "cpu_percent", "io_mb_s", "timeout_seconds")) {
  if ([double]$caps.$field -le 0) { throw "Missing positive cap: $field" }
}
if ([int]$caps.swap_bytes -ne 0) { throw "Only zero registered swap is accepted" }
$command = @($spec.exact_inner_command)
if ($command.Count -lt 2) { throw "Run spec has no executable command" }
$python = (Resolve-Path -LiteralPath ([string]$command[0])).Path
$arguments = @($command | Select-Object -Skip 1 | ForEach-Object { [string]$_ })
$runDir = [System.IO.Path]::GetFullPath([string]$spec.wrapper_output_dir)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$eventsPath = Join-Path $runDir "wrapper_events.jsonl"
$summaryPath = Join-Path $runDir "wrapper_summary.json"
$stdoutPath = Join-Path $runDir "wrapper_stdout.txt"
$stderrPath = Join-Path $runDir "wrapper_stderr.txt"
$pidPath = Join-Path $runDir "owned_pids.json"
$cleanupPath = Join-Path $runDir "cleanup_summary.json"
$cleanupScript = [string]$spec.cleanup_script.path
if (-not (Test-Path -LiteralPath $cleanupScript)) { throw "Cleanup script missing" }

function Write-WrapperEvent([hashtable]$Value) {
  $Value.ts_utc = [DateTime]::UtcNow.ToString("o")
  Add-Content -LiteralPath $eventsPath -Value ($Value | ConvertTo-Json -Compress -Depth 8) -Encoding UTF8
}

function Get-IoBytes([int]$OwnedProcessId) {
  $item = Get-CimInstance Win32_Process -Filter "ProcessId=$OwnedProcessId" -ErrorAction SilentlyContinue
  if ($null -eq $item) { return 0.0 }
  return [double]$item.ReadTransferCount + [double]$item.WriteTransferCount
}

function Get-GpuMemoryMb([int]$OwnedProcessId) {
  if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) { return 0.0 }
  $lines = @(& nvidia-smi --query-compute-apps=pid,used_gpu_memory --format=csv,noheader,nounits 2>$null)
  $total = 0.0
  foreach ($line in $lines) {
    $parts = $line -split ","
    if ($parts.Count -ge 2 -and $parts[0].Trim() -eq "$OwnedProcessId") {
      $value = 0.0
      if ([double]::TryParse($parts[1].Trim(), [ref]$value)) { $total += $value }
    }
  }
  return $total
}

Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class QwenHolonomyJob {
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr CreateJobObject(IntPtr a, string n);
  [DllImport("kernel32.dll")] public static extern bool AssignProcessToJobObject(IntPtr j, IntPtr p);
  [DllImport("kernel32.dll")] public static extern bool SetInformationJobObject(IntPtr j, int t, IntPtr i, uint s);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
  [DllImport("kernel32.dll")] public static extern bool QueryInformationJobObject(IntPtr j, int t, IntPtr i, uint s, IntPtr r);
  public const int Extended = 9;
  public const int Cpu = 15;
  public const uint ProcessMemory = 0x00000100;
  public const uint JobMemory = 0x00000200;
  public const uint KillOnClose = 0x00002000;
  public const uint CpuEnable = 0x1;
  public const uint CpuHardCap = 0x4;
  [StructLayout(LayoutKind.Sequential)] public struct IO_COUNTERS { public ulong ReadOperationCount,WriteOperationCount,OtherOperationCount,ReadTransferCount,WriteTransferCount,OtherTransferCount; }
  [StructLayout(LayoutKind.Sequential)] public struct BASIC_LIMIT_INFORMATION { public long PerProcessUserTimeLimit,PerJobUserTimeLimit; public uint LimitFlags; public UIntPtr MinimumWorkingSetSize,MaximumWorkingSetSize; public uint ActiveProcessLimit; public UIntPtr Affinity; public uint PriorityClass,SchedulingClass; }
  [StructLayout(LayoutKind.Sequential)] public struct EXTENDED_LIMIT_INFORMATION { public BASIC_LIMIT_INFORMATION BasicLimitInformation; public IO_COUNTERS IoInfo; public UIntPtr ProcessMemoryLimit,JobMemoryLimit,PeakProcessMemoryUsed,PeakJobMemoryUsed; }
  [StructLayout(LayoutKind.Sequential)] public struct CPU_RATE_CONTROL_INFORMATION { public uint ControlFlags,CpuRate; }

  public static bool ConfigureMemory(IntPtr job, ulong bytes) {
    var info = new EXTENDED_LIMIT_INFORMATION();
    info.BasicLimitInformation.LimitFlags = ProcessMemory | JobMemory | KillOnClose;
    info.ProcessMemoryLimit = new UIntPtr(bytes);
    info.JobMemoryLimit = new UIntPtr(bytes);
    int size = Marshal.SizeOf(info);
    IntPtr ptr = Marshal.AllocHGlobal(size);
    try { Marshal.StructureToPtr(info, ptr, false); return SetInformationJobObject(job, Extended, ptr, (uint)size); }
    finally { Marshal.FreeHGlobal(ptr); }
  }
  public static bool ConfigureCpu(IntPtr job, uint rate) {
    var info = new CPU_RATE_CONTROL_INFORMATION();
    info.ControlFlags = CpuEnable | CpuHardCap;
    info.CpuRate = rate;
    int size = Marshal.SizeOf(info);
    IntPtr ptr = Marshal.AllocHGlobal(size);
    try { Marshal.StructureToPtr(info, ptr, false); return SetInformationJobObject(job, Cpu, ptr, (uint)size); }
    finally { Marshal.FreeHGlobal(ptr); }
  }
  public static ulong QueryMemoryLimit(IntPtr job) {
    int size = Marshal.SizeOf(typeof(EXTENDED_LIMIT_INFORMATION));
    IntPtr ptr = Marshal.AllocHGlobal(size);
    try {
      if (!QueryInformationJobObject(job, Extended, ptr, (uint)size, IntPtr.Zero)) return 0;
      var info = (EXTENDED_LIMIT_INFORMATION)Marshal.PtrToStructure(ptr, typeof(EXTENDED_LIMIT_INFORMATION));
      return info.JobMemoryLimit.ToUInt64();
    } finally { Marshal.FreeHGlobal(ptr); }
  }
  public static uint QueryCpuRate(IntPtr job) {
    int size = Marshal.SizeOf(typeof(CPU_RATE_CONTROL_INFORMATION));
    IntPtr ptr = Marshal.AllocHGlobal(size);
    try {
      if (!QueryInformationJobObject(job, Cpu, ptr, (uint)size, IntPtr.Zero)) return 0;
      var info = (CPU_RATE_CONTROL_INFORMATION)Marshal.PtrToStructure(ptr, typeof(CPU_RATE_CONTROL_INFORMATION));
      return info.CpuRate;
    } finally { Marshal.FreeHGlobal(ptr); }
  }
}
'@

$memoryBytes = [UInt64]([double]$caps.memory_mb * 1MB)
$cpuRate = [UInt32]([double]$caps.cpu_percent * 100)
$job = [QwenHolonomyJob]::CreateJobObject([IntPtr]::Zero, "qwen-holonomy-$([guid]::NewGuid())")
if ($job -eq [IntPtr]::Zero) { throw "CreateJobObject failed" }
$memorySet = $false
$cpuSet = $false
$queriedMemoryBytes = [UInt64]0
$queriedCpuRate = [UInt32]0
$proc = $null
$status = "failed_before_start"
$abortReason = $null
$exitCode = $null
$peakRam = 0.0
$peakIo = 0.0
$peakGpu = 0.0
$ramSamples = New-Object System.Collections.Generic.List[double]
$cpuSamples = New-Object System.Collections.Generic.List[double]
$started = Get-Date
try {
  $memorySet = [QwenHolonomyJob]::ConfigureMemory($job, $memoryBytes)
  if (-not $memorySet) { throw "Failed to set aggregate/process memory cap" }
  $queriedMemoryBytes = [QwenHolonomyJob]::QueryMemoryLimit($job)
  if ($queriedMemoryBytes -ne $memoryBytes) { throw "Job memory cap query-back mismatch" }
  $cpuSet = [QwenHolonomyJob]::ConfigureCpu($job, $cpuRate)
  if (-not $cpuSet) { throw "Failed to set hard CPU cap" }
  $queriedCpuRate = [QwenHolonomyJob]::QueryCpuRate($job)
  if ($queriedCpuRate -ne $cpuRate) { throw "Job CPU cap query-back mismatch" }

  Write-WrapperEvent @{event="start";run_id=$spec.run_id;caps=$caps;command=$command}
  $proc = Start-Process -FilePath $python -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
  if (-not [QwenHolonomyJob]::AssignProcessToJobObject($job, $proc.Handle)) { throw "AssignProcessToJobObject failed" }
  @{root_pid=$proc.Id;owned_pids=@($proc.Id);run_id=$spec.run_id} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $pidPath -Encoding UTF8
  $status = "running"
  $previousIo = Get-IoBytes $proc.Id
  $previousCpu = $proc.TotalProcessorTime.TotalSeconds
  $previousTime = Get-Date
  $ioBreaches = 0
  while (-not $proc.HasExited) {
    Start-Sleep -Seconds 1
    $proc.Refresh()
    if ($proc.HasExited) { break }
    $now = Get-Date
    $elapsed = [math]::Max(($now - $previousTime).TotalSeconds, 0.001)
    $io = Get-IoBytes $proc.Id
    $ioRate = [math]::Max(0.0, ($io - $previousIo) / 1MB / $elapsed)
    $cpuNow = $proc.TotalProcessorTime.TotalSeconds
    $cpuPct = 100.0 * [math]::Max(0.0, $cpuNow - $previousCpu) / $elapsed / [Environment]::ProcessorCount
    $ramMb = $proc.PrivateMemorySize64 / 1MB
    $gpuMb = Get-GpuMemoryMb $proc.Id
    $peakRam = [math]::Max($peakRam, $ramMb)
    $peakIo = [math]::Max($peakIo, $ioRate)
    $peakGpu = [math]::Max($peakGpu, $gpuMb)
    $ramSamples.Add($ramMb)
    $cpuSamples.Add($cpuPct)
    if ($ioRate -gt [double]$caps.io_mb_s) { $ioBreaches++ } else { $ioBreaches = 0 }
    if ($ioBreaches -ge 3) { $abortReason = "sustained_io_cap_exceeded" }
    if ($gpuMb -gt [double]$caps.gpu_allowance_mb) { $abortReason = "gpu_allowance_exceeded" }
    if (($now - $started).TotalSeconds -gt [double]$caps.timeout_seconds) { $abortReason = "timeout" }
    if ($abortReason) {
      Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
      break
    }
    $previousIo = $io
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
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
} finally {
  if ($proc -and -not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
  if ($job -ne [IntPtr]::Zero) { [void][QwenHolonomyJob]::CloseHandle($job) }
  & $cleanupScript -RunId ([string]$spec.run_id) -PidFile $pidPath -StopOwnedProcesses -SummaryPath $cleanupPath -WaitSeconds 1 | Out-Null
  $cleanup = if (Test-Path -LiteralPath $cleanupPath) { Get-Content $cleanupPath -Raw | ConvertFrom-Json } else { $null }
  if ($cleanup -eq $null -or $cleanup.cleanup_passed -ne $true) {
    if ($status -eq "completed") { $status = "cleanup_failed" }
  }
  $steps = 0
  $innerSummaryPath = if ($spec.capture_parameters) { Join-Path ([string]$spec.capture_parameters.output_dir) "summary.json" } else { "" }
  if ($innerSummaryPath -and (Test-Path -LiteralPath $innerSummaryPath)) {
    $inner = Get-Content $innerSummaryPath -Raw | ConvertFrom-Json
    if ($inner.PSObject.Properties.Name -contains "chunks_completed") { $steps = [int]$inner.chunks_completed }
  }
  $summary = [ordered]@{
    schema_version = "qwen_holonomy_jobobject_summary_v0_1"
    run_id = [string]$spec.run_id
    status = $status
    abort_reason = $abortReason
    exit_code = $exitCode
    memory_cap_set = $memorySet
    cpu_cap_set = $cpuSet
    queried_memory_limit_bytes = $queriedMemoryBytes
    queried_cpu_rate = $queriedCpuRate
    caps = $caps
    peak_ram_mb = [math]::Round($peakRam, 3)
    avg_ram_mb = $(if ($ramSamples.Count) {[math]::Round(($ramSamples | Measure-Object -Average).Average, 3)} else {0})
    peak_io_mb_s = [math]::Round($peakIo, 3)
    cpu_pct = $(if ($cpuSamples.Count) {[math]::Round(($cpuSamples | Measure-Object -Average).Average, 3)} else {0})
    peak_gpu_mb = [math]::Round($peakGpu, 3)
    steps_completed = $steps
    checkpoint_strategy = [string]$spec.checkpoint_strategy
    elapsed_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 3)
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
