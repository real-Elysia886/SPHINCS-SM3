# Evidence Pack

This directory stores real command outputs captured from the repository. These files are intended to support screenshots, slides, and live-demo fallback during competition review.

Refresh the local evidence files with:

```bash
python tools/capture_evidence.py
```

## Files

| File | Purpose |
| --- | --- |
| `ci-status.txt` | Latest GitHub Actions CI status captured with `gh run list --workflow CI --limit 3`. |
| `consistency.txt` | Static parameter-header consistency check. |
| `parameter-search.txt` | Parameter search and Pareto candidate output. |
| `smoke-test.txt` | SM3 known-answer tests plus sign/verify/tamper-rejection smoke tests. |
| `performance-check.txt` | API-level benchmark compile/run check. |

## Suggested Screenshots

Use real screenshots from these outputs rather than generated terminal images:

1. CI status: show the latest `completed success` CI run.
2. Parameter consistency: show all three implemented parameter headers passing, including 76 tree bits and a 12-byte tree field.
3. Smoke test: show `verification succeeded` and `flipping a bit of m invalidates signature`.
4. Parameter search: show the original 64-bit boundary and the isolated `sphincs-sm3-224f-h80` wide-address prototype.
5. Performance check: show the comparison table for signature size and timing trend.

## Notes

Timings in `performance-check.txt` are environment-dependent. Use them as same-machine comparison evidence, not as universal performance claims.
