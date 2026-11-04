"""Run every ASMP package's tests, one pytest process per directory.

The millennium tree intentionally reuses flat module names (run.py,
verify_independent.py, ...), so collecting everything into one interpreter
collides on the module cache.  This runner finds every directory under
ultra-experiments/millennium that holds a test_*.py file and runs pytest
there in its own process, then prints a summary table.

Usage:
  python scripts/run_package_tests.py [--filter asmp12] [--timeout 900] [--jobs 1] [--list]
Exit status is 1 if any package failed.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MILLENNIUM = os.path.join(ROOT, "ultra-experiments", "millennium")
SUMMARY_RE = re.compile(r"(\d+) passed|(\d+) failed|(\d+) error", re.I)


def find_packages(filter_: str) -> list[str]:
    pkgs = []
    for dirpath, dirnames, filenames in os.walk(MILLENNIUM):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".pytest_cache", "artifacts")] if False else [d for d in dirnames if d not in ("__pycache__", ".pytest_cache")]
        if any(f.startswith("test_") and f.endswith(".py") for f in filenames):
            rel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
            if not filter_ or filter_ in rel:
                pkgs.append(rel)
    return sorted(pkgs)


def run_one(rel: str, timeout: int) -> tuple[str, str, float, str]:
    t0 = time.time()
    env = dict(os.environ)
    env["PYTHONPATH"] = ROOT
    # only this directory's own test files: versioned subpackages are run separately,
    # and recursing into them would reintroduce the module-name collision
    tests = sorted(f for f in os.listdir(os.path.join(ROOT, rel)) if f.startswith("test_") and f.endswith(".py"))
    cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", os.path.join(ROOT, rel)] + tests
    try:
        p = subprocess.run(cmd, cwd=os.path.join(ROOT, rel), capture_output=True, text=True, timeout=timeout, env=env)
        out = (p.stdout or "") + (p.stderr or "")
        tail = out.strip().splitlines()[-1] if out.strip() else ""
        status = "pass" if p.returncode == 0 else ("no-tests" if p.returncode == 5 else "FAIL")
    except subprocess.TimeoutExpired:
        status, tail = "TIMEOUT", f"exceeded {timeout}s"
    return rel, status, time.time() - t0, tail[:160]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--filter", default="")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()
    pkgs = find_packages(args.filter)
    if args.list:
        print("\n".join(pkgs))
        return 0
    print(f"{len(pkgs)} package directories with tests")
    results = []
    with cf.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        for res in ex.map(lambda r: run_one(r, args.timeout), pkgs):
            results.append(res)
            rel, status, dt, tail = res
            print(f"{status:8s} {dt:7.1f}s  {rel}  :: {tail}")
    failed = [r for r in results if r[1] in ("FAIL", "TIMEOUT")]
    print()
    print(f"summary: {len(results)} packages, {sum(1 for r in results if r[1] == 'pass')} pass, {len(failed)} fail/timeout, "
          f"{sum(1 for r in results if r[1] == 'no-tests')} with no collected tests")
    for rel, status, dt, tail in failed:
        print(f"  {status}: {rel} :: {tail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
