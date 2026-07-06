<p align="center">
  <img src="assets/showcase/logo.png" width="128" alt="SPHINCS+-SM3 项目标志">
</p>

<h1 align="center">SPHINCS+-SM3</h1>

<p align="center">
  <strong>面向 SPHINCS+-SM3 的截断哈希签名长度优化实验。</strong>
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
  <a href="#实验结果">实验结果</a> ·
  <a href="#性能测试">性能测试</a> ·
  <a href="#快速开始">快速开始</a> ·
  <a href="#项目结构">项目结构</a> ·
  <a href="#安全性说明">安全性说明</a> ·
  <a href="docs/security-analysis.md">安全分析</a>
</p>

![SPHINCS+-SM3 展示图](assets/showcase/hero.png)

<table>
  <tr>
    <td align="center"><strong>20.14%</strong><br>已实现方案最大签名长度降幅</td>
    <td align="center"><strong>39,816 B</strong><br><code>sphincs-sm3-224f</code> 签名长度</td>
    <td align="center"><strong>44,548 B</strong><br><code>sphincs-sm3-224f-dn</code> 保守工程方案</td>
    <td align="center"><strong>SM3 KAT + 签验测试</strong><br>可复现实验链路</td>
  </tr>
</table>

## 为什么做这个项目

SPHINCS+ 是无状态的基于哈希后量子签名方案。以国密 SM3 实例化 SPHINCS+ 有利于国产密码算法生态适配，但快速高安全级别参数的签名长度较大，限制了其在带宽敏感场景中的部署。

本项目研究一个更聚焦的问题：在保持 SM3 标准压缩函数、填充规则和完整 256 位计算过程不变的前提下，是否可以仅截断 SPHINCS+ 内部对象的表示长度，从而降低签名大小。

项目整理为适合竞赛展示和复现实验的形态：

- 接入 SM3 后端；
- 给出两组 224 位实验参数；
- 提供参数长度和地址约束分析脚本；
- 提供 SM3 标准向量测试；
- 提供两组参数的签名、验签 smoke test。

> 本项目定位为实验性参数优化与工程可行性验证，不是可直接标准化部署的新签名方案。

## 功能速览

| 能力 | 你会得到什么 |
| --- | --- |
| SM3 后端 | `sm3.c`、`hash_sm3.c`、`thash_sm3_simple.c`、`thash_sm3_robust.c` |
| 224 位截断 | SM3 仍完整计算 256 位摘要，SPHINCS+ 对象仅保留前 28 字节 |
| 长度分析 | 可复现的签名长度公式、参数表和节省比例 |
| 地址约束检查 | 显式检查参考实现中 64 位 subtree address 限制 |
| SM3 KAT | 覆盖空串、`abc`、`abcd` 重复 16 次三个标准向量 |
| 签验测试 | keygen、sign、verify、原地验签和篡改失效测试 |
| Windows 复现 | `tools/clang_smoke_test.py` 支持无 GNU Make 的 clang 环境 |

## 实验结果

<p align="center">
  <img src="assets/showcase/results-concept.png" alt="签名长度对比概念图" width="820">
</p>

上图为展示用概念图；下表中的数值由 `tools/check_consistency.py` 复算校验。

| 方案 | n | h | d | h/d | WOTS len | d*n | tree bits | 签名长度 | 相对 256f 节省 | 状态 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| SHA2-256f 基线 | 32 | 68 | 17 | 4 | 67 | 544 | 64 | 49856 | 0 | 基线 |
| sphincs-sm3-224f | 28 | 68 | 17 | 4 | 59 | 476 | 64 | 39816 | 10040 (20.14%) | 已实现 |
| sphincs-sm3-224f-dn | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | 已实现 |
| h=80,d=20 候选 | 28 | 80 | 20 | 4 | 59 | 560 | 76 | 45108 | 4748 (9.52%) | 需扩展地址表示 |

参考实现使用 64 位字段保存 subtree index，因此需要满足：

```text
(h / d) * (d - 1) <= 64
```

所以 `h=80,d=20` 虽然是有价值的理论候选，但当前地址格式无法直接表示。

## 性能测试

仓库提供了面向 API 的可复现性能测试脚本，覆盖密钥生成、签名和验签：

```bash
python tools/benchmark_params.py --iterations 5 --message-bytes 64
```

最新本地测试结果记录在 [docs/performance.md](docs/performance.md)。性能数据会受机器、编译器和运行环境影响，因此更适合同机比较签名长度收益和运行时间趋势。

## 快速开始

### 静态参数检查

```bash
python tools/check_consistency.py
python tools/analyze_params.py --search
```

预期关键输出：

```text
params-sphincs-sm3-224f.h: ok (sig=39816, tree_bits=64)
params-sphincs-sm3-224f-dn.h: ok (sig=44548, tree_bits=57)
```

### Windows / clang 一键测试

```bash
python tools/clang_smoke_test.py
```

该脚本会编译并运行 SM3 标准向量测试，以及两组 SM3 参数的密钥生成、签名、验签、原地验签和篡改失效测试。

### GNU Make 流程

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

更强的签验测试：

```bash
make clean
make test/spx PARAMS=sphincs-sm3-224f-dn THASH=robust \
  EXTRA_CFLAGS="-DSPX_SIGNATURES=3 -DSPX_MLEN=64 -DSPX_TEST_INVALIDSIG"
./test/spx
```

## 项目结构

```text
SPHINCS+ 参考实现
  ref/sign.c                  签名 API
  ref/fors.c                  FORS 组件
  ref/wots.c                  WOTS+ 组件
  ref/merkle.c                Merkle 树逻辑

SM3 实例化
  ref/sm3.c                   SM3 压缩、增量接口、MGF1
  ref/hash_sm3.c              PRF、消息随机数、H_msg
  ref/thash_sm3_simple.c      simple 树哈希
  ref/thash_sm3_robust.c      robust 树哈希
  ref/sm3_offsets.h           压缩地址布局

实验参数
  ref/params/params-sphincs-sm3-224f.h
  ref/params/params-sphincs-sm3-224f-dn.h

复现实验工具
  tools/analyze_params.py
  tools/check_consistency.py
  tools/clang_smoke_test.py
  tools/run_experiments.py
```

## 安全性说明

- 将 SM3 输出表示长度从 256 位截断到 224 位会降低单个哈希对象的安全上限。
- 224 位选择参考了 Category Five SPHINCS+ with SHA-256 多目标攻击分析中的 `2^217.4` 水位。
- SM3 场景仍需要独立的多目标第二原像形式化分析。
- `sphincs-sm3-224f-dn` 保持 `d*n`，但为了满足当前 64 位 subtree address 约束选择 `h=60`。

详细的假设边界、风险清单和竞赛答辩口径见 [docs/security-analysis.md](docs/security-analysis.md)。

## 参赛简介（300 字以内）

本作品面向国密后量子签名 SPHINCS+-SM3 签名过长的问题，提出基于截断哈希的实验性优化方案。在保持 SM3 标准压缩函数和完整 256 位计算过程不变的前提下，将 SPHINCS+ 内部对象表示长度截断至 224 位，并结合多目标攻击安全水位、d*n 结构安全量和 64 位地址约束进行参数设计。项目实现 SM3 后端、两组实验参数、SM3 标准向量测试和一键签验脚本。实验显示，直接截断方案签名长度降低 20.14%，保守工程方案降低 10.65%，为 SPHINCS+-SM3 在带宽受限场景中的优化提供了可复现依据。
