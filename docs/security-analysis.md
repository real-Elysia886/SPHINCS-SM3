# Security Analysis Notes

This document explains the security rationale and limitations of the experimental SPHINCS+-SM3 truncated-hash parameter sets in this repository. It is written for competition review and reproducibility; it is not a standardization claim.

## Scope

The project keeps the SM3 computation itself unchanged:

- SM3 compression, padding, and full 256-bit digest computation are not modified.
- The truncation happens at the SPHINCS+ object representation layer: the first 28 bytes are retained as `n = 224` bits.
- The implementation remains a SPHINCS+-style stateless hash-based signature experiment with an SM3 backend.

The main optimization target is signature length. Runtime and implementation compatibility are measured separately in [performance.md](performance.md).

## Security Baseline

The comparison baseline is `sphincs-sha2-256f` from the SPHINCS+ reference parameter family:

| Scheme | n | h | d | h/d | d*n | Signature bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `sphincs-sha2-256f` | 32 | 68 | 17 | 4 | 544 | 49856 |
| `sphincs-sm3-224f` | 28 | 68 | 17 | 4 | 476 | 39816 |
| `sphincs-sm3-224f-dn` | 28 | 60 | 20 | 3 | 560 | 44548 |

The two implemented SM3 variants serve different purposes:

- `sphincs-sm3-224f` maximizes implemented signature-size reduction.
- `sphincs-sm3-224f-dn` is a conservative engineering variant that keeps the `d*n` structural proxy above the 256f baseline while remaining compatible with the current address representation.

## Why 224 Bits

The choice of 224 bits is a deliberate engineering point rather than an arbitrary truncation:

- It reduces WOTS+ element length and Merkle authentication-path size because many SPHINCS+ signature terms scale linearly with `n`.
- It keeps a higher single-object bit length than 192-bit truncation while still producing a visible signature-size reduction.
- It is motivated by the known Category Five SHA-256 multi-target second-preimage discussion around the high 2^217 work-factor range.

This repository treats that discussion as a reference point, not as a proof for SM3. A dedicated SM3 analysis is still required before any deployment or standardization claim. See [multitarget-security.md](multitarget-security.md) for the current screening model and work-factor table.

## What Changes and What Does Not

| Aspect | Changed? | Notes |
| --- | --- | --- |
| SM3 compression function | No | The project does not define a new hash function. |
| SM3 padding and 256-bit computation | No | Full SM3 is computed before output representation is truncated. |
| SPHINCS+ object size `n` | Yes | Internal objects use 28 bytes instead of 32 bytes. |
| WOTS+ length | Yes | For `w = 16`, `WOTS_LEN` falls from 67 to 59. |
| Signature size | Yes | Implemented reductions are 20.14% and 10.65%. |
| Security proof status | Yes | The parameter sets are experimental and not FIPS-approved. |

## Security Properties to Revisit

SPHINCS+ security depends on several hash-related assumptions. For an SM3 instantiation with truncated object representation, the following properties need explicit review:

| Property | Why it matters here |
| --- | --- |
| Preimage resistance | Protects hash-chain and tree values from inversion. |
| Second-preimage resistance | Relevant when an attacker tries to replace signed hash objects. |
| Multi-target second-preimage resistance | Important because many targets are exposed across WOTS+, FORS, and hypertree locations. |
| Tweak/domain separation robustness | Prevents values from different SPHINCS+ roles from becoming interchangeable. |
| PRF behavior | Used in secret-key-derived pseudorandom material and message-dependent randomness. |

The existing implementation verifies functional correctness, but correctness tests do not replace cryptographic analysis.

## Parameter Trade-Offs

### `sphincs-sm3-224f`

This variant keeps the baseline tree shape `h = 68, d = 17`, so the address constraint remains exactly at the current 64-bit subtree-index limit:

```text
(h / d) * (d - 1) = 4 * 16 = 64
```

Its benefit is the largest implemented size reduction:

```text
49856 - 39816 = 10040 bytes = 20.14%
```

Its main cost is that `d*n = 17 * 28 = 476`, below the 256f baseline proxy of `17 * 32 = 544`. This is why it should be presented as the aggressive experimental variant.

### `sphincs-sm3-224f-dn`

This variant increases the layer count and lowers total tree height:

```text
d*n = 20 * 28 = 560
(h / d) * (d - 1) = 3 * 19 = 57
```

It keeps the `d*n` proxy above the 256f baseline and stays within the 64-bit address constraint. Its benefit is smaller but still meaningful:

```text
49856 - 44548 = 5308 bytes = 10.65%
```

This is the safer variant to emphasize when the review focus is engineering conservatism.

### `h=80,d=20` Candidate

The `h=80,d=20` candidate would keep `d*n = 560` and has a computed signature length of 45108 bytes, but it needs:

```text
(h / d) * (d - 1) = 4 * 19 = 76
```

The current reference address format stores subtree indices in 64 bits, so this candidate requires an address-format extension before implementation.

## Risk Register

| Risk | Impact | Mitigation in this project |
| --- | --- | --- |
| SM3-specific multi-target analysis is incomplete | Cannot claim standard-level security | Mark the project as experimental and list formal analysis as future work. |
| Truncation reduces single-object bit length | Lowers generic hash-object security margin | Use 224 bits rather than a more aggressive value; provide conservative `d*n` variant. |
| Address representation limits parameter search | Blocks some attractive candidates | Check `(h / d) * (d - 1) <= 64` and mark unsupported candidates clearly. |
| Performance results are machine-dependent | Timings may vary across reviewers | Provide reproducible scripts and treat timings as same-machine comparisons. |
| Functional tests could be mistaken for proof | Overclaiming risk | Separate smoke tests, benchmark data, and cryptographic assumptions. |

## Competition Positioning

The strongest defensible claim is:

> This project implements and evaluates an experimental SPHINCS+-SM3 parameter optimization that reduces signature size by truncating internal object representation to 224 bits while keeping standard SM3 computation unchanged.

For FIPS 205 / SLH-DSA positioning, use [fips205-mapping.md](fips205-mapping.md). The project follows the SPHINCS+/SLH-DSA structural family but is not a FIPS-approved SLH-DSA parameter set.

The project should not claim:

- that the new parameter sets are standardized,
- that they are deployment-ready,
- that 224-bit SM3 truncation has a complete SPHINCS+ security proof,
- that smoke tests prove cryptographic security.

## Next Security Work

1. Replace the screening model in [multitarget-security.md](multitarget-security.md) with a proof-aligned SM3-oriented multi-target analysis.
2. Analyze the robust and simple tweakable-hash variants separately.
3. Extend the address format and implement the `h=80,d=20` candidate.
4. Extend the parameter-search report with platform-specific performance objectives.
5. Ask for third-party review of the security assumptions before any deployment claim.

## References

- NIST FIPS 205, Stateless Hash-Based Digital Signature Standard: <https://csrc.nist.gov/pubs/fips/205/final>
- SPHINCS+ reference implementation: <https://github.com/sphincs/sphincsplus>
- Perlner, Kelsey, Cooper, "Breaking Category Five SPHINCS+ with SHA-256": <https://eprint.iacr.org/2022/1061>
