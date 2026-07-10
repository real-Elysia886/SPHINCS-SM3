# Competition Demo Script

This script is designed for a 3-minute live demo. If the network or compiler environment is unstable, use the captured outputs in `docs/evidence/` as fallback proof.

## 30-Second Opening

本项目针对 SPHINCS+-SM3 签名长度较大的问题，探索一种基于截断哈希对象表示的实验性优化方案。核心原则是：不修改 SM3 压缩函数、填充规则和完整 256 位计算过程，只将 SPHINCS+ 内部对象表示长度调整为 224 位，并通过参数搜索、安全边界说明和自动化测试验证工程可行性。

## Live Demo Commands

### 1. Parameter Consistency

```bash
python tools/check_consistency.py
```

Expected points to highlight:

- `sphincs-sm3-224f` signature size is `39816` bytes.
- `sphincs-sm3-224f-dn` signature size is `44548` bytes.
- `sphincs-sm3-224f-h80` signature size is `45108` bytes and uses a 12-byte tree field for its 76-bit index.

### 2. Parameter Search

```bash
python tools/analyze_params.py --search --pareto --top 5
```

Expected points to highlight:

- The search is constrained by `d*n >= 544` and subtree-address bits.
- `sphincs-sm3-224f-dn` appears as the conservative implemented choice.
- `sphincs-sm3-224f-h80` demonstrates the 76-bit candidate through an isolated wide-address path while preserving the original encodings.

### 3. Correctness Smoke Test

```bash
python tools/clang_smoke_test.py --signatures 1 --message-bytes 32
```

Expected points to highlight:

- SM3 KAT passes for empty string, `abc`, and `abcd x 16`.
- Key generation succeeds.
- Verification succeeds.
- In-place verification succeeds.
- Bit flipping invalidates the signature.

### 4. Performance Check

```bash
python tools/benchmark_params.py --iterations 1 --message-bytes 32 --no-write-doc
```

Expected points to highlight:

- Baseline `sphincs-sha2-256f`: `49856` signature bytes.
- `sphincs-sm3-224f`: `39816` signature bytes, `20.14%` reduction.
- `sphincs-sm3-224f-dn`: `44548` signature bytes, `10.65%` reduction.
- `sphincs-sm3-224f-h80`: `45108` signature bytes, `9.52%` reduction.
- Runtime is environment-dependent, so the benchmark is used for same-machine comparison.

## 3-Minute Talk Track

1. 问题背景：SPHINCS+ 是无状态哈希签名，抗量子安全性强，但签名长度较大；国密 SM3 场景下同样存在带宽和存储压力。
2. 方法设计：保持 SM3 完整 256 位计算不变，只截断 SPHINCS+ 内部对象表示到 224 位，降低 WOTS+、FORS 和认证路径中线性依赖 `n` 的部分。
3. 参数选择：提供激进方案 `224f`、保守方案 `224f-dn` 和宽地址原型 `224f-h80`。第三组参数用隔离地址布局验证了 76 位 subtree index。
4. 实验结果：三组方案签名长度分别降低 `20.14%`、`10.65%` 和 `9.52%`，并提供 SM3 KAT、签名验签、篡改失败和 CI 自动测试。
5. 安全边界：这是实验性参数优化，不声称标准化部署；SM3 场景仍需要独立的多目标第二原像分析。
6. 标准对标：FIPS 205 标准化的是 SLH-DSA，项目继承 SPHINCS+ 结构思路，但 SM3 后端和 224 位参数集属于实验内容，不声称 FIPS 合规。
7. 后续工作：审查扩展地址编码的单射性与证明兼容性，并开展 robust/simple 树哈希对比。

## Fallback Evidence

If a live demo fails because of the environment, open these files:

- `docs/evidence/ci-status.txt`
- `docs/evidence/consistency.txt`
- `docs/evidence/parameter-search.txt`
- `docs/evidence/smoke-test.txt`
- `docs/evidence/performance-check.txt`

Do not present generated images as experimental proof. Use actual terminal output or GitHub Actions status.
