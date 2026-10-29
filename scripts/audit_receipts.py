"""Audit every sealed SHA-256 file binding in the repository's JSON receipts.

A *binding* is a hash field that names a file in one of three shapes:
  (A) {"<path>": "<sha256>"}                      the key is the path
  (B) {"x": "<path>", "x_sha256": "<sha256>"}      paired keys (also x_path / x_file)
  (C) {"path"|"file"|"filename"|"source"|"name": "<path>", "sha256"|"hash"|"digest": "<sha256>"}

For each binding whose file exists, the file is hashed three ways: raw bytes,
LF-normalised bytes, and CRLF-normalised bytes.  Outcomes:
  match_raw        the sealed hash equals the file as checked out
  match_lf_only    equals the LF form only (working copy has CRLF)
  match_crlf_only  equals the CRLF form only: sealed on a CRLF working copy although
                   .gitattributes mandates LF, so every compliant checkout fails
  mismatch         equals none of the three: the file changed after sealing
  missing          the named file does not exist (tried relative to the receipt's
                   directory, the repository root, and ultra-experiments/millennium)
  self_reference   the binding names the receipt file itself

Content hashes that do not name a file (prompt_sha256, row_sha256, ...) are
not bindings and are not audited.  Writes a markdown report and a JSON table.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")
_PATHLIKE = re.compile(r"(/|\\|\.(py|md|json|jsonl|csv|txt|npz|npy|yaml|yml|toml|sh|ps1|cfg|ini|html|js|pdf|zip|tar\.gz|ots))$|/|\\", re.I)


class _PathLike:
    """A string is path-like if it has no whitespace, is short, and either contains a
    separator or ends with a known extension.  Prompt texts and sentences are excluded."""

    @staticmethod
    def search(s: str):
        if not isinstance(s, str) or len(s) > 300 or re.search(r"\s", s):
            return None
        return _PATHLIKE.search(s)


PATHLIKE = _PathLike()
ABS_RE = re.compile(r"^([A-Za-z]:[\\/]|/|\\\\)")
PATH_SIBLINGS = ("path", "file", "filename", "relative_path", "source", "name", "source_path", "file_path")
HASH_KEYS = ("sha256", "hash", "digest", "sha256_hex")
SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def walk_json(obj, found: list, ctx: dict):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and HEX64.match(v):
                path = None
                shape = None
                if isinstance(k, str) and PATHLIKE.search(k) and not k.endswith("_sha256"):
                    path, shape = k, "A"
                elif isinstance(k, str) and k.lower().endswith(("_sha256", "_hash", "_digest")):
                    base = re.sub(r"_(sha256|hash|digest)$", "", k, flags=re.I)
                    for cand in (base, base + "_path", base + "_file", base + "_relative_path"):
                        if isinstance(obj.get(cand), str) and PATHLIKE.search(obj[cand]):
                            path, shape = obj[cand], "B"
                            break
                elif isinstance(k, str) and k.lower() in HASH_KEYS:
                    for s in PATH_SIBLINGS:
                        if isinstance(obj.get(s), str) and PATHLIKE.search(obj[s]):
                            path, shape = obj[s], "C"
                            break
                if path is not None:
                    found.append({"key": k, "path": path, "sha256": v.lower(), "shape": shape})
            else:
                walk_json(v, found, ctx)
    elif isinstance(obj, list):
        for v in obj:
            walk_json(v, found, ctx)


def resolve(path: str, json_dir: str, root: str, index: dict[str, list[str]]) -> tuple[str | None, str]:
    """Return (resolved absolute path or None, note).  Tries the receipt's directory, each
    ancestor up to the repository root, the two experiment roots, and finally, for a bare
    filename, the repository-wide basename index (unique hit, or a hit under the receipt's
    top-level package directory).  Absolute paths outside the repository are reported as
    external."""
    p = path.replace("\\", "/")
    if ABS_RE.match(p):
        return (p if os.path.isfile(p) else None), "absolute"
    bases = []
    d = os.path.abspath(json_dir)
    while True:
        bases.append(d)
        if os.path.normcase(d) == os.path.normcase(root) or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    bases += [root, os.path.join(root, "ultra-experiments", "millennium"), os.path.join(root, "ultra-experiments")]
    for base in bases:
        cand = os.path.normpath(os.path.join(base, p))
        if os.path.isfile(cand):
            return cand, "relative"
    if "/" not in p:
        hits = index.get(p, [])
        if len(hits) == 1:
            return hits[0], "basename_unique"
        if len(hits) > 1:
            rel_dir = os.path.relpath(json_dir, root).replace(os.sep, "/")
            top = "/".join(rel_dir.split("/")[:3])
            under = [h for h in hits if os.path.relpath(h, root).replace(os.sep, "/").startswith(top)]
            if len(under) == 1:
                return under[0], "basename_in_package"
            return None, "ambiguous"
    return None, "unresolved"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--out-md", default="")
    ap.add_argument("--out-json", default="")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    rows = []
    n_json = 0
    cache: dict[str, tuple[str, str, str]] = {}
    index: dict[str, list[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            index.setdefault(f, []).append(os.path.join(dirpath, f))
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for f in filenames:
            if not f.lower().endswith(".json"):
                continue
            jp = os.path.join(dirpath, f)
            try:
                with open(jp, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except Exception:
                continue
            n_json += 1
            found: list = []
            walk_json(data, found, {})
            rel_json = os.path.relpath(jp, root).replace(os.sep, "/")
            for b in found:
                target, note = resolve(b["path"], dirpath, root, index)
                row = {"receipt": rel_json, "key": b["key"], "path": b["path"], "shape": b["shape"], "sealed": b["sha256"], "resolution": note}
                if target is None:
                    row["status"] = "external_absolute" if note == "absolute" else ("ambiguous_name" if note == "ambiguous" else "missing")
                elif os.path.normcase(os.path.abspath(target)) == os.path.normcase(os.path.abspath(jp)):
                    row["status"] = "self_reference"
                else:
                    if target not in cache:
                        with open(target, "rb") as fh:
                            raw = fh.read()
                        lf = raw.replace(b"\r\n", b"\n")
                        crlf = lf.replace(b"\n", b"\r\n")
                        cache[target] = (sha(raw), sha(lf), sha(crlf))
                    h_raw, h_lf, h_crlf = cache[target]
                    s = b["sha256"]
                    if s == h_raw:
                        row["status"] = "match_raw"
                    elif s == h_lf:
                        row["status"] = "match_lf_only"
                    elif s == h_crlf:
                        row["status"] = "match_crlf_only"
                    else:
                        row["status"] = "mismatch"
                    row["file"] = os.path.relpath(target, root).replace(os.sep, "/")
                rows.append(row)
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    # distinct (file, status) for the problem categories
    def distinct(status: str) -> list[tuple[str, str]]:
        seen = set()
        out = []
        for r in rows:
            if r["status"] == status:
                k = (r.get("file", r["path"]), r["receipt"])
                if k not in seen:
                    seen.add(k)
                    out.append(k)
        return out

    lines = [f"# Receipt audit — {os.path.basename(root)}", "",
             f"Generated by `scripts/audit_receipts.py`. JSON files scanned: {n_json}; file bindings found: {len(rows)}.",
             "", "| status | bindings |", "|---|---:|"]
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"| `{k}` | {v} |")
    lines.append("")
    for status, title in (("match_crlf_only", "Sealed on a CRLF working copy (fails on every LF checkout)"),
                          ("mismatch", "File changed after sealing"),
                          ("match_lf_only", "Working copy has CRLF but the seal is LF"),
                          ("missing", "Named file not found in the repository"),
                          ("ambiguous_name", "Bare filename matching several repository files"),
                          ("external_absolute", "Absolute path outside the repository (unverifiable here)"),
                          ("self_reference", "Receipt hashes itself")):
        items = distinct(status)
        lines.append(f"## {title} — {len(items)} distinct file/receipt pairs")
        lines.append("")
        for f, rcpt in items[:400]:
            lines.append(f"- `{f}` sealed in `{rcpt}`")
        if len(items) > 400:
            lines.append(f"- … {len(items) - 400} more in the JSON table")
        lines.append("")
    out_md = args.out_md or os.path.join(root, "reports", "receipt_audit.md")
    out_json = args.out_json or os.path.join(root, "reports", "receipt_audit.json")
    with open(out_md, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"json_files": n_json, "counts": counts, "rows": rows}, fh, indent=1, sort_keys=True)
    print(f"json files {n_json}; bindings {len(rows)}; counts {counts}")
    print("wrote", out_md, "and", out_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
