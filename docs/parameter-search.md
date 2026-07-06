# Parameter Search Report

This report documents the parameter-search logic used by the SPHINCS+-SM3 experiment. It is generated from `tools/analyze_params.py` and is intended to show that the implemented parameter sets are chosen from explicit engineering constraints rather than ad hoc selection.

## Command

```bash
python tools/analyze_params.py --search --pareto --write-doc
```

## Search Constraints

| Constraint | Value |
| --- | ---: |
| Object size `n` | 28 bytes |
| FORS height `a` | 9 |
| FORS trees `k` | 35 |
| Winternitz parameter `w` | 16 |
| Total height range `h` | 1..100 |
| Layer range `d` | 1..40 |
| Minimum `d*n` | 544 |
| Maximum subtree-address bits | 64 |
| Maximum per-layer tree height | 32 |

The current reference implementation stores subtree indices in 64 bits, so a directly implementable parameter set must satisfy:

```text
(h / d) * (d - 1) <= 64
```

## Implemented and Candidate Sets

| scheme | n | h | d | h/d | WOTS len | d*n | tree bits | sig bytes | saved vs 256f | compatible <= 64 bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sphincs-sha2-256f baseline | 32 | 68 | 17 | 4 | 67 | 544 | 64 | 49856 | 0 (0.00%) | yes |
| sphincs-sm3-224f implemented | 28 | 68 | 17 | 4 | 59 | 476 | 64 | 39816 | 10040 (20.14%) | yes |
| sphincs-sm3-224f-dn implemented | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | yes |
| h=80,d=20 candidate | 28 | 80 | 20 | 4 | 59 | 560 | 76 | 45108 | 4748 (9.52%) | no |

## Shortest Compatible Candidates

These are the shortest candidates satisfying the configured `d*n` and address constraints.

| scheme | n | h | d | h/d | WOTS len | d*n | tree bits | sig bytes | saved vs 256f | compatible <= 64 bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n=28,h=20,d=20 | 28 | 20 | 20 | 1 | 59 | 560 | 19 | 43428 | 6428 (12.89%) | yes |
| n=28,h=40,d=20 | 28 | 40 | 20 | 2 | 59 | 560 | 38 | 43988 | 5868 (11.77%) | yes |
| n=28,h=60,d=20 | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | yes |
| n=28,h=21,d=21 | 28 | 21 | 21 | 1 | 59 | 588 | 20 | 45108 | 4748 (9.52%) | yes |
| n=28,h=42,d=21 | 28 | 42 | 21 | 2 | 59 | 588 | 40 | 45696 | 4160 (8.34%) | yes |
| n=28,h=63,d=21 | 28 | 63 | 21 | 3 | 59 | 588 | 60 | 46284 | 3572 (7.16%) | yes |
| n=28,h=22,d=22 | 28 | 22 | 22 | 1 | 59 | 616 | 21 | 46788 | 3068 (6.15%) | yes |
| n=28,h=44,d=22 | 28 | 44 | 22 | 2 | 59 | 616 | 42 | 47404 | 2452 (4.92%) | yes |
| n=28,h=66,d=22 | 28 | 66 | 22 | 3 | 59 | 616 | 63 | 48020 | 1836 (3.68%) | yes |
| n=28,h=23,d=23 | 28 | 23 | 23 | 1 | 59 | 644 | 22 | 48468 | 1388 (2.78%) | yes |
| n=28,h=46,d=23 | 28 | 46 | 23 | 2 | 59 | 644 | 44 | 49112 | 744 (1.49%) | yes |
| n=28,h=24,d=24 | 28 | 24 | 24 | 1 | 59 | 672 | 23 | 50148 | -292 (-0.59%) | yes |

## Pareto Front

The Pareto front is computed over three objectives:

- minimize signature size,
- maximize `d*n`,
- maximize total tree height `h`.

| scheme | n | h | d | h/d | WOTS len | d*n | tree bits | sig bytes | saved vs 256f | compatible <= 64 bits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n=28,h=20,d=20 | 28 | 20 | 20 | 1 | 59 | 560 | 19 | 43428 | 6428 (12.89%) | yes |
| n=28,h=40,d=20 | 28 | 40 | 20 | 2 | 59 | 560 | 38 | 43988 | 5868 (11.77%) | yes |
| n=28,h=60,d=20 | 28 | 60 | 20 | 3 | 59 | 560 | 57 | 44548 | 5308 (10.65%) | yes |
| n=28,h=21,d=21 | 28 | 21 | 21 | 1 | 59 | 588 | 20 | 45108 | 4748 (9.52%) | yes |
| n=28,h=42,d=21 | 28 | 42 | 21 | 2 | 59 | 588 | 40 | 45696 | 4160 (8.34%) | yes |
| n=28,h=63,d=21 | 28 | 63 | 21 | 3 | 59 | 588 | 60 | 46284 | 3572 (7.16%) | yes |
| n=28,h=22,d=22 | 28 | 22 | 22 | 1 | 59 | 616 | 21 | 46788 | 3068 (6.15%) | yes |
| n=28,h=44,d=22 | 28 | 44 | 22 | 2 | 59 | 616 | 42 | 47404 | 2452 (4.92%) | yes |
| n=28,h=66,d=22 | 28 | 66 | 22 | 3 | 59 | 616 | 63 | 48020 | 1836 (3.68%) | yes |
| n=28,h=23,d=23 | 28 | 23 | 23 | 1 | 59 | 644 | 22 | 48468 | 1388 (2.78%) | yes |
| n=28,h=46,d=23 | 28 | 46 | 23 | 2 | 59 | 644 | 44 | 49112 | 744 (1.49%) | yes |
| n=28,h=24,d=24 | 28 | 24 | 24 | 1 | 59 | 672 | 23 | 50148 | -292 (-0.59%) | yes |

## Interpretation

- `sphincs-sm3-224f` is the aggressive implemented choice: it keeps the 256f tree shape and gives the largest implemented size reduction, but its `d*n` proxy is below the 256f baseline.
- `sphincs-sm3-224f-dn` is the conservative implemented choice: it preserves `d*n >= 544`, remains address-compatible, and still reduces signature size by 10.65%.
- `h=80,d=20` is an attractive theoretical candidate because it keeps `d*n = 560`, but it needs 76 subtree-address bits and therefore requires an address-format extension before implementation.

## Next Work

1. Add an extended-address prototype to evaluate `h=80,d=20`.
2. Add simple/robust tweakable-hash comparisons.
3. Expand the search objective set with performance measurements once more platforms are tested.
