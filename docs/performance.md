# Performance Notes

This page records a reproducible local benchmark path for the implemented parameter sets. Timings are environment-dependent; use them to compare trends under the same machine and compiler rather than as universal constants.

## Command

```bash
python tools/benchmark_params.py --iterations 3 --message-bytes 64
```

## Environment

- OS: `Windows-11-10.0.26200-SP0`
- Machine: `AMD64`
- Compiler command: `clang`
- Iterations per operation: `3`
- Message length: `64` bytes

## Results

| Scheme | Signature bytes | Saved vs 256f | Public key | Secret key | Keygen avg | Sign avg | Verify avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `sphincs-sha2-256f` | 49856 | 0 (0.00%) | 64 | 128 | 7.667 ms | 153.333 ms | 4.667 ms |
| `sphincs-sm3-224f` | 39816 | 10040 (20.14%) | 56 | 112 | 6.333 ms | 138.667 ms | 4.000 ms |
| `sphincs-sm3-224f-dn` | 44548 | 5308 (10.65%) | 56 | 112 | 3.333 ms | 93.000 ms | 4.667 ms |
| `sphincs-sm3-224f-h80` | 45108 | 4748 (9.52%) | 56 | 112 | 9.333 ms | 233.667 ms | 6.333 ms |

## Interpretation

- `sphincs-sm3-224f` gives the strongest implemented signature-size reduction.
- `sphincs-sm3-224f-dn` keeps the `d*n` structural proxy at or above the 256f baseline while still reducing signature size.
- `sphincs-sm3-224f-h80` validates the 76-bit wide-address path; its deeper tree shape increases signing cost in this reference implementation.
- The optimization target is signature length. Runtime should be evaluated together with parameter shape, implementation constraints, and the SM3 backend cost.
