#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${RUN_ROOT:-/workspace/asmp9_dynamic_v067}"
REPO_COMMIT="${REPO_COMMIT:?exact RSITopology commit required}"
REPO_ROOT="${RUN_ROOT}/repo"
VENV="${RUN_ROOT}/venv"

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates \
  git \
  python3-venv \
  rsync

mkdir -p "${RUN_ROOT}/model" "${RUN_ROOT}/construction"
if [[ ! -d "${REPO_ROOT}/.git" ]]; then
  git clone https://github.com/MoralityLabAI/RSITopology.git "${REPO_ROOT}"
fi
git -C "${REPO_ROOT}" fetch origin feat/spectral-bundle-v0.3-bifiltration
git -C "${REPO_ROOT}" checkout --detach "${REPO_COMMIT}"

if [[ ! -x "${VENV}/bin/python" ]]; then
  python3 -m venv --system-site-packages "${VENV}"
fi
"${VENV}/bin/python" -m pip install --disable-pip-version-check --upgrade \
  "jinja2==3.1.6" \
  "transformers==5.3.0" \
  "accelerate==1.12.0" \
  "safetensors==0.6.2"

"${VENV}/bin/python" - <<'PY'
import json
import torch
import transformers
import accelerate
import safetensors
import jinja2

if not torch.cuda.is_available():
    raise SystemExit("CUDA unavailable in staged runtime")
print(json.dumps({
    "torch": torch.__version__,
    "transformers": transformers.__version__,
    "accelerate": accelerate.__version__,
    "safetensors": safetensors.__version__,
    "jinja2": jinja2.__version__,
    "cuda": True,
}, sort_keys=True))
PY

{
  date -u +setup_completed_utc=%Y-%m-%dT%H:%M:%SZ
  uname -a
  nvidia-smi \
    --query-gpu=name,uuid,driver_version,memory.total \
    --format=csv,noheader
  "${VENV}/bin/python" --version
  git -C "${REPO_ROOT}" rev-parse HEAD
  sha256sum \
    "${REPO_ROOT}/ultra-experiments/millennium/asmp9_reward_gauge_census/physical_dynamic_bridge_v0_67/protocol_v0_67.json"
} > "${RUN_ROOT}/setup_facts.txt"
