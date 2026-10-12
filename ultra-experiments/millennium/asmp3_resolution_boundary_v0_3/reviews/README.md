# Independent expert-review receipts

Place signed or otherwise attributable JSON review receipts in this directory.
Each receipt must satisfy `../expert_review.schema.json` and bind itself to the
SHA-256 of `../RELEASE_MANIFEST_v0_3.json`.

The manifest also binds the normative ASMP v0.1 Markdown statement and its
machine-readable problem registry. Both reviews must answer all twelve
end-to-end questions `yes`; a `no` or `unclear` answer is non-qualifying even if the
declared verdict says `accept`.

At least one qualifying team must also place an independently implemented
checker below `checkers/`, record its relative path and SHA-256 in the receipt,
and report a passing result. Re-running or wrapping the supplied checkers is not
an independent implementation.

Do not place model-generated self-reviews here. The canonical acceptance rule
requires genuinely independent expert teams.

Run:

```powershell
python ../verify_expert_reviews.py
```

Use `--require-complete` only when adjudicating the final resolution gate.
