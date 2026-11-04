from __future__ import annotations

from normative_closure_impossibility import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.18 failed gates: {failed}")
    print(
        "ASMP-3 normative-closure impossibility certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])}"
    )


if __name__ == "__main__":
    main()
