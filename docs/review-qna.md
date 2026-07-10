# Review Q&A

This file collects likely competition-review questions and concise answers.

## 1. Why choose 224 bits?

224 bits is a middle point between visible signature-size reduction and preserving a high hash-object bit length. It reduces SPHINCS+ object size from 32 bytes to 28 bytes, which directly reduces WOTS+, FORS, and authentication-path contributions. It is also motivated by public discussion around Category Five SPHINCS+ multi-target second-preimage costs, but this project treats that only as a reference point, not as a complete proof for SM3.

## 2. Did the project modify SM3?

No. SM3 compression, padding, and full 256-bit digest computation are kept unchanged. The project truncates only the SPHINCS+ internal object representation to 28 bytes.

## 3. Does truncation weaken security?

Yes, truncation lowers the upper bound of a single hash object from 256 bits to 224 bits. That is why the repository clearly marks the result as an experimental parameter optimization and includes a conservative `sphincs-sm3-224f-dn` variant.

## 4. Why provide three implemented parameter sets?

`sphincs-sm3-224f` keeps the original 256f tree shape and gives the largest implemented size reduction: `20.14%`.

`sphincs-sm3-224f-dn` keeps `d*n = 560`, which is above the 256f baseline proxy `544`, and still reduces size by `10.65%`. It is the more conservative engineering choice.

`sphincs-sm3-224f-h80` keeps `d*n = 560` and restores `h/d = 4`. It is the engineering prototype used to validate 76-bit subtree indexing.

## 5. What does `d*n` mean in this project?

It is used as a structural proxy combining the number of hypertree layers `d` and the hash-object size `n`. It is not a full security proof, but it is useful for comparing how much hash-object material is distributed across layers.

## 6. How is `h=80,d=20` implemented despite the 64-bit limit?

The original reference path stores subtree indices in 64 bits. For `h=80,d=20`, the required subtree bits are:

```text
(h / d) * (d - 1) = 4 * 19 = 76
```

The `sphincs-sm3-224f-h80` prototype uses a portable high/low 64-bit index and a separate 12-byte tree field. It leaves the original parameter encodings unchanged. This proves functional feasibility, not cryptographic security or standards compatibility.

## 7. What is the main innovation?

The project combines three pieces:

- SM3 backend integration for SPHINCS+,
- 224-bit internal object representation to reduce signature size,
- reproducible parameter search and engineering-constraint checks,
- an isolated wide-address prototype that makes the 76-bit candidate executable.

The strongest claim is not “a new standard,” but “a reproducible SPHINCS+-SM3 parameter-optimization experiment.”

## 8. Are the performance numbers universal?

No. Performance numbers depend on CPU, compiler, optimization flags, and operating system. The project provides scripts so reviewers can reproduce same-machine comparisons.

## 9. What proves correctness?

Correctness is covered by:

- SM3 known-answer tests,
- key generation,
- signing,
- verification,
- in-place verification,
- tamper-rejection tests,
- GitHub Actions CI.

These prove implementation behavior, not cryptographic security.

## 10. Can it be deployed directly?

No. It should not be deployed as a production signature scheme without a dedicated SM3-oriented security proof, more review, and standardization work.

## 11. How should the project be positioned in the competition?

Position it as:

> An experimental SPHINCS+-SM3 signature-length optimization that preserves standard SM3 computation, implements three reproducible parameter sets including a wide-address prototype, and exposes the engineering/security trade-offs with automated tests.

## 12. What is the next technical milestone?

Review the extended compressed-address encoding for injectivity and proof compatibility, then compare robust and simple tweakable-hash variants across the three implemented schemes.

## 13. Is this project FIPS 205 compliant?

No. FIPS 205 standardizes SLH-DSA, which is derived from SPHINCS+. This project follows the SPHINCS+/SLH-DSA structural family, but it uses SM3 and experimental 224-bit parameter sets. The right wording is "FIPS 205-inspired structural mapping," not "FIPS-approved implementation."

## 14. How is the multi-target security margin estimated?

The current document uses a screening model:

```text
log2(W_generic) ~= n - log2(q) - log2(tau)
```

where `n = 224`, `q` is the number of observed signatures, and `tau` is a coarse per-signature target-count proxy. This is not a formal proof; it is a transparent way to explain why 224-bit truncation must be treated carefully under many-target settings.
