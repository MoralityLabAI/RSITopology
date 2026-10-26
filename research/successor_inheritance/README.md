# Successor artifact inheritance

This is an isolated, model-free FRC-Bench module for the *Towards
SuperAlignment Intractability Proofs* research program. It uses symbolic rows
and a deterministic last-write-wins learner. It neither trains models nor
connects to live training, intervention, or deployment systems.

- [Theorem and assumptions audit](theorem_audit.md)
- [Experiment report](experiment_report.md)
- [Proposed paper section](paper_section.md)
- [Pinned source and manuscript provenance](provenance.json)
- [Execution and test receipt](results/verification.json)
- [Original six source files](source_pr12/)

## Integration decision

The destination was inspected at `659b5b13d5c1609ba74ae8cb4c3546a86545b518`:
`README.md`, `pyproject.toml`, `rsi_topology/__init__.py`, the discovery,
attestation, Blue Beam and recursive-gate modules, their tests, and the
mathematical-program, bundle-lineage, monitor-holonomy, signed-control theorem,
and proposal-recursion reports. No FRC implementation or manuscript was present
in that tree. The two manuscripts were subsequently located in
`MoralityLabAI/morality-lab-site`; the inspected versions are the October 10,
2026 revisions, not the original August drafts.

The existing repository uses `rsi_topology/` for reusable logic, `scripts/`
for runners, `protocols/` for fixed matrices, and `tests/` for pytest tests.
Accordingly, `rsi_topology/successor_inheritance.py` is a separate module with
no imports from the spectral or live-model mechanisms. The package initializer
and all existing gates are unchanged. Python still loads the repository's
existing package initializer, so its declared numerical dependencies are needed
for normal package import even though the new experiment itself uses stdlib.

This research directory owns interpretation and the source archive. Archived
source prose is historical evidence, not the current claims ledger. In
particular, its reference to Theorem 2 is superseded by the revised paper's
Conjecture 1, and the unverified external risk-report discussion is not used
as evidence in this integration.

## Reproduce

From the repository root, in Python 3.11 or newer with the dependencies in
`pyproject.toml` and pytest installed:

```sh
python -m unittest discover -s tests -p test_successor_inheritance.py -v
python -m pytest tests/test_successor_semantic.py -q
python scripts/run_successor_inheritance.py
python scripts/run_successor_inheritance.py --semantic
python scripts/verify_successor_inheritance.py --out-dir artifacts/successor_replay
```

The first command runs the 13 ported original tests. The second runs 13 new
semantic, query-model, configuration and reproduction checks. The verification
command also runs the untouched source tests and source CLI from the six-file
archive, compares all 1,024 records, checks Git blob hashes, and creates a
machine-readable receipt with implementation/output hashes and environment
versions. Its output directory must be new. Runner outputs are LF-terminated
UTF-8 and compare-or-fail: a differing existing receipt is never overwritten.
Default outputs go to ignored `artifacts/successor_inheritance/`. The published
run is deliberately tracked in `research/successor_inheritance/results/`.

The runner reads the pinned protocol; command-line grids, counts and seed can
override it explicitly. V1 fixes history to 0--3 and generations to three;
changing those protocol fields fails rather than being silently ignored.
The optional semantic comparison observes the same artifacts and does not
change the random stream, probes, repairs or baseline summary.

For Windows sandbox runs, set `TEMP` and `TMP` to a writable workspace
directory before testing. The verified environment is in the receipt; BLAS
and OpenMP threads were limited to one for the regression suite.

The existing full suite requires an ignored external fixture. Its original
bytes are already in the committed release archive and can be restored with:

```sh
python -c "from pathlib import Path; from zipfile import ZipFile; p=Path('artifacts/external_fable_files7/holonomy_from_spec_repro.py'); b=ZipFile('RSITopology_monitor_holonomy_v0_3_20260712.zip').read(p.as_posix()); p.parent.mkdir(parents=True,exist_ok=True); assert not p.exists() or p.read_bytes()==b; p.write_bytes(b)"
python -m pytest -q
```

No existing test is skipped or altered. This restoration changes only ignored
local run material. It is a pre-existing clean-checkout prerequisite.
