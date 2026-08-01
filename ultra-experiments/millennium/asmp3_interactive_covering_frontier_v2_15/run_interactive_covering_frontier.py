from __future__ import annotations

from interactive_covering_frontier import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.15 failed gates: {failed}")
    print(
        "ASMP-3 interactive covering certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])}"
    )


if __name__ == "__main__":
    main()
