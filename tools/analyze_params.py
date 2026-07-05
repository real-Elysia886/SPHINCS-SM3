#!/usr/bin/env python3
"""Compute SPHINCS+-SM3 parameter sizes and implementation constraints."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Params:
    name: str
    n: int
    h: int
    d: int
    a: int
    k: int
    w: int = 16

    @property
    def logw(self) -> int:
        return int(math.log2(self.w))

    @property
    def wots_len1(self) -> int:
        return 8 * self.n // self.logw

    @property
    def wots_len2(self) -> int:
        x = self.wots_len1 * (self.w - 1)
        result = 0
        power = 1
        while power <= x:
            result += 1
            power *= self.w
        return result

    @property
    def wots_len(self) -> int:
        return self.wots_len1 + self.wots_len2

    @property
    def tree_height(self) -> int | None:
        if self.h % self.d != 0:
            return None
        return self.h // self.d

    @property
    def tree_bits(self) -> int | None:
        if self.tree_height is None:
            return None
        return self.tree_height * (self.d - 1)

    @property
    def sig_bytes(self) -> int:
        return (
            self.n
            + (self.a + 1) * self.k * self.n
            + self.d * self.wots_len * self.n
            + self.h * self.n
        )

    @property
    def dn(self) -> int:
        return self.d * self.n

    @property
    def ref_compatible(self) -> bool:
        return (
            self.tree_height is not None
            and self.tree_bits is not None
            and self.tree_bits <= 64
            and self.tree_height <= 32
        )


BASELINE = Params("sphincs-sha2-256f baseline", 32, 68, 17, 9, 35)

CANDIDATES = [
    BASELINE,
    Params("sphincs-sm3-224f implemented", 28, 68, 17, 9, 35),
    Params("sphincs-sm3-224f-dn implemented", 28, 60, 20, 9, 35),
    Params("h=80,d=20 candidate", 28, 80, 20, 9, 35),
]


def row(p: Params) -> list[str]:
    saved = BASELINE.sig_bytes - p.sig_bytes
    pct = 100.0 * saved / BASELINE.sig_bytes
    return [
        p.name,
        str(p.n),
        str(p.h),
        str(p.d),
        str(p.tree_height) if p.tree_height is not None else "invalid",
        str(p.wots_len),
        str(p.dn),
        str(p.tree_bits) if p.tree_bits is not None else "invalid",
        str(p.sig_bytes),
        f"{saved} ({pct:.2f}%)",
        "yes" if p.ref_compatible else "no",
    ]


def print_markdown(params: list[Params]) -> None:
    headers = [
        "scheme",
        "n",
        "h",
        "d",
        "h/d",
        "WOTS len",
        "d*n",
        "tree bits",
        "sig bytes",
        "saved vs 256f",
        "ref-compatible",
    ]
    rows = [row(p) for p in params]
    print("| " + " | ".join(headers) + " |")
    print("| " + " | ".join(["---"] * len(headers)) + " |")
    for values in rows:
        print("| " + " | ".join(values) + " |")


def search(args: argparse.Namespace) -> None:
    print("Reference-compatible candidates with d*n >= baseline d*n:")
    found = False
    for d in range(args.min_d, args.max_d + 1):
        for h in range(args.min_h, args.max_h + 1):
            p = Params(f"n={args.n},h={h},d={d}", args.n, h, d, args.a, args.k, args.w)
            if p.dn >= BASELINE.dn and p.ref_compatible:
                found = True
                print(
                    f"  h={h:3d} d={d:2d} h/d={p.tree_height:2d} "
                    f"tree_bits={p.tree_bits:2d} sig={p.sig_bytes}"
                )
    if not found:
        print("  none in the requested range")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--n", type=int, default=28)
    parser.add_argument("--a", type=int, default=9)
    parser.add_argument("--k", type=int, default=35)
    parser.add_argument("--w", type=int, default=16)
    parser.add_argument("--min-h", type=int, default=1)
    parser.add_argument("--max-h", type=int, default=100)
    parser.add_argument("--min-d", type=int, default=1)
    parser.add_argument("--max-d", type=int, default=40)
    args = parser.parse_args()

    print_markdown(CANDIDATES)
    print()
    print(
        "Constraint: the reference address format stores subtree indices in 64 bits, "
        "so (h / d) * (d - 1) must be <= 64."
    )
    if args.search:
        print()
        search(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
