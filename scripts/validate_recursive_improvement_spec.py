"""Extract and validate rendered recursive-improvement protocol formulas."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import sys
from importlib import metadata
from pathlib import Path
from typing import Any

from pypdf import PdfReader


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def package_version(name: str) -> str:
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return "not-installed"


def write_once_or_equal(path: Path, payload: Any) -> None:
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != encoded:
            raise FileExistsError(f"write-once artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)


def validate(
    *, source_path: Path, pdf_path: Path, schema_path: Path, artifact_dir: Path
) -> dict[str, Any]:
    source = source_path.read_text(encoding="utf-8")
    if not source.isascii():
        raise ValueError("source contains non-ASCII characters")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    reader = PdfReader(str(pdf_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    extracted = "\n\n".join(pages)
    normalized_source = normalize(source)
    normalized_pdf = normalize(extracted)
    source_checks = {
        item: normalize(item) in normalized_source
        for item in schema["required_ascii_source_substrings"]
    }
    pdf_checks = {
        item: normalize(item) in normalized_pdf
        for item in schema["required_pdf_text_substrings"]
    }
    formula_checks: dict[str, Any] = {}
    machine_artifact = json.loads(
        (source_path.parents[1] / "protocols" / "proposal_recursive_improvement_v1.json").read_text(
            encoding="utf-8"
        )
    )
    formulas = {
        "lambda_prompt": machine_artifact["atlas"]["prompt_scale_ascii"],
        "adversarial_suite_V": json.loads(
            (source_path.parents[1] / "protocols" / "proposal_recursive_ordering_generator_v1.json").read_text(
                encoding="utf-8"
            )
        )["suite_validity"]["ascii"],
    }
    for name, definition in schema["machine_formula_checks"].items():
        value = formulas[name]
        tokens = {token: token in value for token in definition["required_tokens"]}
        formula_checks[name] = {"formula": value, "tokens": tokens, "passed": all(tokens.values())}
    passed = bool(
        all(source_checks.values())
        and all(pdf_checks.values())
        and all(item["passed"] for item in formula_checks.values())
        and len(pages) >= 5
    )
    artifact_dir.mkdir(parents=True, exist_ok=True)
    extracted_path = artifact_dir / "proposal_recursive_improvement_v1.extracted.txt"
    extracted_path.write_text(extracted, encoding="utf-8")
    environment = {
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "packages": {
            "reportlab": package_version("reportlab"),
            "pypdf": package_version("pypdf"),
            "PyMuPDF": package_version("PyMuPDF"),
            "numpy": package_version("numpy"),
        },
    }
    environment_path = artifact_dir / "environment_lock.json"
    write_once_or_equal(environment_path, environment)
    receipt = {
        "schema_version": "proposal_recursive_render_validation_v1",
        "status": "passed" if passed else "failed",
        "page_count": len(pages),
        "source_ascii": source.isascii(),
        "source_checks": source_checks,
        "pdf_checks": pdf_checks,
        "machine_formula_checks": formula_checks,
        "sha256": {
            "source_markdown": sha256_file(source_path),
            "rendered_pdf": sha256_file(pdf_path),
            "extracted_text": sha256_file(extracted_path),
            "sentinel_schema": sha256_file(schema_path),
            "environment_lock": sha256_file(environment_path),
        },
    }
    receipt_path = artifact_dir / "render_validation_receipt.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if not passed:
        failures = [item for item, ok in source_checks.items() if not ok]
        failures += [item for item, ok in pdf_checks.items() if not ok]
        failures += [name for name, item in formula_checks.items() if not item["passed"]]
        raise ValueError(f"render validation failed: {failures}")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    receipt = validate(
        source_path=args.source.resolve(),
        pdf_path=args.pdf.resolve(),
        schema_path=args.schema.resolve(),
        artifact_dir=args.artifact_dir.resolve(),
    )
    print(json.dumps({"status": receipt["status"], "pages": receipt["page_count"]}))


if __name__ == "__main__":
    main()
