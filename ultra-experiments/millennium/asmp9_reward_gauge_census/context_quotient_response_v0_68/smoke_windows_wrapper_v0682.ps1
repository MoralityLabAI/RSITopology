param(
  [string]$OutputRoot = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $OutputRoot) {
  $OutputRoot = Join-Path $env:TEMP (
    "asmp9-v0682-wrapper-smoke-" + [Guid]::NewGuid().ToString("N")
  )
}
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$caps = [ordered]@{
  memory_mb = 512
  minimum_free_memory_mb = 1024
  cpu_percent = 50
  io_mb_s = 50
  io_sustained_samples = 5
  gpu_allowance_mb = 3900
  gpu_clean_start_ceiling_mb = 64
  temperature_limit_c = 88
  timeout_seconds = 60
  batch_size = 1
  max_prompt_tokens = 768
  checkpoint_every_records = 1
  poll_seconds = 1
  minimum_runtime_free_memory_mb = 1024
  swap_policy = "detect_and_invalidate_cleanup"
}
$registration = [ordered]@{
  status = "registered_prereveal"
  outcomes_read = $false
  phase = "confirmation"
  execution_contract_version = "local_windows_v0_68_2"
  resource_contract = $caps
}
$registrationPath = Join-Path $OutputRoot "registration.json"
[IO.File]::WriteAllText(
  $registrationPath,
  ($registration | ConvertTo-Json -Depth 8 -Compress) + "`n",
  [Text.UTF8Encoding]::new($false)
)
$wrapper = Join-Path $here "windows\run_windows_guarded_v0_68_2.ps1"
$cleanup = Join-Path $here "windows\post_run_windows_v0_68_2.ps1"
$python = (Get-Command python).Source
$authorization = [ordered]@{
  schema_version = "asmp9_context_quotient_authorization_v0_68_2_windows"
  run_id = "asmp9-v0682-wrapper-smoke"
  phase = "confirmation"
  exact_runner_command = @($python, "-c", "print('runner-smoke')")
  exact_analysis_command = @($python, "-c", "print('analysis-smoke')")
  wrapper_output_dir = (Join-Path $OutputRoot "wrapper")
  capture_parameters = @{
    result_dir = (Join-Path $OutputRoot "result")
    analysis_dir = (Join-Path $OutputRoot "analysis")
  }
  resource_caps = $caps
  hard_cap_wrapper = @{
    path = $wrapper
    sha256 = (Get-FileHash $wrapper -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  cleanup_script = @{
    path = $cleanup
    sha256 = (Get-FileHash $cleanup -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  registration = @{
    path = $registrationPath
    sha256 = (
      Get-FileHash $registrationPath -Algorithm SHA256
    ).Hash.ToLowerInvariant()
  }
}
$authorizationPath = Join-Path $OutputRoot "authorization.json"
[IO.File]::WriteAllText(
  $authorizationPath,
  ($authorization | ConvertTo-Json -Depth 10 -Compress) + "`n",
  [Text.UTF8Encoding]::new($false)
)
& powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File $wrapper -AuthorizationPath $authorizationPath
if ($LASTEXITCODE -ne 0) {
  throw "wrapper smoke failed with exit code $LASTEXITCODE"
}
$summary = Get-ChildItem -LiteralPath (
  Join-Path $OutputRoot "wrapper\attempts"
) -Filter "wrapper_summary.json" -Recurse | Select-Object -First 1
if (-not $summary) { throw "wrapper summary was not written" }
$value = Get-Content -LiteralPath $summary.FullName -Raw | ConvertFrom-Json
if ($value.status -ne "completed") {
  throw "wrapper smoke status is $($value.status)"
}
$value | ConvertTo-Json -Depth 10
