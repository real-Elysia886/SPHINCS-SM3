# FIPS 205 / SLH-DSA Mapping Notes

This document maps the SPHINCS+-SM3 experiment in this repository to the structure of NIST FIPS 205, the Stateless Hash-Based Digital Signature Standard. It is a comparison document, not a compliance claim.

## Source Standard

NIST FIPS 205 was published and became effective on August 13, 2024. It specifies the Stateless Hash-Based Digital Signature Algorithm, SLH-DSA. NIST states that SLH-DSA is derived from the SPHINCS+ submission, with several modifications relative to the NIST submission version.

Relevant public sources:

- FIPS 205 final page: <https://csrc.nist.gov/pubs/fips/205/final>
- NIST PQC standards announcement: <https://www.nist.gov/news-events/news/2024/08/announcing-approval-three-federal-information-processing-standards-fips>
- SPHINCS+ project page: <https://sphincs.org/>

## Position of This Repository

This project is best described as:

> An experimental SPHINCS+-style SM3 instantiation and parameter-optimization study that preserves the standard SM3 computation and truncates only the internal SPHINCS+ object representation to 224 bits.

It is not:

- a FIPS 205 approved parameter set,
- a FIPS-validated implementation,
- a drop-in SLH-DSA replacement,
- a deployment-ready signature standard.

## Structural Mapping

| FIPS 205 / SLH-DSA concept | Repository component | Mapping status |
| --- | --- | --- |
| Stateless hash-based signature | `ref/sign.c`, `ref/api.h` | Same high-level family |
| Hypertree | `ref/merkle.c`, `SPX_FULL_HEIGHT`, `SPX_D` | Same structural concept |
| WOTS+ | `ref/wots.c`, `ref/wotsx1.c` | Same component family |
| FORS | `ref/fors.c` | Same component family |
| Tweakable hash calls | `ref/thash_sm3_simple.c`, `ref/thash_sm3_robust.c` | SM3-specific experimental backend |
| Approved hash families | SHA2 / SHAKE in FIPS 205 | This project uses SM3, so it is outside FIPS 205 approval |
| Approved parameter sets | SLH-DSA parameter sets | This project defines experimental `sphincs-sm3-224f` and `sphincs-sm3-224f-dn` |
| Object length `n` | `SPX_N = 28` | Experimental 224-bit internal representation |
| Address representation | `ref/address.c`, `ref/sm3_offsets.h` | Reference-style address layout with current 64-bit subtree-index limit |
| Reproducibility tests | `.github/workflows/ci.yml`, `tools/*` | Project-specific engineering validation |

## What Is Preserved

The experiment intentionally preserves the following design properties from the SPHINCS+/SLH-DSA lineage:

- stateless signing,
- FORS + WOTS+ + hypertree structure,
- per-parameter deterministic size formulas,
- explicit address/domain separation machinery,
- robust and simple tree-hash implementation slots,
- public-key and secret-key layout style inherited from the reference implementation.

## What Is Changed

| Change | Reason | Consequence |
| --- | --- | --- |
| Use SM3 backend | Explore national-cryptography adaptation | Not FIPS 205 approved |
| Set `n = 28` bytes | Reduce signature size | Lowers single-object hash security margin |
| Add `sphincs-sm3-224f` | Maximize implemented size reduction | `d*n` below 256f baseline proxy |
| Add `sphincs-sm3-224f-dn` | Preserve `d*n >= 544` under 64-bit address constraint | Smaller size reduction but more conservative |
| Keep `h=80,d=20` as candidate | Shows parameter-search direction | Needs address extension because it requires 76 subtree bits |

## Parameter Comparison

| Parameter set | Hash family | n | h | d | h/d | d*n | Signature bytes | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `sphincs-sha2-256f` baseline | SHA-256 | 32 | 68 | 17 | 4 | 544 | 49856 | Reference comparison |
| `sphincs-sm3-224f` | SM3 | 28 | 68 | 17 | 4 | 476 | 39816 | Implemented experiment |
| `sphincs-sm3-224f-dn` | SM3 | 28 | 60 | 20 | 3 | 560 | 44548 | Implemented conservative experiment |
| `h=80,d=20` candidate | SM3 | 28 | 80 | 20 | 4 | 560 | 45108 | Requires address extension |

## FIPS Compatibility Boundary

The phrase "FIPS 205 mapping" should be used carefully:

- Correct: "The project maps its components to the SLH-DSA/SPHINCS+ structure defined by FIPS 205."
- Correct: "The project identifies which parts are inherited from SPHINCS+ and which parts are experimental."
- Incorrect: "The SM3 parameter sets are FIPS 205 compliant."
- Incorrect: "The project implements an approved SLH-DSA-SM3 scheme."

## Recommended Competition Claim

Use this wording in slides and reports:

> FIPS 205 standardizes SLH-DSA, a stateless hash-based signature algorithm derived from SPHINCS+. Our work follows the same high-level SPHINCS+ construction style, but replaces the hash backend with SM3 and explores 224-bit internal object representations as an experimental signature-size optimization. Therefore, the project is a FIPS 205-inspired engineering study, not a FIPS-approved algorithm.

## Review Checklist

Before claiming progress against FIPS 205, check:

- Does the statement distinguish SLH-DSA from this SM3 experiment?
- Does it avoid implying that SM3 is an approved FIPS 205 hash family?
- Does it state that the parameter sets are experimental?
- Does it point to correctness tests separately from cryptographic proof?
- Does it mention that a dedicated SM3 security analysis is still needed?

## Next Work

1. Compare the repository function names against the FIPS 205 algorithm boxes.
2. Add a line-by-line mapping for address fields and domain-separation constants.
3. Separate "FIPS-inspired structure" from "SM3 experimental backend" in the final report.
4. If standardization language is needed, draft it as a future-work appendix rather than as a current compliance claim.
