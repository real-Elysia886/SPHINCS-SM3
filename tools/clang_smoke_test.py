#!/usr/bin/env python3
"""Build and run the SM3 KAT and SPHINCS+ smoke tests with clang."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "ref"

COMMON_SOURCES = [
    "address.c",
    "randombytes.c",
    "merkle.c",
    "wots.c",
    "wotsx1.c",
    "utils.c",
    "utilsx1.c",
    "fors.c",
    "sign.c",
    "sm3.c",
    "hash_sm3.c",
]


def run(cmd: list[str]) -> int:
    print("$ " + " ".join(display_arg(part) for part in cmd), flush=True)
    proc = subprocess.run(cmd, cwd=REF, text=True)
    return proc.returncode


def display_arg(arg: str) -> str:
    try:
        path = Path(arg)
        if path.is_absolute():
            return str(path.relative_to(REF))
    except ValueError:
        pass
    return arg


def exe(name: str) -> str:
    return f"test\\{name}.exe" if "\\" in str(REF) else f"test/{name}"


def exe_abs(path: str) -> str:
    return str(REF / path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clang", default="clang")
    parser.add_argument("--signatures", default="1")
    parser.add_argument("--message-bytes", default="32")
    parser.add_argument("--thash", choices=["robust", "simple"], default="robust")
    parser.add_argument("--keep-binaries", action="store_true")
    parser.add_argument(
        "--params",
        nargs="+",
        default=[
            "sphincs-sm3-224f",
            "sphincs-sm3-224f-dn",
            "sphincs-sm3-224f-h80",
        ],
    )
    args = parser.parse_args()

    if shutil.which(args.clang) is None:
        print(f"missing clang: {args.clang}")
        return 127

    ret = 0
    artifacts: list[Path] = []
    for param in args.params:
        suffix = param.replace("sphincs-", "").replace("-", "_")
        kat = exe(f"sm3_kat_{suffix}")
        spx = exe(f"spx_{suffix}_{args.thash}")
        artifacts.extend([REF / kat, REF / spx])

        step_ret = run([
            args.clang,
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-O2",
            "-std=c99",
            f"-DPARAMS={param}",
            "-o",
            kat,
            "sm3.c",
            "test\\sm3_kat.c" if "\\" in kat else "test/sm3_kat.c",
        ])
        if step_ret == 0:
            step_ret |= run([exe_abs(kat)])
        ret |= step_ret

        step_ret = run([
            args.clang,
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-O2",
            "-std=c99",
            f"-DPARAMS={param}",
            f"-DSPX_SIGNATURES={args.signatures}",
            f"-DSPX_MLEN={args.message_bytes}",
            "-o",
            spx,
            *COMMON_SOURCES,
            f"thash_sm3_{args.thash}.c",
            "test\\spx.c" if "\\" in spx else "test/spx.c",
        ])
        if step_ret == 0:
            step_ret |= run([exe_abs(spx)])
        ret |= step_ret

    if not args.keep_binaries:
        for artifact in artifacts:
            artifact.unlink(missing_ok=True)

    return 0 if ret == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
