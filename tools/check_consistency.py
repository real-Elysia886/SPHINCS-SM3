#!/usr/bin/env python3
"""Static consistency checks for the SM3 parameter headers."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PARAM_DIR = ROOT / "ref" / "params"

EXPECTED = {
    "params-sphincs-sm3-224f.h": {
        "SPX_N": 28,
        "SPX_FULL_HEIGHT": 68,
        "SPX_D": 17,
        "SPX_FORS_HEIGHT": 9,
        "SPX_FORS_TREES": 35,
        "SPX_WOTS_W": 16,
        "SPX_BYTES": 39816,
        "TREE_BITS": 64,
    },
    "params-sphincs-sm3-224f-dn.h": {
        "SPX_N": 28,
        "SPX_FULL_HEIGHT": 60,
        "SPX_D": 20,
        "SPX_FORS_HEIGHT": 9,
        "SPX_FORS_TREES": 35,
        "SPX_WOTS_W": 16,
        "SPX_BYTES": 44548,
        "TREE_BITS": 57,
    },
}


def parse_defines(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    values: dict[str, int] = {}
    for name in [
        "SPX_N",
        "SPX_FULL_HEIGHT",
        "SPX_D",
        "SPX_FORS_HEIGHT",
        "SPX_FORS_TREES",
        "SPX_WOTS_W",
    ]:
        match = re.search(rf"^\s*#define\s+{name}\s+(\d+)\s*$", text, re.MULTILINE)
        if match is None:
            raise AssertionError(f"{path.name}: missing {name}")
        values[name] = int(match.group(1))
    return values


def wots_len(n: int, w: int) -> int:
    logw = {16: 4, 256: 8}[w]
    len1 = 8 * n // logw
    x = len1 * (w - 1)
    len2 = 0
    power = 1
    while power <= x:
        len2 += 1
        power *= w
    return len1 + len2


def compute(values: dict[str, int]) -> dict[str, int]:
    n = values["SPX_N"]
    h = values["SPX_FULL_HEIGHT"]
    d = values["SPX_D"]
    a = values["SPX_FORS_HEIGHT"]
    k = values["SPX_FORS_TREES"]
    w = values["SPX_WOTS_W"]
    tree_height = h // d
    if tree_height * d != h:
        raise AssertionError(f"h={h} is not divisible by d={d}")
    length = wots_len(n, w)
    return {
        "SPX_BYTES": n + (a + 1) * k * n + d * length * n + h * n,
        "TREE_BITS": tree_height * (d - 1),
    }


def main() -> int:
    for filename, expected in EXPECTED.items():
        path = PARAM_DIR / filename
        values = parse_defines(path)
        derived = compute(values)
        actual = {**values, **derived}
        for key, want in expected.items():
            got = actual[key]
            if got != want:
                raise AssertionError(f"{filename}: {key}={got}, expected {want}")
        if actual["TREE_BITS"] > 64:
            raise AssertionError(f"{filename}: TREE_BITS exceeds 64")
        print(
            f"{filename}: ok "
            f"(sig={actual['SPX_BYTES']}, tree_bits={actual['TREE_BITS']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
