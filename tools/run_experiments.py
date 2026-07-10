#!/usr/bin/env python3
"""Run reproducible build, KAT, sign/verify, and benchmark experiments."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "ref"
RESULTS = ROOT / "results"


def run(cmd: list[str], outfile: Path) -> int:
    print("$ " + " ".join(cmd))
    proc = subprocess.run(
        cmd,
        cwd=REF,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    with outfile.open("a", encoding="utf-8") as f:
        f.write("$ " + " ".join(cmd) + "\n")
        f.write(proc.stdout)
        if not proc.stdout.endswith("\n"):
            f.write("\n")
        f.write(f"[exit code: {proc.returncode}]\n\n")
    print(proc.stdout)
    return proc.returncode


def require_tool(name: str) -> bool:
    if shutil.which(name) is not None:
        return True
    print(f"missing tool: {name}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--make", default="make")
    parser.add_argument("--cc", default=None)
    parser.add_argument("--skip-benchmark", action="store_true")
    args = parser.parse_args()

    if not require_tool(args.make):
        print("Install GNU Make and a C compiler, then rerun this script.")
        return 127

    RESULTS.mkdir(exist_ok=True)
    make_prefix = [args.make]
    if args.cc:
        make_prefix.append(f"CC={args.cc}")

    params = [
        "sphincs-sm3-224f",
        "sphincs-sm3-224f-dn",
        "sphincs-sm3-224f-h80",
    ]
    ret = 0

    for param in params:
        for old_log in RESULTS.glob(f"{param}-*.txt"):
            old_log.unlink()

        clean_log = RESULTS / f"{param}-clean.txt"
        ret |= run(make_prefix + ["clean"], clean_log)

        kat_log = RESULTS / f"{param}-sm3-kat.txt"
        step_ret = run(make_prefix + ["test/sm3_kat", f"PARAMS={param}", "THASH=robust"], kat_log)
        if step_ret == 0:
            step_ret |= run(["./test/sm3_kat"], kat_log)
        ret |= step_ret

        spx_log = RESULTS / f"{param}-spx.txt"
        step_ret = run(
            make_prefix
            + [
                "test/spx",
                f"PARAMS={param}",
                "THASH=robust",
                "EXTRA_CFLAGS=-DSPX_SIGNATURES=3 -DSPX_MLEN=64 -DSPX_TEST_INVALIDSIG",
            ],
            spx_log,
        )
        if step_ret == 0:
            step_ret |= run(["./test/spx"], spx_log)
        ret |= step_ret

        if not args.skip_benchmark:
            bench_log = RESULTS / f"{param}-benchmark.txt"
            step_ret = run(make_prefix + ["test/benchmark", f"PARAMS={param}", "THASH=robust"], bench_log)
            if step_ret == 0:
                step_ret |= run(["./test/benchmark"], bench_log)
            ret |= step_ret

    return 0 if ret == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
