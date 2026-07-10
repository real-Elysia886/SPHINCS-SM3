<p align="center">
  <img src="assets/showcase/logo.png" width="128" alt="SPHINCS+-SM3 project logo">
</p>

<h1 align="center">SPHINCS+-SM3</h1>

<p align="center">
  <strong>Truncated-hash signature size optimization for the SM3 instantiation of SPHINCS+.</strong>
</p>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README_CN.md">中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Post--Quantum-SPHINCS%2B-2E74B5" alt="Post-quantum SPHINCS+">
  <img src="https://img.shields.io/badge/Hash-SM3-c62828" alt="SM3">
  <img src="https://img.shields.io/badge/C-99-00599C?logo=c" alt="C99">
  <img src="https://github.com/real-Elysia886/SPHINCS-SM3/actions/workflows/ci.yml/badge.svg" alt="CI">
  <img src="https://img.shields.io/badge/tests-KAT%20%2B%20sign%2Fverify-brightgreen" alt="Tests">
  <img src="https://img.shields.io/badge/status-experimental-orange" alt="Experimental">
</p>

<p align="center">
  <a href="#results">Results</a> ·
  <a href="#performance">Performance</a> ·
  <a href="#project-documentation">Project Documentation</a> ·
  <a href="#quick-start">Quick Start</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#security-notes">Security Notes</a>
</p>

![SPHINCS+-SM3 hero](assets/showcase/hero.png)

<table>
  <tr>
    <td align="center"><strong>20.14%</strong><br>maximum implemented signature-size reduction</td>
    <td align="center"><strong>39,816 B</strong><br><code>sphincs-sm3-224f</code> signature size</td>
    <td align="center"><strong>76-bit index</strong><br><code>sphincs-sm3-224f-h80</code> wide-address prototype</td>
    <td align="center"><strong>SM3 KAT + sign/verify</strong><br>reproducible test path</td>
  </tr>
</table>

## Why This Project

SPHINCS+ is a stateless hash-based post-quantum signature scheme. An SM3-based instantiation is attractive for Chinese cryptographic ecosystems, but the fast high-security parameter shape produces large signatures. This project explores whether the internal object length can be reduced by truncating the output representation while keeping the standard SM3 computation intact.

The repository is organized as a reproducible experimental study:

- An SM3 backend for the SPHINCS+ reference implementation.
- Three implemented 224-bit parameter sets, including an isolated wide-address prototype.
- Parameter-size and address-constraint analysis scripts.
- SM3 Known-Answer Tests (KATs).
- Sign/verify smoke tests for all three parameter sets.

> [!NOTE]
> This is an experimental parameter-optimization study, not a deployment-ready signature standard.

## Feature Overview

| Capability | What you get |
| --- | --- |
| SM3 backend | `sm3.c`, `hash_sm3.c`, `thash_sm3_simple.c`, and `thash_sm3_robust.c` |
| 224-bit truncation | SM3 still computes 256-bit digests; SPHINCS+ objects keep the first 28 bytes |
| Parameter search | Reproducible size formulas, address checks, and Pareto-style candidate search |
| Wide tree addressing | Portable high/low 64-bit index operations plus an isolated 12-byte tree field for the 76-bit prototype |
| SM3 KAT | Known-answer tests for empty string, `abc`, and `abcd` repeated 16 times |
| Smoke tests | keygen, sign, verify, in-place verify, and tamper rejection |
| Windows-friendly runner | `tools/clang_smoke_test.py` for environments without GNU Make |

## Results

<p align="center">
  <img src="assets/showcase/results-concept.png" alt="Conceptual signature-size comparison" width="820">
</p>

The visual above is illustrative. The reproducible numeric results are listed below and checked by `tools/check_consistency.py`.

| Scheme | n | h | d | h/d | WOTS len | d*n | Tree bits | Signature bytes | Saved vs 256f | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| SHA2-256f baseline | 32 | 68 | 17 | 4 | 67 | 544 | 64 | 49856 | 0 | baseline |
| sphincs-sm3-224f | 28 | 68 | 17 | 4 | 59 | 476 | 64 | 39816 | 10040 (20.14%) | implemented |
| sphincs-sm3-224f-dn | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | implemented |
| sphincs-sm3-224f-h80 | 28 | 80 | 20 | 4 | 59 | 560 | 76 | 45108 | 4748 (9.52%) | wide-address prototype |

The original compressed address path stores subtree indices in 64 bits:

```text
(h / d) * (d - 1) <= 64
```

The new `sphincs-sm3-224f-h80` parameter set crosses that boundary with a separate 12-byte tree field and 26-byte compressed SM3 address. The existing parameter sets retain their original 8-byte tree field and 22-byte compressed address.

## Performance

The repository includes a reproducible API-level benchmark for key generation, signing, and verification:

```bash
python tools/benchmark_params.py --iterations 5 --message-bytes 64
```

The latest local benchmark table is recorded in [docs/performance.md](docs/performance.md). Timings are environment-dependent; the table is intended for same-machine comparison of signature-size savings and runtime trends.

## Project Documentation

| Document | Description |
| --- | --- |
| [Parameter Search](docs/parameter-search.md) | Search constraints, Pareto candidates, and parameter-selection rationale |
| [Security Analysis](docs/security-analysis.md) | Cryptographic assumptions, collision bounds, and security claim boundary |
| [FIPS 205 Mapping](docs/fips205-mapping.md) | SLH-DSA structural mapping and compliance boundary |
| [Multi-Target Security](docs/multitarget-security.md) | 224-bit truncation screening formula and work-factor table |
| [Performance Benchmarks](docs/performance.md) | Runtime performance comparisons and optimization analysis |
| [Execution Evidence](docs/evidence/README.md) | Command outputs and logs verifying implementation consistency |

## Quick Start

### Static checks

```bash
python tools/check_consistency.py
python tools/analyze_params.py --search --pareto
```

Expected highlights:

```text
params-sphincs-sm3-224f.h: ok (sig=39816, tree_bits=64, tree_addr_bytes=8)
params-sphincs-sm3-224f-dn.h: ok (sig=44548, tree_bits=57, tree_addr_bytes=8)
params-sphincs-sm3-224f-h80.h: ok (sig=45108, tree_bits=76, tree_addr_bytes=12)
```

### Windows / clang smoke test

```bash
python tools/clang_smoke_test.py
```

This builds and runs SM3 known-answer tests, key generation, signing, verification, in-place verification, and tamper rejection for all three SM3 parameter sets.

### GNU Make workflow

```bash
cd ref
make clean
make test/sm3_kat PARAMS=sphincs-sm3-224f THASH=robust
./test/sm3_kat

make clean
make test/spx PARAMS=sphincs-sm3-224f THASH=robust
./test/spx

make clean
make test/spx PARAMS=sphincs-sm3-224f-dn THASH=robust
./test/spx

make clean
make test/spx PARAMS=sphincs-sm3-224f-h80 THASH=robust
./test/spx
```

Stronger sign/verify check:

```bash
make clean
make test/spx PARAMS=sphincs-sm3-224f-dn THASH=robust \
  EXTRA_CFLAGS="-DSPX_SIGNATURES=3 -DSPX_MLEN=64 -DSPX_TEST_INVALIDSIG"
./test/spx
```

## Architecture

```text
SPHINCS+ reference implementation
  ref/sign.c                  signature API
  ref/fors.c                  FORS signing component
  ref/wots.c                  WOTS+ signing component
  ref/merkle.c                Merkle tree logic

SM3 instantiation
  ref/sm3.c                   SM3 compression, incremental API, MGF1
  ref/hash_sm3.c              PRF, message randomness, H_msg
  ref/thash_sm3_simple.c      simple tree hash
  ref/thash_sm3_robust.c      robust tree hash
  ref/sm3_offsets.h           compressed address layout
  ref/sm3_extended_offsets.h  isolated wide-address layout

Experimental parameters
  ref/params/params-sphincs-sm3-224f.h
  ref/params/params-sphincs-sm3-224f-dn.h
  ref/params/params-sphincs-sm3-224f-h80.h

Reproducibility tools
  tools/analyze_params.py
  tools/check_consistency.py
  tools/clang_smoke_test.py
  tools/run_experiments.py
```

## Security Notes

- Truncating SM3 output from 256 bits to 224 bits lowers the upper bound of a single hash object.
- The 224-bit choice is motivated by the known Category Five SPHINCS+ with SHA-256 multi-target analysis around the `2^217.4` waterline.
- The SM3 setting still needs a dedicated formal multi-target second-preimage analysis.
- `sphincs-sm3-224f-dn` preserves `d*n`, but uses `h=60` to satisfy the current 64-bit subtree-address constraint.
- `sphincs-sm3-224f-h80` demonstrates 76-bit subtree indexing, but its distinct address encoding remains experimental and does not add a security proof.

See [docs/security-analysis.md](docs/security-analysis.md) for the detailed assumptions, risk register, and security claim boundary. See [docs/fips205-mapping.md](docs/fips205-mapping.md) for the SLH-DSA/FIPS 205 comparison and [docs/multitarget-security.md](docs/multitarget-security.md) for the 224-bit multi-target screening model.
