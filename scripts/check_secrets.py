from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


PATTERNS = [
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "Private key block",
        re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"),
    ),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "Credentialed URL",
        re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s@]+@[^\s]+", re.IGNORECASE),
    ),
    (
        "Generic secret assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password|client[_-]?secret)\b\s*[:=]\s*['\"]?(?!your_|example|placeholder|changeme|dummy|test|<)[A-Za-z0-9_\-+/=]{16,}"
        ),
    ),
]


def staged_files() -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMRTUXB",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def file_content(path: str) -> str:
    result = subprocess.run(
        ["git", "show", f":{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def main() -> int:
    findings: list[str] = []

    for relative_path in staged_files():
        if relative_path.startswith(".githooks/"):
            continue

        try:
            content = file_content(relative_path)
        except subprocess.CalledProcessError:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            for label, pattern in PATTERNS:
                if pattern.search(line):
                    findings.append(
                        f"{relative_path}:{line_number}: {label} pattern matched"
                    )

    if findings:
        print("Potential secrets detected in staged changes:", file=sys.stderr)
        for finding in findings:
            print(f"  - {finding}", file=sys.stderr)
        return 1

    print("No obvious secrets detected in staged changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())