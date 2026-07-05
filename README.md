# SPHINCS+-SM3 Truncated-Hash Signature Size Optimization

面向 SPHINCS+-SM3 的后量子签名长度优化实验项目。项目基于 SPHINCS+ 参考实现接入国密 SM3 后端，在不修改 SM3 压缩函数、填充规则和完整 256 位计算过程的前提下，将 SPHINCS+ 内部对象表示长度截断至 224 位，并给出可复现的参数分析、正确性测试和工程约束检查。

> 定位：实验性参数优化与工程可行性验证，不是可直接标准化部署的新签名方案。

## Highlights

- **SM3 后端实现**：新增 `sm3.c`、`hash_sm3.c`、`thash_sm3_simple.c`、`thash_sm3_robust.c`。
- **224 位截断实验**：`sphincs-sm3-224f` 将签名长度从 49856 字节降至 39816 字节，减少 **20.14%**。
- **结构安全量保持实验**：`sphincs-sm3-224f-dn` 在当前 64 位 subtree address 约束内保持 `d*n >= 17*32`，签名长度降至 44548 字节，减少 **10.65%**。
- **可复现实验链路**：提供参数复算、SM3 标准向量测试、签名/验签 smoke test 和 Windows/clang 一键验证脚本。
- **工程边界清晰**：明确 `h=80,d=20` 需要 76 位 subtree index，当前参考实现无法直接表示，因此仅作为理论候选。

## Parameter Results

| Scheme | n | h | d | h/d | WOTS len | d*n | Tree bits | Signature bytes | Saved vs 256f | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| SHA2-256f baseline | 32 | 68 | 17 | 4 | 67 | 544 | 64 | 49856 | 0 | baseline |
| sphincs-sm3-224f | 28 | 68 | 17 | 4 | 59 | 476 | 64 | 39816 | 10040 (20.14%) | implemented |
| sphincs-sm3-224f-dn | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | implemented |
| h=80,d=20 candidate | 28 | 80 | 20 | 4 | 59 | 560 | 76 | 45108 | 4748 (9.52%) | address extension required |

The reference implementation stores subtree indices in a 64-bit field:

```text
(h / d) * (d - 1) <= 64
```

So `h=80,d=20` is useful as a design candidate, but it is not represented by the current address format.

## Quick Start

### 1. Static parameter check

```sh
python tools/check_consistency.py
python tools/analyze_params.py --search
```

Expected highlights:

```text
params-sphincs-sm3-224f.h: ok (sig=39816, tree_bits=64)
params-sphincs-sm3-224f-dn.h: ok (sig=44548, tree_bits=57)
```

### 2. Windows / clang smoke test

```sh
python tools/clang_smoke_test.py
```

This builds and runs:

- SM3 known-answer tests: empty string, `abc`, and `abcd` repeated 16 times.
- Key generation, signing, verification, in-place verification, and tamper rejection for both SM3 parameter sets.

### 3. GNU Make workflow

```sh
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

For a stronger sign/verify check:

```sh
make clean
make test/spx PARAMS=sphincs-sm3-224f-dn THASH=robust \
  EXTRA_CFLAGS="-DSPX_SIGNATURES=3 -DSPX_MLEN=64 -DSPX_TEST_INVALIDSIG"
./test/spx
```

## Repository Layout

```text
ref/
  params/params-sphincs-sm3-224f.h       224-bit truncated SM3 parameter set
  params/params-sphincs-sm3-224f-dn.h    d*n-preserving engineering parameter set
  sm3.c, sm3.h                           SM3 implementation and MGF1 helper
  hash_sm3.c                             SPHINCS+ hash backend using SM3
  thash_sm3_simple.c / robust.c          Tree hash implementations for SM3
  test/sm3_kat.c                         SM3 known-answer tests
  test/spx.c                             sign/verify smoke test

tools/
  analyze_params.py                      size and address-constraint analysis
  check_consistency.py                   static parameter-header consistency check
  clang_smoke_test.py                    Windows/clang build-and-test runner
  run_experiments.py                     GNU Make experiment runner
```

## Security Notes

- Truncating SM3 output from 256 bits to 224 bits lowers the upper bound of a single hash object.
- The 224-bit choice is motivated by the known Category Five SPHINCS+ with SHA-256 multi-target analysis around the `2^217.4` waterline.
- The SM3 setting still needs a dedicated formal multi-target second-preimage analysis.
- `sphincs-sm3-224f-dn` preserves `d*n`, but uses `h=60` to satisfy the current 64-bit subtree address implementation constraint.

## 参赛简介（300字以内）

本作品面向国密后量子签名 SPHINCS+-SM3 签名过长的问题，提出基于截断哈希的实验性优化方案。在保持 SM3 标准压缩函数和完整 256 位计算过程不变的前提下，将 SPHINCS+ 内部对象表示长度截断至 224 位，并结合多目标攻击安全水位、d*n 结构安全量和 64 位地址约束进行参数设计。项目实现 SM3 后端、两组实验参数、SM3 标准向量测试和一键签验脚本。实验显示，直接截断方案签名长度降低 20.14%，保守工程方案降低 10.65%，为 SPHINCS+-SM3 在带宽受限场景中的优化提供了可复现依据。
