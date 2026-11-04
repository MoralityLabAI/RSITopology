from __future__ import annotations

from oracle_parametric_replay import write_artifact


def main() -> None:
    artifact = write_artifact()
    gates = artifact["gates"]
    passed = sum(bool(value) for value in gates.values())
    if passed != len(gates):
        failed = [name for name, value in gates.items() if not value]
        raise RuntimeError(f"ASMP-3 v2.9 failed gates: {failed}")
    print(f"ASMP-3 oracle-parametric replay certified: {passed}/{len(gates)} gates")


if __name__ == "__main__":
    main()
