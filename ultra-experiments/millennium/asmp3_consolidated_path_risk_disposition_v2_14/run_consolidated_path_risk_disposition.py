from __future__ import annotations

from consolidated_path_risk_disposition import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.14 failed gates: {failed}")
    print(
        "ASMP-3 v2.14 consolidated disposition certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])}"
    )


if __name__ == "__main__":
    main()
