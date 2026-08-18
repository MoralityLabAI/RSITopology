from __future__ import annotations

from pathlib import Path

import resume_liveness_pilot_v0_4b as resume


def test_output_dir_parser_is_exact(tmp_path: Path) -> None:
    output = tmp_path / "artifacts"
    parsed = resume.output_dir_from_argv(["--config", "frozen.json", "--output-dir", str(output)])
    assert parsed == output.resolve()
