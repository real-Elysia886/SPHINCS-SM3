#!/usr/bin/env python3
"""Build and benchmark selected SPHINCS+ parameter sets."""

from __future__ import annotations

import argparse
import csv
import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "ref"
DOCS = ROOT / "docs"

BASELINE_BYTES = 49_856

BASE_SOURCES = [
    "address.c",
    "randombytes.c",
    "merkle.c",
    "wots.c",
    "wotsx1.c",
    "utils.c",
    "utilsx1.c",
    "fors.c",
    "sign.c",
]

HASH_SOURCES = {
    "sha2": ["sha2.c", "hash_sha2.c", "thash_sha2_robust.c"],
    "sm3": ["sm3.c", "hash_sm3.c", "thash_sm3_robust.c"],
    "shake": ["fips202.c", "hash_shake.c", "thash_shake_robust.c"],
}


@dataclass(frozen=True)
class BenchmarkRow:
    scheme: str
    signature_bytes: int
    public_key_bytes: int
    secret_key_bytes: int
    message_bytes: int
    iterations: int
    keygen_ms: float
    sign_ms: float
    verify_ms: float

    @property
    def saved_bytes(self) -> int:
        return BASELINE_BYTES - self.signature_bytes

    @property
    def saved_percent(self) -> float:
        return 100.0 * self.saved_bytes / BASELINE_BYTES


def hash_family(param: str) -> str:
    for family in HASH_SOURCES:
        if family in param:
            return family
    raise ValueError(f"unsupported parameter family: {param}")


def exe_name(param: str) -> str:
    suffix = param.replace("sphincs-", "").replace("-", "_")
    return f"test\\perf_{suffix}.exe" if "\\" in str(REF) else f"test/perf_{suffix}"


def exe_abs(path: str) -> str:
    return str(REF / path)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(display_arg(part) for part in cmd), flush=True)
    return subprocess.run(cmd, cwd=REF, text=True, capture_output=True)


def display_arg(arg: str) -> str:
    try:
        path = Path(arg)
        if path.is_absolute():
            return str(path.relative_to(REF))
    except ValueError:
        pass
    return arg


def build_and_run(cc: str, param: str, iterations: int, message_bytes: int) -> BenchmarkRow:
    family = hash_family(param)
    output = exe_name(param)
    cmd = [
        cc,
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-O2",
        "-std=c99",
        f"-DPARAMS={param}",
        f"-DSPX_BENCH_ITERS={iterations}",
        f"-DSPX_MLEN={message_bytes}",
        "-o",
        output,
        *BASE_SOURCES,
        *HASH_SOURCES[family],
        "test\\perf_api.c" if "\\" in output else "test/perf_api.c",
    ]

    proc = run(cmd)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)

    proc = run([exe_abs(output)])
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout + proc.stderr)

    print(proc.stdout, end="")
    result_line = next(
        line for line in proc.stdout.splitlines() if line.startswith("RESULT,")
    )
    fields = next(csv.reader([result_line]))
    return BenchmarkRow(
        scheme=param,
        signature_bytes=int(fields[1]),
        public_key_bytes=int(fields[2]),
        secret_key_bytes=int(fields[3]),
        message_bytes=int(fields[4]),
        iterations=int(fields[5]),
        keygen_ms=float(fields[6]),
        sign_ms=float(fields[7]),
        verify_ms=float(fields[8]),
    )


def markdown_table(rows: list[BenchmarkRow]) -> str:
    lines = [
        "| Scheme | Signature bytes | Saved vs 256f | Public key | Secret key | Keygen avg | Sign avg | Verify avg |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        saved = f"{row.saved_bytes} ({row.saved_percent:.2f}%)"
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{row.scheme}`",
                    str(row.signature_bytes),
                    saved,
                    str(row.public_key_bytes),
                    str(row.secret_key_bytes),
                    f"{row.keygen_ms:.3f} ms",
                    f"{row.sign_ms:.3f} ms",
                    f"{row.verify_ms:.3f} ms",
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def write_doc(rows: list[BenchmarkRow], cc: str) -> Path:
    DOCS.mkdir(exist_ok=True)
    path = DOCS / "performance.md"
    iterations = rows[0].iterations if rows else 0
    message_bytes = rows[0].message_bytes if rows else 0
    text = f"""# Performance Notes

This page records a reproducible local benchmark path for the implemented parameter sets. Timings are environment-dependent; use them to compare trends under the same machine and compiler rather than as universal constants.

## Command

```bash
python tools/benchmark_params.py --iterations {iterations} --message-bytes {message_bytes}
```

## Environment

- OS: `{platform.platform()}`
- Machine: `{platform.machine()}`
- Compiler command: `{cc}`
- Iterations per operation: `{iterations}`
- Message length: `{message_bytes}` bytes

## Results

{markdown_table(rows)}

## Interpretation

- `sphincs-sm3-224f` gives the strongest implemented signature-size reduction.
- `sphincs-sm3-224f-dn` keeps the `d*n` structural proxy at or above the 256f baseline while still reducing signature size.
- The optimization target is signature length. Runtime should be evaluated together with parameter shape, implementation constraints, and the SM3 backend cost.
"""
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cc", default=None)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--message-bytes", type=int, default=64)
    parser.add_argument(
        "--params",
        nargs="+",
        default=[
            "sphincs-sha2-256f",
            "sphincs-sm3-224f",
            "sphincs-sm3-224f-dn",
        ],
    )
    parser.add_argument("--no-write-doc", action="store_true")
    parser.add_argument("--keep-binaries", action="store_true")
    args = parser.parse_args()

    cc = args.cc or ("clang" if shutil.which("clang") else "cc")
    if shutil.which(cc) is None:
        print(f"missing compiler: {cc}")
        return 127

    rows = [
        build_and_run(cc, param, args.iterations, args.message_bytes)
        for param in args.params
    ]
    print()
    print(markdown_table(rows))

    if not args.no_write_doc:
        path = write_doc(rows, cc)
        print(f"\nwrote {path.relative_to(ROOT)}")

    if not args.keep_binaries:
        for param in args.params:
            binary = REF / exe_name(param)
            if binary.exists():
                binary.unlink()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
