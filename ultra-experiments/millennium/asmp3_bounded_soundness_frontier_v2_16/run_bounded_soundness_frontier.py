from __future__ import annotations

from bounded_soundness_frontier import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.16 failed gates: {failed}")
    print(
        "ASMP-3 bounded-soundness frontier certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])}"
    )


if __name__ == "__main__":
    main()
