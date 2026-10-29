from __future__ import annotations

from normative_closure_reassessment import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, passed in artifact["gates"].items() if not passed]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.19 reassessment failed: {failed}")
    print(f"ASMP-3 normative-closure reassessment passed: {len(artifact['gates'])}/{len(artifact['gates'])}")


if __name__ == "__main__":
    main()
