from __future__ import annotations

import ctypes
import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREDECESSOR = HERE.parent / "repair_v0_26_1" / "adjudicate_v0_26_1.py"


def load_predecessor():
    spec = importlib.util.spec_from_file_location(
        "offset_access_repair_v0_26_1", PREDECESSOR
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load sealed predecessor")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def corrected_peak_resident_bytes() -> int:
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

        value = Counters()
        value.cb = ctypes.sizeof(value)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = (
            wintypes.HANDLE,
            ctypes.POINTER(Counters),
            wintypes.DWORD,
        )
        if not psapi.GetProcessMemoryInfo(
            kernel32.GetCurrentProcess(), ctypes.byref(value), value.cb
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return int(value.PeakWorkingSetSize)
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)
    return int(usage.ru_maxrss * (1 if sys.platform == "darwin" else 1024))


def output_directory_from_argv() -> Path:
    index = sys.argv.index("--output-dir")
    return Path(sys.argv[index + 1]).resolve()


def main() -> None:
    output_dir = output_directory_from_argv()
    predecessor = load_predecessor()
    predecessor.peak_resident_bytes = corrected_peak_resident_bytes
    predecessor.main()
    (output_dir / "result_v0_26_1.json").replace(
        output_dir / "result_v0_26_2.json"
    )
    (output_dir / "run_receipt_v0_26_1.json").replace(
        output_dir / "run_receipt_v0_26_2.json"
    )


if __name__ == "__main__":
    main()
