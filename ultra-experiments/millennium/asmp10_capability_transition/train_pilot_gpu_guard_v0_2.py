"""Additive CUDA-allocation and global-memory guard for the v0.1 pilot trainer."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any


os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch  # noqa: E402

import train_pilot  # noqa: E402


def gpu_used_mb() -> float:
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    values = [float(line.strip()) for line in completed.stdout.splitlines() if line.strip()]
    if len(values) != 1:
        raise RuntimeError(f"expected one GPU memory value, received {values}")
    return values[0]


def parse_config_and_output(argv: list[str]) -> tuple[dict[str, Any], Path]:
    config_index = argv.index("--config") + 1
    output_index = argv.index("--output-dir") + 1
    config = json.loads(Path(argv[config_index]).resolve().read_text(encoding="utf-8"))
    return config, Path(argv[output_index]).resolve()


class GpuGuard:
    def __init__(self, allowance_mb: float, output_dir: Path) -> None:
        self.allowance_mb = allowance_mb
        self.output_dir = output_dir
        self.triggered = False
        self.ever_triggered = False
        self.latest_used_mb = gpu_used_mb()
        self.peak_used_mb = self.latest_used_mb
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._poll, name="asmp10-gpu-guard", daemon=True)

    def _poll(self) -> None:
        while not self._stop.wait(1.0):
            try:
                used = gpu_used_mb()
                with self._lock:
                    self.latest_used_mb = used
                    self.peak_used_mb = max(self.peak_used_mb, used)
                    if used > self.allowance_mb:
                        self.triggered = True
                        self.ever_triggered = True
            except Exception:
                with self._lock:
                    self.triggered = True
                    self.ever_triggered = True

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._thread.join(timeout=5)
        record = {
            "schema_version": "asmp10_gpu_guard_summary_v0_2",
            "allowance_mb": self.allowance_mb,
            "latest_used_mb": self.latest_used_mb,
            "peak_used_mb": self.peak_used_mb,
            "triggered": self.ever_triggered,
        }
        train_pilot.atomic_write(
            self.output_dir / "gpu_guard_summary.json",
            train_pilot.canonical_json(record).encode("utf-8"),
        )

    def check(self) -> None:
        with self._lock:
            if self.triggered:
                # Clear before raising so the trainer's abort event and summary
                # can be written through the original append path.
                self.triggered = False
                raise RuntimeError(
                    f"gpu_allowance_exceeded_or_monitor_failed: "
                    f"used={self.latest_used_mb:.1f}MB allowance={self.allowance_mb:.1f}MB"
                )


def main() -> int:
    config, output_dir = parse_config_and_output(sys.argv[1:])
    allowance_mb = float(config["resource_intent"]["gpu_allowance_mb"])
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable")
    total_mb = torch.cuda.get_device_properties(0).total_memory / (1024**2)
    fraction = min(0.65, 0.90 * allowance_mb / total_mb)
    torch.cuda.set_per_process_memory_fraction(fraction, device=0)
    guard = GpuGuard(allowance_mb=allowance_mb, output_dir=output_dir)
    original_append = train_pilot.append_event

    def guarded_append(path: Path, event: dict[str, Any]) -> None:
        guard.check()
        original_append(
            path,
            {
                **event,
                "gpu_used_mb_guard": guard.latest_used_mb,
                "gpu_allowance_mb_guard": allowance_mb,
            },
        )

    train_pilot.append_event = guarded_append
    guard.start()
    original_append(
        output_dir / "events.jsonl",
        {
            "event": "gpu_guard_start",
            "allowance_mb": allowance_mb,
            "allocator_fraction": fraction,
            "total_gpu_mb": total_mb,
            "initial_used_mb": guard.latest_used_mb,
        },
    )
    try:
        return train_pilot.main()
    finally:
        guard.stop()
        if torch.cuda.is_available():
            torch.cuda.synchronize()
            torch.cuda.empty_cache()
            if hasattr(torch.cuda, "ipc_collect"):
                torch.cuda.ipc_collect()


if __name__ == "__main__":
    raise SystemExit(main())
