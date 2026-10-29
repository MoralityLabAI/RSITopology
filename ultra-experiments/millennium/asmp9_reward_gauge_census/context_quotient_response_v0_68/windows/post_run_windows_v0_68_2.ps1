param(
  [string]$RunId,
  [string]$PidFile,
  [string]$SummaryPath,
  [switch]$StopOwnedProcesses
)

$ErrorActionPreference = "Continue"
Set-StrictMode -Version Latest

function Get-MemorySnapshot {
  $os = Get-CimInstance Win32_OperatingSystem
  $pageFiles = @(Get-CimInstance Win32_PageFileUsage -ErrorAction SilentlyContinue)
  return [ordered]@{
    total_mb = [int]([double]$os.TotalVisibleMemorySize / 1024)
    free_mb = [int]([double]$os.FreePhysicalMemory / 1024)
    page_file_current_usage_mb = [int](
      ($pageFiles | Measure-Object CurrentUsage -Sum).Sum
    )
  }
}

function Get-GpuSnapshot {
  $gpu = @(& nvidia-smi `
    --query-gpu=name,temperature.gpu,memory.used,memory.total,utilization.gpu `
    --format=csv,noheader,nounits 2>$null)
  $apps = @(& nvidia-smi `
    --query-compute-apps=pid,process_name,used_memory `
    --format=csv,noheader,nounits 2>$null |
    Where-Object {
      $_ -and $_.Trim().Length -gt 0 -and $_ -notmatch "\[N/A\]"
    })
  return [ordered]@{ gpu = $gpu; compute_apps = $apps }
}

function Get-ProcessTree {
  param([int[]]$Roots)
  $all = @(Get-CimInstance Win32_Process)
  $seen = [Collections.Generic.HashSet[int]]::new()
  $queue = [Collections.Generic.Queue[int]]::new()
  foreach ($root in $Roots) {
    if ($root -gt 0 -and $seen.Add($root)) { $queue.Enqueue($root) }
  }
  while ($queue.Count -gt 0) {
    $parent = $queue.Dequeue()
    foreach ($child in @($all | Where-Object {
      $_.ParentProcessId -eq $parent
    })) {
      if ($seen.Add([int]$child.ProcessId)) {
        $queue.Enqueue([int]$child.ProcessId)
      }
    }
  }
  return @($seen)
}

$before = Get-MemorySnapshot
$gpuBefore = Get-GpuSnapshot
$ownedRoots = @()
if ($PidFile -and (Test-Path -LiteralPath $PidFile)) {
  try {
    $pidRecord = Get-Content -LiteralPath $PidFile -Raw | ConvertFrom-Json
    $ownedRoots = @($pidRecord.owned_pids | ForEach-Object { [int]$_ })
  } catch {}
}
$tree = @(Get-ProcessTree -Roots $ownedRoots)
$stopped = @()
if ($StopOwnedProcesses) {
  foreach ($ownedProcessId in ($tree | Sort-Object -Descending)) {
    $process = Get-Process -Id $ownedProcessId -ErrorAction SilentlyContinue
    if ($process) {
      try {
        Stop-Process -Id $ownedProcessId -Force -ErrorAction Stop
        $stopped += $ownedProcessId
      } catch {
        $stopped += "failed:$ownedProcessId"
      }
    }
  }
}
Start-Sleep -Seconds 2
$lingering = @($tree | Where-Object {
  Get-Process -Id $_ -ErrorAction SilentlyContinue
})
$after = Get-MemorySnapshot
$gpuAfter = Get-GpuSnapshot
$top = @(Get-Process | Sort-Object WorkingSet64 -Descending |
  Select-Object -First 12 Id,ProcessName,
    @{n="working_set_mb";e={[math]::Round($_.WorkingSet64 / 1MB, 1)}},
    @{n="private_mb";e={[math]::Round($_.PrivateMemorySize64 / 1MB, 1)}})
$summary = [ordered]@{
  schema_version = "asmp9_context_quotient_windows_cleanup_v0_68_2"
  run_id = $RunId
  ts_utc = (Get-Date).ToUniversalTime().ToString("o")
  owned_roots = $ownedRoots
  owned_process_tree = $tree
  stopped = $stopped
  lingering_owned_pids = $lingering
  memory_before = $before
  memory_after = $after
  gpu_before = $gpuBefore
  gpu_after = $gpuAfter
  top_processes = $top
  cleanup_passed = ($lingering.Count -eq 0)
}
$json = $summary | ConvertTo-Json -Depth 8 -Compress
$parent = Split-Path -Parent $SummaryPath
if ($parent -and -not (Test-Path -LiteralPath $parent)) {
  New-Item -ItemType Directory -Path $parent -Force | Out-Null
}
[IO.File]::WriteAllText(
  $SummaryPath,
  $json + "`n",
  [Text.UTF8Encoding]::new($false)
)
$json
