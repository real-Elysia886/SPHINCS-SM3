# Multi-Target Security Notes for 224-bit Truncation

This document gives a competition-facing security model for the 224-bit truncation used in the SPHINCS+-SM3 experiment. It is a screening analysis, not a formal proof.

## Goal

The key question is:

> If SM3 still computes a full 256-bit digest, but SPHINCS+ internal objects retain only 224 bits, what security margin should be expected against generic multi-target second-preimage style attacks?

The short answer is:

- A single retained object has at most 224 bits of generic preimage/second-preimage margin.
- With many exposed targets, the generic work factor decreases by approximately `log2(T)` bits, where `T` is the number of exploitable targets.
- This project therefore treats 224-bit truncation as an experimental optimization and does not claim full Category Five standard-level security.

## Generic Multi-Target Model

Let:

| Symbol | Meaning |
| --- | --- |
| `n` | retained object length in bits |
| `q` | number of observed valid signatures |
| `tau` | approximate number of useful target hash objects exposed per signature |
| `T = q * tau` | total target count |
| `L = log2(T)` | target-count advantage in bits |
| `W_generic` | generic multi-target work estimate |

The simple screening estimate is:

```text
W_generic ~= 2^n / T
log2(W_generic) ~= n - log2(q) - log2(tau)
```

For this project:

```text
n = 224
```

This model is intentionally conservative and simple. It does not replace the SPHINCS+ proof framework, nor does it model SM3-specific structural properties.

## Target-Count Proxy

SPHINCS+ exposes several kinds of hash-derived objects across FORS, WOTS+, and hypertree authentication paths. A coarse per-signature target proxy is:

```text
tau_proxy = d * WOTS_LEN + FORS_TREES + FULL_HEIGHT
```

This is not a proof-tight target count. It is a transparent competition-screening proxy that helps explain why multi-target analysis is necessary.

| Scheme | d | WOTS_LEN | FORS trees | h | tau_proxy | log2(tau_proxy) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `sphincs-sm3-224f` | 17 | 59 | 35 | 68 | 1106 | 10.11 |
| `sphincs-sm3-224f-dn` | 20 | 59 | 35 | 60 | 1275 | 10.32 |
| `sphincs-sm3-224f-h80` | 20 | 59 | 35 | 80 | 1295 | 10.34 |

## Work-Factor Table

Using the generic screening formula:

```text
log2(W_generic) ~= 224 - log2(q) - log2(tau_proxy)
```

| Observed signatures `q` | `log2(q)` | `224f` estimate | `224f-dn` estimate | `224f-h80` estimate |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0 | 213.89 | 213.68 | 213.66 |
| 2^20 | 20 | 193.89 | 193.68 | 193.66 |
| 2^32 | 32 | 181.89 | 181.68 | 181.66 |
| 2^40 | 40 | 173.89 | 173.68 | 173.66 |
| 2^64 | 64 | 149.89 | 149.68 | 149.66 |

Interpretation:

- For a small number of signatures, the generic screening margin remains high.
- Under very large signature counts such as `2^64`, the generic target-count advantage becomes significant.
- This supports positioning the current project as an experimental optimization and motivates future limited-use or address-extended variants rather than immediate deployment.

## Relation to the SHA-256 Category-Five Discussion

The public "Breaking Category Five SPHINCS+ with SHA-256" work discusses the DM-SPR property and shows that certain SHA-256-based Category Five SPHINCS+ parameter sets lose about 40 bits of classical security in the discussed attack setting. NIST's summary of the work states that the relevant SPHINCS+ security proof relies on distinct-function multi-target second-preimage resistance of the keyed hash function.

This project uses that work as a warning signal:

- SPHINCS+-style schemes must treat multi-target second-preimage properties carefully.
- Merkle-Damgard hash constructions require attention to prefix/domain separation and target counts.
- A security argument for SHA-256 should not be copied directly to SM3.

The project does not claim that the same attack applies to SM3, and it does not claim that SM3 is immune. The correct next step is a dedicated SM3-oriented analysis.

## Why `sphincs-sm3-224f-dn` Exists

`sphincs-sm3-224f` gives the largest implemented size reduction, but its structural proxy decreases:

```text
17 * 32 = 544
17 * 28 = 476
```

`sphincs-sm3-224f-dn` compensates by increasing `d`:

```text
20 * 28 = 560
```

This does not prove security, but it gives a conservative engineering rationale for keeping more layer-distributed hash-object material while staying within the 64-bit address constraint.

## Practical Claim Boundary

Safe claims:

- The 224-bit variants reduce signature size in a reproducible implementation.
- The project gives a transparent generic multi-target screening formula.
- The project separates aggressive and conservative parameter choices.
- The project identifies where a formal SM3 analysis is still missing.

Unsafe claims:

- "224-bit truncation is proven secure for SPHINCS+-SM3."
- "The project achieves FIPS 205 Category Five security."
- "Smoke tests prove cryptographic security."
- "The SHA-256 attack result directly proves or disproves SM3 security."

## Next Analysis Tasks

1. Replace `tau_proxy` with a proof-aligned target count for FORS, WOTS+, and hypertree nodes.
2. Analyze SM3's Merkle-Damgard structure under distinct-prefix multi-target second-preimage assumptions.
3. Compare robust and simple tweakable hash variants separately.
4. Define a limited-signature-use profile if the target application does not require `2^64` signatures.
5. Ask for external cryptographic review before making deployment claims.

## References

- NIST FIPS 205 final page: <https://csrc.nist.gov/pubs/fips/205/final>
- NIST summary of "Breaking Category Five SPHINCS+ with SHA-256": <https://www.nist.gov/publications/breaking-category-five-sphincs-sha-256>
- IACR ePrint 2022/1061: <https://eprint.iacr.org/2022/1061>
- SPHINCS+ project page: <https://sphincs.org/>
