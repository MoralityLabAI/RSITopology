#!/usr/bin/env bash
set -euo pipefail

export CUDA_VISIBLE_DEVICES=""
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

PROFILE="${PROFILE:-pilot}"
WORKERS="${WORKERS:-1}"
ENTRIES=(
  experiments/01_split_rate.py
  experiments/02_spectral_entropy.py
  experiments/03_finite_horizon.py
  experiments/04_transversal_index.py
  experiments/05_sufficiency_audit.py
  experiments/06_spin_glass.py
)

INDEX="${SLURM_ARRAY_TASK_ID:?SLURM_ARRAY_TASK_ID must be 0..5}"
ENTRY="${ENTRIES[$INDEX]}"
NAME="$(basename "$ENTRY" .py)"
CONFIG="configs/${PROFILE}/${NAME}.yaml"

python "$ENTRY" --config "$CONFIG" --workers "$WORKERS"
