#!/usr/bin/env python3
"""Compute and search SPHINCS+-SM3 parameter-size trade-offs."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


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

    def address_compatible(self, address_bits: int = 64) -> bool:
        return (
            self.tree_height is not None
            and self.tree_bits is not None
            and self.tree_bits <= address_bits
            and self.tree_height <= 32
        )

    @property
    def ref_compatible(self) -> bool:
        return self.address_compatible(64)


BASELINE = Params("sphincs-sha2-256f baseline", 32, 68, 17, 9, 35)

CANDIDATES = [
    BASELINE,
    Params("sphincs-sm3-224f implemented", 28, 68, 17, 9, 35),
    Params("sphincs-sm3-224f-dn implemented", 28, 60, 20, 9, 35),
    Params("sphincs-sm3-224f-h80 wide-address prototype", 28, 80, 20, 9, 35),
]


def saved_text(p: Params) -> str:
    saved = BASELINE.sig_bytes - p.sig_bytes
    pct = 100.0 * saved / BASELINE.sig_bytes
    return f"{saved} ({pct:.2f}%)"


def row(p: Params, address_bits: int = 64) -> list[str]:
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
        saved_text(p),
        "yes" if p.address_compatible(address_bits) else "no",
    ]


def markdown_table(params: list[Params], address_bits: int = 64) -> str:
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
        f"original address <= {address_bits} bits",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for p in params:
        lines.append("| " + " | ".join(row(p, address_bits)) + " |")
    return "\n".join(lines)


def print_markdown(params: list[Params], address_bits: int = 64) -> None:
    print(markdown_table(params, address_bits))


def generate(args: argparse.Namespace) -> list[Params]:
    params: list[Params] = []
    for d in range(args.min_d, args.max_d + 1):
        for h in range(args.min_h, args.max_h + 1):
            p = Params(f"n={args.n},h={h},d={d}", args.n, h, d, args.a, args.k, args.w)
            if p.tree_height is None:
                continue
            if p.tree_height > args.max_tree_height:
                continue
            if p.tree_bits is None or p.tree_bits > args.max_tree_bits:
                continue
            if args.require_ref_compatible and not p.address_compatible(args.address_bits):
                continue
            if args.min_dn is not None and p.dn < args.min_dn:
                continue
            params.append(p)
    return sorted(params, key=lambda p: (p.sig_bytes, -p.dn, -p.h, p.d))


def dominates(a: Params, b: Params) -> bool:
    """Return true if a is at least as good as b in core trade-off objectives."""
    at_least = (
        a.sig_bytes <= b.sig_bytes
        and a.dn >= b.dn
        and a.h >= b.h
    )
    strict = (
        a.sig_bytes < b.sig_bytes
        or a.dn > b.dn
        or a.h > b.h
    )
    return at_least and strict


def pareto_front(params: list[Params]) -> list[Params]:
    front = []
    for p in params:
        if not any(dominates(q, p) for q in params if q is not p):
            front.append(p)
    return sorted(front, key=lambda p: (p.sig_bytes, -p.dn, -p.h, p.d))


def search(args: argparse.Namespace) -> list[Params]:
    params = generate(args)
    print(
        f"Reference-compatible candidates with d*n >= {args.min_dn} "
        f"and tree bits <= {args.address_bits}:"
    )
    if not params:
        print("  none in the requested range")
        return []
    for p in params[: args.top]:
        print(
            f"  h={p.h:3d} d={p.d:2d} h/d={p.tree_height:2d} "
            f"d*n={p.dn:3d} tree_bits={p.tree_bits:2d} sig={p.sig_bytes}"
        )
    if len(params) > args.top:
        print(f"  ... {len(params) - args.top} more candidates omitted")
    return params


def print_pareto(args: argparse.Namespace) -> list[Params]:
    params = generate(args)
    front = pareto_front(params)
    print(
        f"Pareto front over signature size, d*n, and h "
        f"({len(front)} of {len(params)} candidates):"
    )
    if not front:
        print("  none in the requested range")
        return []
    print_markdown(front[: args.top], args.address_bits)
    if len(front) > args.top:
        print(f"\n... {len(front) - args.top} more Pareto candidates omitted")
    return front


def write_parameter_report(args: argparse.Namespace) -> Path:
    params = generate(args)
    front = pareto_front(params)
    report_front = front[: args.top]
    DOCS.mkdir(exist_ok=True)
    path = DOCS / "parameter-search.md"

    selected = [
        Params("sphincs-sm3-224f implemented", 28, 68, 17, 9, 35),
        Params("sphincs-sm3-224f-dn implemented", 28, 60, 20, 9, 35),
        Params("sphincs-sm3-224f-h80 wide-address prototype", 28, 80, 20, 9, 35),
    ]
    shortest = params[: min(args.top, len(params))]

    text = f"""# Parameter Search Report

This report documents the parameter-search logic used by the SPHINCS+-SM3 experiment. It is generated from `tools/analyze_params.py` and is intended to show that the implemented parameter sets are chosen from explicit engineering constraints rather than ad hoc selection.

## Command

```bash
python tools/analyze_params.py --search --pareto --write-doc
```

## Search Constraints

| Constraint | Value |
| --- | ---: |
| Object size `n` | {args.n} bytes |
| FORS height `a` | {args.a} |
| FORS trees `k` | {args.k} |
| Winternitz parameter `w` | {args.w} |
| Total height range `h` | {args.min_h}..{args.max_h} |
| Layer range `d` | {args.min_d}..{args.max_d} |
| Minimum `d*n` | {args.min_dn} |
| Maximum subtree-address bits | {args.address_bits} |
| Maximum per-layer tree height | {args.max_tree_height} |

The unmodified reference address path stores subtree indices in 64 bits, so a parameter set using the original compressed layout must satisfy:

```text
(h / d) * (d - 1) <= 64
```

## Implemented Sets and Baseline

{markdown_table([BASELINE, *selected], args.address_bits)}

## Shortest Compatible Candidates

These are the shortest candidates satisfying the configured `d*n` and address constraints.

{markdown_table(shortest, args.address_bits) if shortest else "No compatible candidates found."}

## Pareto Front

The Pareto front is computed over three objectives:

- minimize signature size,
- maximize `d*n`,
- maximize total tree height `h`.

{markdown_table(report_front, args.address_bits) if report_front else "No Pareto candidates found."}

## Interpretation

- `sphincs-sm3-224f` is the aggressive implemented choice: it keeps the 256f tree shape and gives the largest implemented size reduction, but its `d*n` proxy is below the 256f baseline.
- `sphincs-sm3-224f-dn` is the conservative implemented choice: it preserves `d*n >= 544`, remains address-compatible, and still reduces signature size by 10.65%.
- `sphincs-sm3-224f-h80` is the implemented wide-address prototype: it keeps `d*n = 560`, uses 76 subtree-index bits, and serializes them into a separate 12-byte tree field.
- The wide-address prototype deliberately uses a distinct 26-byte compressed SM3 address layout; it is not wire-compatible with the original 22-byte experimental layout.

## Next Work

1. Add deterministic tests for the wide tree-index conversion helpers.
2. Add simple/robust tweakable-hash comparisons.
3. Expand the search objective set with performance measurements once more platforms are tested.
"""
    path.write_text(text, encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--search", action="store_true")
    parser.add_argument("--pareto", action="store_true")
    parser.add_argument("--write-doc", action="store_true")
    parser.add_argument("--n", type=int, default=28)
    parser.add_argument("--a", type=int, default=9)
    parser.add_argument("--k", type=int, default=35)
    parser.add_argument("--w", type=int, default=16)
    parser.add_argument("--min-h", type=int, default=1)
    parser.add_argument("--max-h", type=int, default=100)
    parser.add_argument("--min-d", type=int, default=1)
    parser.add_argument("--max-d", type=int, default=40)
    parser.add_argument("--min-dn", type=int, default=BASELINE.dn)
    parser.add_argument("--address-bits", type=int, default=64)
    parser.add_argument("--max-tree-bits", type=int, default=64)
    parser.add_argument("--max-tree-height", type=int, default=32)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument(
        "--allow-incompatible",
        dest="require_ref_compatible",
        action="store_false",
        help="include candidates that fail the current address compatibility check",
    )
    parser.set_defaults(require_ref_compatible=True)
    args = parser.parse_args()

    print_markdown(CANDIDATES, args.address_bits)
    print()
    print(
        "Constraint: the original compressed address format stores subtree indices "
        "in 64 bits; the isolated wide-address prototype extends this field to 96 bits."
    )
    if args.search:
        print()
        search(args)
    if args.pareto:
        print()
        print_pareto(args)
    if args.write_doc:
        path = write_parameter_report(args)
        print(f"\nwrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
