from __future__ import annotations

from correlated_path_risk import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.13 failed gates: {failed}")
    print(
        "ASMP-3 correlated path-risk certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])} gates"
    )


if __name__ == "__main__":
    main()
