from __future__ import annotations

from uniform_membership_undecidability import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, passed in artifact["gates"].items() if not passed]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.20 producer failed: {failed}")
    print(f"ASMP-3 uniform-membership undecidability passed: {len(artifact['gates'])}/{len(artifact['gates'])}")


if __name__ == "__main__":
    main()
