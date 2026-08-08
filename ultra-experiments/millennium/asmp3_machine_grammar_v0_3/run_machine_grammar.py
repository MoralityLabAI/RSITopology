from __future__ import annotations

from machine_grammar import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, passed in artifact["gates"].items() if not passed]
    if failed:
        raise RuntimeError(f"ASMP-3 machine grammar producer failed: {failed}")
    print(f"ASMP-3 machine grammar passed: {len(artifact['gates'])}/{len(artifact['gates'])}")


if __name__ == "__main__":
    main()
