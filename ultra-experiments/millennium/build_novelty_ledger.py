"""Build NOVELTY_LEDGER_<date>.md: one page listing, for every ASMP package, its
headline result status, its prior-art disposition, its frozen novelty sentence
and its conservative external description (the two sentences the repository's
own prior-art standard requires), plus every sentence in the package corpus that
asserts or hedges novelty rather than disclaiming it.  Mechanical extraction
with stated rules; no judgment is added.

Usage:  python build_novelty_ledger.py [--root ultra-experiments/millennium] [--out NOVELTY_LEDGER_YYYYMMDD.md]
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys

RESULT_NAMES = re.compile(r"^(RESULT|PUBLIC_SUMMARY|DEVELOPMENT_RESULT|RESOLUTION_DISPOSITION|REASSESSMENT_AND_CORRECTION)[A-Za-z0-9_.-]*\.md$", re.I)
PRIOR_NAMES = re.compile(r"PRIOR_ART", re.I)
SCAN_NAMES = re.compile(r"^(RESULT|PUBLIC_SUMMARY|DEVELOPMENT_RESULT|THEOREM|NOTE|.*PRIOR_ART.*)[A-Za-z0-9_.-]*\.md$", re.I)
TOKENS = ["candidate_new", "partial_extension", "subsumed", "classical", "ill_posed", "distinct", "subproblem"]
TOKEN_RE = re.compile(r"`(" + "|".join(TOKENS) + r")`")
JSON_DISP_RE = re.compile(r'"(prior_art_disposition|disposition)"\s*:\s*"([^"]*)"')
STATUS_TOKEN_RE = re.compile(r"`([a-z][a-z0-9_]{11,})`")
NOVELTY_HEAD = re.compile(r"novelty sentence|proposed novelty|novelty claim|novelty posture|novelty and claim", re.I)
EXTDESC_HEAD = re.compile(r"external description|external-description", re.I)
CONTRIB_HEAD = re.compile(r"contribution|residual|surviving|durable|deliverable", re.I)
VERDICT_HEAD = re.compile(r"^(verdict|decision|disposition|outcome|status|final disposition|registered verdict|conclusion|audit conclusion)\b", re.I)
NEGATION = re.compile(r"\b(not|no|neither|nor|never|without|unestablished|reject\w*|forbid\w*|disclaim\w*|cannot|insufficient|absent|withdrawn)\b", re.I)
ASMP_RE = re.compile(r"^(asmp\d+[a-z]?)", re.I)


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def asmp_key(rel: str) -> tuple[int, str, str]:
    m = ASMP_RE.match(rel)
    if not m:
        return (99, "", rel)
    tag = m.group(1).lower()
    return (int(re.sub(r"[^0-9]", "", tag)), tag, rel)


def strip_md(s: str) -> str:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = s.replace("**", "").replace("__", "")
    s = re.sub(r"(?<!\w)\*(?!\s)", "", s)
    s = s.replace("`", "")
    return s


def sections(text: str) -> list[tuple[str, list[str]]]:
    """Split markdown into (heading, body lines); the preamble has heading ''."""
    out: list[tuple[str, list[str]]] = [("", [])]
    for line in text.splitlines():
        if line.startswith("#"):
            out.append((line.lstrip("#").strip(), []))
        else:
            out[-1][1].append(line)
    return out


LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def paragraphs(body: list[str]) -> list[str]:
    """Paragraphs of a section; list items are separate units."""
    paras: list[str] = []
    cur: list[str] = []

    def flush() -> None:
        nonlocal cur
        if cur:
            paras.append(" ".join(x.strip().lstrip("> ").strip() for x in cur))
            cur = []

    for line in body:
        s = line.strip()
        if s == "" or s.startswith("|") or s.startswith("```"):
            flush()
            continue
        if LIST_ITEM.match(line):
            flush()
            cur.append("• " + LIST_ITEM.sub("", line))   # marker: list item
            flush()
            continue
        cur.append(line)
    flush()
    return [re.sub(r"\s+", " ", p).strip() for p in paras if p.strip()]


def first_para(body: list[str], prefer_quote: bool = True) -> str:
    if prefer_quote:
        q = [l.strip()[1:].strip() for l in body if l.strip().startswith(">")]
        if q:
            return re.sub(r"\s+", " ", " ".join(q))
    ps = [p[2:] if p.startswith("• ") else p for p in paragraphs(body)]
    return ps[0] if ps else ""


def sentences(par: str) -> list[str]:
    par = strip_md(par)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z(\"'])", par) if s.strip()]


def novelty_sentences(text: str) -> list[tuple[str, str]]:
    """Sentences mentioning novelty, classified. A negation in the section heading,
    or in a lead-in paragraph ending with a colon, carries into the units below it."""
    out = []
    for heading, body in sections(text):
        head_neg = bool(NEGATION.search(strip_md(heading)))
        lead_neg = False
        for p in paragraphs(body):
            is_item = p.startswith("• ")
            p_text = p[2:] if is_item else p
            p_neg = bool(NEGATION.search(strip_md(p_text)))
            for s in sentences(p_text):
                if re.search(r"novel|candidate[-_ ]new", s, re.I):
                    negated = NEGATION.search(s) or head_neg or lead_neg
                    kind = "disclaims" if negated else "asserts_or_hedges"
                    out.append((kind, s[:400]))
            if not is_item:
                lead_neg = p_neg if p_text.rstrip().endswith(":") else False
    return out


def prior_art_fields(text: str) -> dict[str, str]:
    f = {"tokens": "", "verdict": "", "novelty_sentence": "", "external": "", "contribution": ""}
    toks = sorted(set(TOKEN_RE.findall(text)))
    f["tokens"] = ", ".join("`" + t + "`" for t in toks)
    for heading, body in sections(text):
        h = heading.strip()
        if not f["novelty_sentence"] and NOVELTY_HEAD.search(h):
            f["novelty_sentence"] = strip_md(first_para(body))[:400]
        elif not f["external"] and EXTDESC_HEAD.search(h):
            f["external"] = strip_md(first_para(body))[:400]
        elif not f["verdict"] and VERDICT_HEAD.search(h):
            f["verdict"] = strip_md(first_para(body, prefer_quote=False))[:300]
        elif not f["contribution"] and CONTRIB_HEAD.search(h):
            f["contribution"] = strip_md(first_para(body, prefer_quote=False))[:300]
    return f


def headline_status(text: str) -> str:
    head = "\n".join(text.splitlines()[:25])
    for m in STATUS_TOKEN_RE.finditer(head):
        tok = m.group(1)
        if "_" in tok and not re.fullmatch(r"[0-9a-f]+", tok) and not tok.startswith(("sha", "artifacts", "protocol", "registration")):
            return "`" + tok + "`"
    for heading, body in sections(text):
        if VERDICT_HEAD.search(heading.strip()):
            p = first_para(body, prefer_quote=False)
            if p:
                return strip_md(p)[:220]
    for heading, body in sections(text)[:3]:
        ps = paragraphs(body)
        if ps:
            return strip_md(ps[0])[:220]
    return ""


def cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    root = os.path.abspath(args.root)
    today = dt.date.today().strftime("%Y%m%d")
    out = args.out or os.path.join(root, f"NOVELTY_LEDGER_{today}.md")

    packages: dict[str, dict] = {}
    all_novelty: list[tuple[str, str, str]] = []
    token_hits: dict[tuple[str, str], int] = {}
    json_disp: list[tuple[str, str, str]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git")]
        rel_dir = os.path.relpath(dirpath, root).replace(os.sep, "/")
        results = sorted([f for f in filenames if RESULT_NAMES.match(f)])
        priors = sorted([f for f in filenames if PRIOR_NAMES.search(f) and f.lower().endswith(".md")])
        for f in filenames:
            rel = (rel_dir + "/" + f) if rel_dir != "." else f
            if SCAN_NAMES.match(f):
                text = read(os.path.join(dirpath, f))
                for kind, s in novelty_sentences(text):
                    all_novelty.append((rel, kind, s))
                for t in TOKEN_RE.findall(text):
                    token_hits[(rel, t)] = token_hits.get((rel, t), 0) + 1
            if f.lower().endswith(".json"):
                text = read(os.path.join(dirpath, f))
                for m in JSON_DISP_RE.finditer(text):
                    if len(m.group(2)) < 220:
                        json_disp.append((rel, m.group(1), m.group(2)))
        if rel_dir == "." or (not results and not priors):
            continue
        rec = {"dir": rel_dir, "result_file": "", "status": "", "prior_file": "", "pa": None}
        if results:
            rec["result_file"] = results[-1]
            rec["status"] = headline_status(read(os.path.join(dirpath, results[-1])))
        if priors:
            rec["prior_file"] = priors[-1]
            rec["pa"] = prior_art_fields(read(os.path.join(dirpath, priors[-1])))
        packages[rel_dir] = rec

    for rel_dir, rec in packages.items():
        if rec["pa"] is not None:
            continue
        parts = rel_dir.split("/")
        for k in range(len(parts) - 1, 0, -1):
            parent = "/".join(parts[:k])
            if parent in packages and packages[parent]["pa"] is not None:
                rec["prior_file"] = parent + "/" + packages[parent]["prior_file"] + " (inherited)"
                rec["pa"] = packages[parent]["pa"]
                break

    ordered = sorted(packages.values(), key=lambda r: asmp_key(r["dir"]))
    n_disclaim = sum(1 for _, k, _ in all_novelty if k == "disclaims")
    n_assert = sum(1 for _, k, _ in all_novelty if k == "asserts_or_hedges")
    tok_counts: dict[str, int] = {}
    for (rel, t), c in token_hits.items():
        tok_counts[t] = tok_counts.get(t, 0) + c
    with_novelty = sum(1 for r in ordered if r["pa"] and r["pa"]["novelty_sentence"] and "(inherited)" not in r["prior_file"])
    with_ext = sum(1 for r in ordered if r["pa"] and r["pa"]["external"] and "(inherited)" not in r["prior_file"])
    with_prior = sum(1 for r in ordered if r["pa"] and "(inherited)" not in r["prior_file"])

    L: list[str] = []
    L.append(f"# ASMP novelty ledger — generated {dt.date.today().isoformat()}")
    L.append("")
    L.append("Generated by `build_novelty_ledger.py` from the package corpus. Mechanical")
    L.append("extraction with the rules below; no judgment is added. Purpose: let a reviewer")
    L.append("find every explicit novelty statement in the corpus without reading all of")
    L.append("it. Regenerate after any package change.")
    L.append("")
    L.append("## Rules")
    L.append("")
    L.append("- A *package* is any directory holding a `RESULT*`, `PUBLIC_SUMMARY*`,")
    L.append("  `DEVELOPMENT_RESULT*`, `RESOLUTION_DISPOSITION*`, `REASSESSMENT*` or")
    L.append("  `*PRIOR_ART*` markdown file. Versioned subpackages without their own")
    L.append("  prior-art file inherit the parent's (marked).")
    L.append("- *Status*: the first long backticked token in the first 25 lines of the")
    L.append("  package's latest result file, else the first paragraph under a verdict-like")
    L.append("  heading, else the first body paragraph.")
    L.append("- *Novelty sentence* / *external description*: the first blockquote or")
    L.append("  paragraph under a heading mentioning a novelty sentence / an external")
    L.append("  description in the latest prior-art file. These are the two sentences")
    L.append("  `PRIOR_ART_BEFORE_FREEZE_STANDARD_v0_1.md` requires.")
    L.append("- *Verdict*: first paragraph under a verdict/decision/disposition heading of")
    L.append("  the prior-art file; *tokens*: backticked disposition tokens found there.")
    L.append("- *Novelty mentions*: every sentence containing \"novel\" or \"candidate-new\" in")
    L.append("  result, prior-art, theorem and note files, with markdown emphasis removed")
    L.append("  and headings kept apart. A sentence `disclaims` if it contains a negation")
    L.append("  word (not, no, neither, never, without, unestablished, reject, forbid,")
    L.append("  cannot, insufficient, absent, withdrawn); otherwise it `asserts_or_hedges`.")
    L.append("  Only the second kind is listed; the rule errs toward listing.")
    L.append("")
    L.append("## Summary")
    L.append("")
    L.append(f"- packages: {len(ordered)}; with their own prior-art file: {with_prior}; of those with an")
    L.append(f"  explicit novelty sentence: {with_novelty}; with an explicit external description: {with_ext}")
    L.append("- backticked disposition tokens in markdown: " + ", ".join(f"`{t}` ×{c}" for t, c in sorted(tok_counts.items(), key=lambda x: -x[1])))
    L.append(f"- JSON disposition fields: {len(json_disp)}")
    L.append(f"- sentences mentioning novelty: {len(all_novelty)} ({n_disclaim} disclaim, {n_assert} assert or hedge)")
    L.append("")
    L.append("## Explicit novelty sentences (the standard's required sentence)")
    L.append("")
    for r in ordered:
        if r["pa"] and r["pa"]["novelty_sentence"] and "(inherited)" not in r["prior_file"]:
            L.append(f"- [{r['dir']}]({r['dir']}/{r['prior_file']}): {r['pa']['novelty_sentence']}")
    L.append("")
    L.append("## Explicit conservative external descriptions")
    L.append("")
    for r in ordered:
        if r["pa"] and r["pa"]["external"] and "(inherited)" not in r["prior_file"]:
            L.append(f"- [{r['dir']}]({r['dir']}/{r['prior_file']}): {r['pa']['external']}")
    L.append("")
    L.append("## Sentences that assert or hedge novelty (review these)")
    L.append("")
    cur = None
    for rel, kind, s in sorted(all_novelty, key=lambda x: (asmp_key(x[0]), x[0])):
        if kind != "asserts_or_hedges":
            continue
        tag = asmp_key(rel)[1] or "top-level"
        if tag != cur:
            L.append(f"### {tag}")
            L.append("")
            cur = tag
        L.append(f"- [{rel}]({rel}): {s}")
    L.append("")
    L.append("## Explicit disposition tokens")
    L.append("")
    for (rel, t), c in sorted(token_hits.items()):
        L.append(f"- `{t}`" + (f" ×{c}" if c > 1 else "") + f" — [{rel}]({rel})")
    L.append("")
    L.append("## JSON disposition fields")
    L.append("")
    for rel, key, val in sorted(json_disp):
        L.append(f"- [{rel}]({rel}) `{key}`: {val}")
    L.append("")
    L.append("## Package table")
    L.append("")
    cur = None
    for r in ordered:
        tag = asmp_key(r["dir"])[1]
        if tag != cur:
            L.append(f"### {tag}")
            L.append("")
            L.append("| package | status | prior-art verdict / tokens | contribution as stated |")
            L.append("|---|---|---|---|")
            cur = tag
        pa = r["pa"] or {"tokens": "", "verdict": "", "contribution": ""}
        verdict = (pa["tokens"] + (" " if pa["tokens"] and pa["verdict"] else "") + pa["verdict"]) or ("(prior-art file without a verdict heading)" if r["pa"] else "(no prior-art file)")
        if r["pa"] and "(inherited)" in r["prior_file"]:
            verdict += " [inherited]"
        L.append(f"| [{r['dir']}]({r['dir']}) | {cell(r['status'])} | {cell(verdict)} | {cell(pa['contribution'])} |")
    L.append("")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print(f"packages={len(ordered)} own_prior_art={with_prior} novelty_sentences={with_novelty} external_descriptions={with_ext}")
    print(f"novelty mentions={len(all_novelty)} (disclaim={n_disclaim}, assert/hedge={n_assert}) tokens={tok_counts} json_fields={len(json_disp)}")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
