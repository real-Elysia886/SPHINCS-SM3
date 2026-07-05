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
  <a href="#quick-start">Quick Start</a> ·
  <a href="#architecture">Architecture</a> ·
  <a href="#security-notes">Security Notes</a>
</p>

![SPHINCS+-SM3 hero](assets/showcase/hero.png)

<table>
  <tr>
    <td align="center"><strong>20.14%</strong><br>maximum implemented signature-size reduction</td>
    <td align="center"><strong>39,816 B</strong><br><code>sphincs-sm3-224f</code> signature size</td>
    <td align="center"><strong>44,548 B</strong><br><code>sphincs-sm3-224f-dn</code> conservative size</td>
    <td align="center"><strong>SM3 KAT + sign/verify</strong><br>reproducible test path</td>
  </tr>
</table>

## Why This Project

SPHINCS+ is a stateless hash-based post-quantum signature scheme. An SM3-based instantiation is attractive for Chinese cryptographic ecosystems, but the fast high-security parameter shape produces large signatures. This project explores whether the internal object length can be reduced by truncating the output representation while keeping the standard SM3 computation intact.

The repository is organized as a competition-friendly, reproducible experiment:

- an SM3 backend for the SPHINCS+ reference implementation,
- two implemented 224-bit parameter sets,
- parameter-size and address-constraint analysis scripts,
- SM3 known-answer tests,
- sign/verify smoke tests for both parameter sets.

> This is an experimental parameter-optimization study, not a deployment-ready signature standard.

## Feature Overview

| Capability | What you get |
| --- | --- |
| SM3 backend | `sm3.c`, `hash_sm3.c`, `thash_sm3_simple.c`, and `thash_sm3_robust.c` |
| 224-bit truncation | SM3 still computes 256-bit digests; SPHINCS+ objects keep the first 28 bytes |
| Size analysis | Reproducible signature-size formulas and parameter comparisons |
| Address constraint check | Explicit handling of the 64-bit subtree-address limit in the reference code |
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
| h=80,d=20 candidate | 28 | 80 | 20 | 4 | 59 | 560 | 76 | 45108 | 4748 (9.52%) | address extension required |

The reference implementation stores subtree indices in 64 bits:

```text
(h / d) * (d - 1) <= 64
```

Therefore `h=80,d=20` is a useful design candidate, but it cannot be represented by the current address format.

## Quick Start

### Static checks

```bash
python tools/check_consistency.py
python tools/analyze_params.py --search
```

Expected highlights:

```text
params-sphincs-sm3-224f.h: ok (sig=39816, tree_bits=64)
params-sphincs-sm3-224f-dn.h: ok (sig=44548, tree_bits=57)
```

### Windows / clang smoke test

```bash
python tools/clang_smoke_test.py
```

This builds and runs SM3 known-answer tests, key generation, signing, verification, in-place verification, and tamper rejection for both SM3 parameter sets.

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

Experimental parameters
  ref/params/params-sphincs-sm3-224f.h
  ref/params/params-sphincs-sm3-224f-dn.h

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

## Competition Summary

This project targets the large-signature problem of SPHINCS+-SM3. It keeps the standard SM3 compression and full 256-bit computation unchanged, truncates only the internal SPHINCS+ object representation to 224 bits, and evaluates the result under multi-target security and implementation constraints. The implemented `sphincs-sm3-224f` parameter set reduces signature size by 20.14%, while the conservative `sphincs-sm3-224f-dn` set preserves the `d*n` proxy and reduces size by 10.65%. The project includes SM3 KATs, static parameter checks, and reproducible sign/verify tests.
