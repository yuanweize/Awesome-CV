#!/usr/bin/env python3
"""Fail when private CV data, credentials, or unsafe generated files are tracked."""

from __future__ import annotations

import argparse
import ipaddress
import re
import subprocess
import sys
from pathlib import Path


PRIVATE_PATHS = (
    "config.tex",
    "letter_config.tex",
    "sections/",
    "profiles/",
    "baselines/",
    "archive/",
    "meta/",
    "build/",
    "tmp/",
)
PRIVATE_SUFFIXES = {".pdf", ".aux", ".log", ".out", ".synctex.gz", ".key", ".p12", ".pfx", ".pem"}
SECRET_FILENAMES = {".env", "targets.yaml", "targets.json", "credentials.json", "secrets.yaml", "secrets.yml"}

SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "GitLab token": re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    "OpenAI API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "npm token": re.compile(r"\bnpm_[A-Za-z0-9]{30,}\b"),
    "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    "generic bearer token": re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{16,}"),
    "non-example email": re.compile(r"\b[A-Z0-9._%+-]+@(?!example\.(?:com|org|net)\b)[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "international phone": re.compile(r"(?<!\w)\+[1-9][0-9 ()-]{7,}[0-9](?!\w)"),
}

# Exact public attribution retained from the upstream Awesome-CV source. Keep
# this narrow: it must never become a path-wide or pattern-wide PII bypass.
PUBLIC_ATTRIBUTION_EMAILS = {
    ("src/awesome-cv.cls", "posquit0.bj" + "@gmail.com"),
}
IP_PATTERN = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.ip_network(value)
    for value in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24", "127.0.0.0/8", "0.0.0.0/32")
)


def git_files(root: Path, staged: bool) -> list[str]:
    command = (
        ["git", "diff", "--cached", "--diff-filter=ACMR", "--name-only", "-z"]
        if staged
        else ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"]
    )
    result = subprocess.run(command, cwd=root, check=True, capture_output=True)
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def path_violations(paths: list[str]) -> list[str]:
    issues: list[str] = []
    for path in paths:
        if path in ("config.tex", "letter_config.tex") or any(
            path.startswith(prefix) for prefix in PRIVATE_PATHS if prefix.endswith("/")
        ):
            issues.append(f"private path is tracked: {path}")
        name = Path(path).name.lower()
        env_secret = name == ".env" or (name.startswith(".env.") and name != ".env.example")
        named_secret = (
            name in SECRET_FILENAMES
            or (name.startswith("credentials") and name.endswith(".json"))
            or (name.startswith("secrets") and name.endswith((".yaml", ".yml")))
        )
        if env_secret or named_secret:
            issues.append(f"credential/config filename is tracked: {path}")
        lowered = path.lower()
        if any(lowered.endswith(suffix) for suffix in PRIVATE_SUFFIXES):
            issues.append(f"generated or credential file is tracked: {path}")
    return issues


def is_documentation_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return True
    return any(address in network for network in DOCUMENTATION_NETWORKS)


def read_content(root: Path, relative: str, staged: bool) -> bytes:
    if staged:
        result = subprocess.run(
            ["git", "show", f":{relative}"],
            cwd=root,
            check=True,
            capture_output=True,
        )
        return result.stdout
    return (root / relative).read_bytes()


def content_violations(root: Path, paths: list[str], staged: bool = False) -> list[str]:
    issues: list[str] = []
    for relative in paths:
        path = root / relative
        if not staged and not path.is_file():
            continue
        try:
            raw = read_content(root, relative, staged)
            if b"\0" in raw:
                continue
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError, subprocess.CalledProcessError):
            continue

        for line_number, line in enumerate(text.splitlines(), 1):
            for label, pattern in SECRET_PATTERNS.items():
                match = pattern.search(line)
                if not match:
                    continue
                if label == "non-example email" and (
                    relative,
                    match.group(0).lower(),
                ) in PUBLIC_ATTRIBUTION_EMAILS:
                    continue
                issues.append(f"{relative}:{line_number}: possible {label} [value redacted]")
            for match in IP_PATTERN.finditer(line):
                value = match.group(0)
                if not is_documentation_ip(value):
                    issues.append(
                        f"{relative}:{line_number}: non-documentation IP address [value redacted]"
                    )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Check staged files instead of all tracked files")
    args = parser.parse_args()

    try:
        root_result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=Path.cwd(),
            check=True,
            capture_output=True,
            text=True,
        )
        root = Path(root_result.stdout.strip())
    except subprocess.CalledProcessError:
        print("ERROR: run the privacy check inside a Git repository", file=sys.stderr)
        return 2
    try:
        paths = git_files(root, args.staged)
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git file listing failed: {exc}", file=sys.stderr)
        return 2

    issues = path_violations(paths) + content_violations(root, paths, staged=args.staged)
    if issues:
        print("Privacy check failed:")
        for issue in issues:
            print(f"- {issue}")
        print("Remove the file from Git tracking, rotate exposed credentials, and rerun the check.")
        return 1

    scope = "staged" if args.staged else "tracked/untracked non-ignored"
    print(f"Privacy check passed: {len(paths)} {scope} files inspected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
