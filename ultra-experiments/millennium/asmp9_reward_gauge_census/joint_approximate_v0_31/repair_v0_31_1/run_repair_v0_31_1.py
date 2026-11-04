from __future__ import annotations

import ctypes
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ORIGINAL_DIR = HERE.parent
ORIGINAL_RUNNER = ORIGINAL_DIR / "run_verification_v0_31.py"


def fixed_peak_resident_bytes() -> int:
    if sys.platform == "win32":
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(),
            ctypes.byref(counters),
            counters.cb,
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(counters.PeakWorkingSetSize)
    import resource

    return int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)


def load_original_runner():
    sys.path.insert(0, str(ORIGINAL_DIR))
    spec = importlib.util.spec_from_file_location(
        "sealed_joint_approximate_v0_31_runner",
        ORIGINAL_RUNNER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load sealed v0.31 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    runner = load_original_runner()
    runner.peak_resident_bytes = fixed_peak_resident_bytes
    runner.main()


if __name__ == "__main__":
    main()
