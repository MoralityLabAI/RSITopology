from __future__ import annotations

from online_noisy_trace_extractor import write_artifact


def main() -> None:
    artifact = write_artifact()
    failed = [name for name, value in artifact["gates"].items() if not value]
    if failed:
        raise RuntimeError(f"ASMP-3 v2.10 failed gates: {failed}")
    print(
        "ASMP-3 online noisy-trace extractor certified: "
        f"{len(artifact['gates'])}/{len(artifact['gates'])} gates"
    )


if __name__ == "__main__":
    main()
