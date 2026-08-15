#!/usr/bin/env python3
"""Audit the stable repository layout, privacy boundary, and visible workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from workspace_init import SECTION_TEMPLATE_NAMES, TEMPLATE_FILES, find_project_root


PUBLIC_PATHS = (
    ".github/workflows",
    "docs",
    "integrations/dify",
    "skills/evidence-first-cv",
    "src",
    "templates",
    "tests",
    "tools",
    "Makefile",
    "README.md",
    "cv",
)

PRIVATE_IGNORE_RULES = (
    "/archive/",
    "/meta/",
    "/output/",
    "/workspace/",
)

# The runtime tree is organized physically, so the shared editor configuration
# must not hide it as a substitute for structure.
VISIBLE_PATHS = (
    "archive",
    "meta",
    "output",
    "output/pdf",
    "workspace",
    "workspace/current",
    "workspace/profiles",
    "workspace/baselines",
    "workspace/build",
    "workspace/tmp",
)

HUMAN_SURFACE = (
    "README.md",
    "meta/master_cv.yaml",
    "meta/applications",
    "output/pdf/README.md",
    "workspace/current/sections",
    "workspace/profiles",
    "cv",
)


def _read_noncomment_lines(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def git_ignored_paths(root: Path, paths: list[str]) -> list[str]:
    """Return public paths hidden by repository or local Git ignore rules."""
    if not (root / ".git").exists():
        return []
    ignored: list[str] = []
    for relative in paths:
        result = subprocess.run(
            ["git", "check-ignore", "-q", "--no-index", "--", relative],
            cwd=root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if result.returncode == 0:
            ignored.append(relative)
    return ignored


def audit_workspace(root: Path) -> dict[str, Any]:
    """Return deterministic structure, privacy, and visibility diagnostics."""
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    for relative in PUBLIC_PATHS:
        if not (root / relative).exists():
            errors.append(f"required public path is missing: {relative}")

    required_templates = [source for source, _ in TEMPLATE_FILES]
    required_templates.extend(
        f"templates/sections/{name}" for name in SECTION_TEMPLATE_NAMES
    )
    for relative in required_templates:
        if not (root / relative).is_file():
            errors.append(f"initializer source is missing: {relative}")

    try:
        ignored_public = git_ignored_paths(
            root, [*required_templates, ".vscode/settings.json"]
        )
    except OSError as exc:
        warnings.append(f"could not inspect Git ignore precedence: {exc}")
    else:
        for relative in ignored_public:
            errors.append(f"public initializer/view path is hidden by Git ignore rules: {relative}")

    ignore_path = root / ".gitignore"
    if not ignore_path.is_file():
        errors.append(".gitignore is missing")
    else:
        ignore_rules = _read_noncomment_lines(ignore_path)
        for rule in PRIVATE_IGNORE_RULES:
            if rule not in ignore_rules:
                errors.append(f"private path is not protected by .gitignore: {rule}")
        if "!.vscode/settings.json" not in ignore_rules:
            errors.append("the shared VS Code settings file is not explicitly tracked")

    settings_path = root / ".vscode" / "settings.json"
    excludes: dict[str, Any] = {}
    if not settings_path.is_file():
        errors.append("shared VS Code settings are missing: .vscode/settings.json")
    else:
        try:
            settings = json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid .vscode/settings.json: {exc}")
        else:
            for setting_name in (
                "files.exclude",
                "search.exclude",
                "files.watcherExclude",
            ):
                candidate = settings.get(setting_name, {})
                if not isinstance(candidate, dict):
                    errors.append(f"{setting_name} must be a JSON object")
                    continue
                if candidate:
                    errors.append(
                        f"{setting_name} must be empty; organize repository paths instead of hiding them"
                    )
                if setting_name == "files.exclude":
                    excludes = candidate

    # This is informational rather than an error: ignored runtime paths are
    # created on first use, so a pristine public clone need not contain them.
    missing_human_runtime = [
        path
        for path in ("meta/master_cv.yaml", "workspace/current/sections")
        if not (root / path).exists()
    ]
    if missing_human_runtime:
        warnings.append(
            "private workspace is not initialized; run './cv init': "
            + ", ".join(missing_human_runtime)
        )

    return {
        "schema_version": "1.0",
        "root": str(root),
        "ok": not errors,
        "human_surface": list(HUMAN_SURFACE),
        "public_product": list(PUBLIC_PATHS),
        "visible_runtime": list(VISIBLE_PATHS),
        "errors": errors,
        "warnings": warnings,
    }


def render_text(report: dict[str, Any]) -> str:
    status = "PASS" if report["ok"] else "FAIL"
    lines = [f"Workspace structure: {status}", ""]
    lines.append("Primary work surface:")
    lines.extend(f"  - {path}" for path in report["human_surface"])
    lines.append("")
    lines.append("Runtime paths visible in VS Code:")
    lines.extend(f"  - {path}" for path in report["visible_runtime"])
    if report["warnings"]:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"  - {item}" for item in report["warnings"])
    if report["errors"]:
        lines.append("")
        lines.append("Errors:")
        lines.extend(f"  - {item}" for item in report["errors"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit Awesome-CV paths, privacy ignores, templates, and runtime visibility."
    )
    parser.add_argument("--root", type=Path, help="Repository root; auto-detected by default")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when the contract fails")
    args = parser.parse_args()

    try:
        root = args.root.resolve() if args.root else find_project_root()
        report = audit_workspace(root)
    except (OSError, ValueError) as exc:
        print(f"Structure audit failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(report, indent=2) if args.json else render_text(report))
    return 2 if args.strict and not report["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
