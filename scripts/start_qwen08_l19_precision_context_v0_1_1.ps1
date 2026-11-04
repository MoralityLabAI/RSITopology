param(
  [Parameter(Mandatory=$true)][string]$RunSpecPath,
  [string]$WrapperPath = ""
)

$ErrorActionPreference = "Stop"
$specPath = (Resolve-Path -LiteralPath $RunSpecPath).Path
$spec = Get-Content -LiteralPath $specPath -Raw | ConvertFrom-Json
if ($spec.status -ne "authorized_for_analysis") { throw "Run spec is not authorized" }
if ([string]::IsNullOrWhiteSpace($WrapperPath)) {
  $WrapperPath = [string]$spec.hard_cap_wrapper.path
}
$wrapper = (Resolve-Path -LiteralPath $WrapperPath).Path
$wrapperHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $wrapper).Hash.ToLowerInvariant()
if ($wrapperHash -ne [string]$spec.hard_cap_wrapper.sha256) { throw "Wrapper hash differs from authorization" }
$runDir = [System.IO.Path]::GetFullPath([string]$spec.wrapper_output_dir)
New-Item -ItemType Directory -Force -Path $runDir | Out-Null
$launcherReceipt = Join-Path $runDir "detached_launcher_receipt.json"
if (Test-Path -LiteralPath $launcherReceipt) { throw "Detached launcher receipt already exists" }
$argumentList = @(
  "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $wrapper,
  "-RunSpecPath", $specPath
)
$process = Start-Process -FilePath "powershell.exe" -ArgumentList $argumentList -WindowStyle Hidden -PassThru
$receipt = [ordered]@{
  schema_version = "qwen08_l19_precision_context_detached_launcher_v0_1_1"
  created_utc = [DateTime]::UtcNow.ToString("o")
  wrapper_pid = $process.Id
  run_spec_path = $specPath
  run_spec_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $specPath).Hash.ToLowerInvariant()
  wrapper_path = $wrapper
  wrapper_sha256 = $wrapperHash
  detached = $true
}
[System.IO.File]::WriteAllText($launcherReceipt, ($receipt | ConvertTo-Json -Depth 6), [System.Text.UTF8Encoding]::new($false))
$receipt | ConvertTo-Json -Depth 6
