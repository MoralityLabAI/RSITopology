param(
    [int]$Workers = 1
)

$ErrorActionPreference = "Stop"
$env:CUDA_VISIBLE_DEVICES = ""
$env:OMP_NUM_THREADS = "1"
$env:MKL_NUM_THREADS = "1"
$env:OPENBLAS_NUM_THREADS = "1"
$env:NUMEXPR_NUM_THREADS = "1"

$entries = @(
    "experiments/01_split_rate.py",
    "experiments/02_spectral_entropy.py",
    "experiments/03_finite_horizon.py",
    "experiments/04_transversal_index.py",
    "experiments/05_sufficiency_audit.py",
    "experiments/06_spin_glass.py"
)

foreach ($entry in $entries) {
    python $entry --workers $Workers
    if ($LASTEXITCODE -ne 0) {
        throw "Confinement smoke entry failed: $entry"
    }
}
