"""Compile the deterministic ASMP-5 v0.3 theorem artifact."""

from pathlib import Path

from inductive_root import canonical_json, compile_result, load_protocol


HERE = Path(__file__).resolve().parent


def main() -> None:
    protocol = load_protocol(HERE / "protocol_v0_3.json")
    output = HERE / "artifacts_v0_3" / "result_v0_3.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(canonical_json(compile_result(protocol)), encoding="utf-8", newline="\n")
    print(output)


if __name__ == "__main__":
    main()
