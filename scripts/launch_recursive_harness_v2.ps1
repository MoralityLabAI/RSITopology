param(
  [Parameter(Mandatory=$true)][string]$Registration,
  [Parameter(Mandatory=$true)][string]$PrePayload,
  [Parameter(Mandatory=$true)][string]$PreAnchorReceipt,
  [Parameter(Mandatory=$true)][string]$RunDir,
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$registrationPath = (Resolve-Path -LiteralPath $Registration).Path
$prePayloadPath = (Resolve-Path -LiteralPath $PrePayload).Path
$preAnchorPath = (Resolve-Path -LiteralPath $PreAnchorReceipt).Path
$RunDir = [IO.Path]::GetFullPath($RunDir)
if(Test-Path -LiteralPath $RunDir){
  throw "RunDir is write-once and must not already exist: $RunDir"
}
New-Item -ItemType Directory -Path $RunDir | Out-Null
$authorizationPath = Join-Path $RunDir "launch_authorization.json"
$eventPath = Join-Path $RunDir "events.jsonl"
$summaryPath = Join-Path $RunDir "summary.json"
$pidPath = Join-Path $RunDir "owned_pids.json"

function Write-Event([hashtable]$Payload) {
  $Payload.ts_utc = [DateTime]::UtcNow.ToString("o")
  Add-Content -LiteralPath $eventPath -Value ($Payload | ConvertTo-Json -Compress -Depth 7) -Encoding UTF8
}

try {
  & $PythonExe (Join-Path $root "scripts\authorize_recursive_run_v2.py") `
    --registration $registrationPath `
    --pre-payload $prePayloadPath `
    --pre-anchor-receipt $preAnchorPath `
    --output $authorizationPath | Out-Null
  if($LASTEXITCODE -ne 0){ throw "Run authorization failed." }
  $authorization = Get-Content -Raw -LiteralPath $authorizationPath | ConvertFrom-Json
  if($authorization.status -ne "authorized_for_registered_launch"){
    throw "Authorization receipt is not launch-valid."
  }
  $command = @($authorization.exact_command)
  if($command.Count -lt 2){ throw "Registered exact command is incomplete." }
  Write-Event @{event="authorized_start";run_id=$authorization.run_id;command_sha256=$authorization.exact_command_sha256}
  $process = Start-Process -FilePath $command[0] -ArgumentList $command[1..($command.Count - 1)] -PassThru -WindowStyle Hidden
  @{root_pid=$process.Id;owned_pids=@($process.Id)} | ConvertTo-Json | Set-Content -LiteralPath $pidPath -Encoding UTF8
  $process.WaitForExit()
  $cleanupPath = [string]$authorization.resource_envelope.cleanup_script.path
  $cleanupSummaryPath = Join-Path $RunDir "cleanup_summary.json"
  & $cleanupPath -RunId $authorization.run_id -PidFile $pidPath -StopOwnedProcesses -SummaryPath $cleanupSummaryPath -WaitSeconds 1 | Out-Null
  $cleanup = Get-Content -Raw -LiteralPath $cleanupSummaryPath | ConvertFrom-Json
  $status = if(-not $cleanup.cleanup_passed){"cleanup_failed"}elseif($process.ExitCode -eq 0){"completed"}else{"failed"}
  $reportedExitCode = if($status -eq "cleanup_failed"){127}else{$process.ExitCode}
  $summary = [ordered]@{
    schema_version="proposal_recursive_launch_summary_v1"
    run_id=$authorization.run_id
    status=$status
    exit_code=$reportedExitCode
    authorization_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $authorizationPath).Hash.ToLowerInvariant()
    owned_pids=@($process.Id)
    cleanup_status=$status
    cleanup_summary=$cleanupSummaryPath
  }
  $summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
  Write-Event @{event=$status;exit_code=$reportedExitCode;summary=$summaryPath}
  exit $reportedExitCode
} catch {
  if((Test-Path -LiteralPath $pidPath) -and $null -ne $authorization){
    try {
      $cleanupPath = [string]$authorization.resource_envelope.cleanup_script.path
      & $cleanupPath -RunId $authorization.run_id -PidFile $pidPath -StopOwnedProcesses -SummaryPath (Join-Path $RunDir "cleanup_summary.json") -WaitSeconds 1 | Out-Null
    } catch {}
  }
  $failure = [ordered]@{
    schema_version="proposal_recursive_launch_summary_v1"
    status="blocked_or_failed"
    error=$_.Exception.Message
    scientific_run_started=(Test-Path -LiteralPath $pidPath)
  }
  $failure | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $summaryPath -Encoding UTF8
  Write-Event @{event="blocked_or_failed";error=$_.Exception.Message}
  throw
}
