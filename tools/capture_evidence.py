#!/usr/bin/env python3
"""Refresh competition evidence logs with real command output."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"

COMMANDS = {
    "consistency.txt": [sys.executable, "tools/check_consistency.py"],
    "parameter-search.txt": [
        sys.executable,
        "tools/analyze_params.py",
        "--search",
        "--pareto",
    ],
    "smoke-test.txt": [
        sys.executable,
        "tools/clang_smoke_test.py",
        "--signatures",
        "1",
        "--message-bytes",
        "32",
    ],
    "performance-check.txt": [
        sys.executable,
        "tools/benchmark_params.py",
        "--iterations",
        "1",
        "--message-bytes",
        "32",
        "--no-write-doc",
    ],
}


def display_command(command: list[str]) -> str:
    parts = ["python" if part == sys.executable else part for part in command]
    return "$ " + " ".join(parts)


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    result = 0

    for filename, command in COMMANDS.items():
        print(f"capturing {filename}...", flush=True)
        proc = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        clean_output = "\n".join(line.rstrip() for line in proc.stdout.splitlines())
        content = (
            f"{display_command(command)}\n\n"
            f"{clean_output}\n\n"
            f"[exit code: {proc.returncode}]\n"
        )
        (EVIDENCE / filename).write_text(content, encoding="utf-8")
        result |= proc.returncode

    return 0 if result == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
