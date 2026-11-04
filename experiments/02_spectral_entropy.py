#!/usr/bin/env python
from __future__ import annotations

import os
from pathlib import Path
import sys

for name in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(name, "1")
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rsi_topology.confinement_experiments.cli import main


if __name__ == "__main__":
    main("02_spectral_entropy", "configs/smoke/02_spectral_entropy.yaml")
