#!/usr/bin/env bash
set -euo pipefail

RUN_ROOT="${RUN_ROOT:-/workspace/asmp9_physical_v0343}"
REPO_COMMIT="${REPO_COMMIT:?exact RSITopology commit required}"
LLAMA_COMMIT="${LLAMA_COMMIT:-86d86ed4396b4130922f7b9af26e3d9fc11a591b}"

sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  build-essential \
  ca-certificates \
  cuda-toolkit-12-8 \
  cmake \
  g++-12 \
  git

mkdir -p "${RUN_ROOT}/model" "${RUN_ROOT}/input"

if [[ ! -d "${RUN_ROOT}/repo/.git" ]]; then
  git clone https://github.com/MoralityLabAI/RSITopology.git \
    "${RUN_ROOT}/repo"
fi
git -C "${RUN_ROOT}/repo" fetch origin \
  feat/spectral-bundle-v0.3-bifiltration
git -C "${RUN_ROOT}/repo" checkout --detach "${REPO_COMMIT}"

if [[ ! -d /workspace/llama.cpp/.git ]]; then
  git clone https://github.com/ggml-org/llama.cpp.git /workspace/llama.cpp
fi
git -C /workspace/llama.cpp fetch --tags origin
git -C /workspace/llama.cpp checkout --detach "${LLAMA_COMMIT}"

cmake \
  -S /workspace/llama.cpp \
  -B /workspace/llama.cpp/build-sm89 \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-12 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-12.8/bin/nvcc \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-12 \
  -DCUDAToolkit_ROOT=/usr/local/cuda-12.8 \
  -DCMAKE_CUDA_ARCHITECTURES=89-real \
  -DGGML_CUDA=ON \
  -DGGML_CUDA_FA=ON \
  -DGGML_CUDA_COMPRESSION_MODE=size \
  -DGGML_CUDA_NCCL=ON \
  -DLLAMA_CURL=OFF
cmake --build /workspace/llama.cpp/build-sm89 \
  --target llama-server \
  --parallel 6

{
  date -u +setup_completed_utc=%Y-%m-%dT%H:%M:%SZ
  uname -a
  nvidia-smi \
    --query-gpu=name,uuid,driver_version,memory.total \
    --format=csv,noheader
  /usr/local/cuda-12.8/bin/nvcc --version
  python3 --version
  git -C "${RUN_ROOT}/repo" rev-parse HEAD
  git -C /workspace/llama.cpp rev-parse HEAD
  sha256sum /workspace/llama.cpp/build-sm89/bin/llama-server
  sha256sum /workspace/llama.cpp/build-sm89/bin/libggml-cuda.so.0.17.0
} > "${RUN_ROOT}/setup_facts.txt"
