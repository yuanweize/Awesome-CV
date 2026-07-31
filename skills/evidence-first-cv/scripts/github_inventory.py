#!/usr/bin/env python3
"""Inventory public GitHub repositories and Actions without promoting CV claims."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import yaml


OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")


def find_project_root() -> Path:
    for candidate in [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def owner_from_master(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return ""
    if not isinstance(data, dict):
        return ""
    personal = data.get("personal_information", {})
    return personal.get("github", "") if isinstance(personal, dict) else ""


def gh_api(endpoint: str) -> Any:
    result = subprocess.run(
        ["gh", "api", endpoint],
        check=False,
        capture_output=True,
        text=True,
        timeout=45,
    )
    if result.returncode != 0:
        detail = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else "unknown error"
        raise RuntimeError(f"gh api failed for {endpoint}: {detail}")
    return json.loads(result.stdout)


def list_repositories(owner: str) -> list[dict[str, Any]]:
    repositories: list[dict[str, Any]] = []
    page = 1
    while True:
        payload = gh_api(
            f"users/{owner}/repos?type=owner&sort=updated&direction=desc&per_page=100&page={page}"
        )
        if not isinstance(payload, list):
            raise RuntimeError("GitHub repositories response was not a list")
        repositories.extend(item for item in payload if isinstance(item, dict))
        if len(payload) < 100:
            break
        page += 1
    return repositories


def workflow_inventory(owner: str, repository: str) -> tuple[list[dict[str, str]], str]:
    endpoint = f"repos/{owner}/{repository}/actions/workflows?per_page=100"
    try:
        payload = gh_api(endpoint)
    except RuntimeError as exc:
        return [], str(exc)
    workflows = payload.get("workflows", []) if isinstance(payload, dict) else []
    normalized = [
        {
            "name": str(item.get("name", "")),
            "path": str(item.get("path", "")),
            "state": str(item.get("state", "")),
            "kind": (
                "repository"
                if str(item.get("path", "")).startswith(".github/workflows/")
                else "github_managed"
            ),
        }
        for item in workflows
        if isinstance(item, dict)
    ]
    return sorted(normalized, key=lambda item: (item["path"], item["name"])), ""


def normalize_repository(item: dict[str, Any]) -> dict[str, Any]:
    license_data = item.get("license")
    license_name = license_data.get("spdx_id", "") if isinstance(license_data, dict) else ""
    return {
        "name": item.get("name", ""),
        "url": item.get("html_url", ""),
        "description": item.get("description") or "",
        "fork": bool(item.get("fork")),
        "archived": bool(item.get("archived")),
        "disabled": bool(item.get("disabled")),
        "visibility": item.get("visibility", "public"),
        "default_branch": item.get("default_branch", ""),
        "primary_language": item.get("language") or "",
        "stars": int(item.get("stargazers_count", 0) or 0),
        "forks": int(item.get("forks_count", 0) or 0),
        "open_issues": int(item.get("open_issues_count", 0) or 0),
        "size_kib": int(item.get("size", 0) or 0),
        "license": license_name,
        "created_at": item.get("created_at", ""),
        "updated_at": item.get("updated_at", ""),
        "pushed_at": item.get("pushed_at", ""),
        "topics": sorted(item.get("topics", [])) if isinstance(item.get("topics"), list) else [],
        "actions_workflows": [],
    }


def summarize_repositories(repositories: list[dict[str, Any]]) -> dict[str, Any]:
    originals = [item for item in repositories if not item.get("fork")]
    forks = [item for item in repositories if item.get("fork")]
    original_workflow_repositories = [item for item in originals if item.get("actions_workflows")]
    fork_workflow_repositories = [item for item in forks if item.get("actions_workflows")]
    original_active_workflows = [
        workflow
        for item in originals
        for workflow in item.get("actions_workflows", [])
        if workflow.get("state") == "active" and workflow.get("kind", "repository") == "repository"
    ]
    fork_active_workflows = [
        workflow
        for item in forks
        for workflow in item.get("actions_workflows", [])
        if workflow.get("state") == "active" and workflow.get("kind", "repository") == "repository"
    ]
    top_originals = sorted(
        originals,
        key=lambda item: (int(item.get("stars", 0)), int(item.get("forks", 0)), item.get("name", "")),
        reverse=True,
    )[:15]
    return {
        "repositories": len(repositories),
        "originals": len(originals),
        "forks": len(forks),
        "archived": sum(1 for item in repositories if item.get("archived")),
        "original_stars": sum(int(item.get("stars", 0)) for item in originals),
        "original_forks": sum(int(item.get("forks", 0)) for item in originals),
        "original_repositories_with_actions": sum(
            1
            for item in original_workflow_repositories
            if any(workflow.get("kind", "repository") == "repository" for workflow in item.get("actions_workflows", []))
        ),
        "original_active_actions_workflows": len(original_active_workflows),
        "original_github_managed_workflows": sum(
            1
            for item in originals
            for workflow in item.get("actions_workflows", [])
            if workflow.get("state") == "active" and workflow.get("kind") == "github_managed"
        ),
        "fork_repositories_with_actions": len(fork_workflow_repositories),
        "fork_active_actions_workflows": len(fork_active_workflows),
        "top_originals": [
            {
                "name": item.get("name", ""),
                "stars": int(item.get("stars", 0)),
                "forks": int(item.get("forks", 0)),
                "pushed_at": item.get("pushed_at", ""),
            }
            for item in top_originals
        ],
    }


def build_inventory(owner: str, workers: int = 8) -> dict[str, Any]:
    if not OWNER_PATTERN.fullmatch(owner):
        raise ValueError("owner must be a valid GitHub username")
    raw = list_repositories(owner)
    repositories = [normalize_repository(item) for item in raw]
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, min(workers, 16))) as pool:
        futures = {
            pool.submit(workflow_inventory, owner, str(item["name"])): item
            for item in repositories
            if not item["fork"]
        }
        for future in as_completed(futures):
            item = futures[future]
            workflows, error = future.result()
            item["actions_workflows"] = workflows
            if error:
                errors.append(f"{item['name']}: {error}")

    repositories.sort(key=lambda item: (item["fork"], item["name"].lower()))
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    inventory = {
        "schema_version": "1.0",
        "source": "GitHub public REST API via authenticated gh CLI",
        "owner": owner,
        "captured_at": captured_at,
        "policy": {
            "dynamic_metrics_are_snapshot_only": True,
            "forks_are_not_authorship_evidence": True,
            "actions_presence_is_not_professional_scope": True,
            "automatic_claim_promotion": False,
            "workflow_scan_scope": "original repositories only",
        },
        "repositories": repositories,
        "errors": sorted(errors),
    }
    inventory["summary"] = summarize_repositories(repositories)
    return inventory


def render_summary(inventory: dict[str, Any]) -> str:
    summary = inventory["summary"]
    lines = [
        f"GitHub inventory for {inventory['owner']} at {inventory['captured_at']}",
        f"Repositories: {summary['repositories']} ({summary['originals']} original, {summary['forks']} forks, {summary['archived']} archived)",
        f"Original-repository snapshot: {summary['original_stars']} stars, {summary['original_forks']} forks",
        f"Original GitHub Actions: {summary['original_repositories_with_actions']} repositories, {summary['original_active_actions_workflows']} active workflows",
        f"GitHub-managed dynamic workflows (excluded from authored-workflow counts): {summary['original_github_managed_workflows']}",
        "Top original repositories:",
    ]
    lines.extend(
        f"- {item['name']}: {item['stars']} stars, {item['forks']} forks, pushed {item['pushed_at'] or 'unknown'}"
        for item in summary["top_originals"]
    )
    if inventory.get("errors"):
        lines.append(f"Warnings: {len(inventory['errors'])} workflow endpoint(s) could not be read")
    lines.append("Policy: metrics are dated snapshots; nothing was promoted to a CV claim.")
    return "\n".join(lines)


def markdown_cell(value: Any) -> str:
    return str(value if value not in (None, "") else "-").replace("|", "\\|").replace("\n", " ")


def render_markdown(inventory: dict[str, Any], include_forks: bool = False) -> str:
    summary = inventory["summary"]
    lines = [
        "# Public GitHub portfolio inventory",
        "",
        f"- Owner: `{inventory['owner']}`",
        f"- Captured at: `{inventory['captured_at']}`",
        f"- Public repositories: {summary['repositories']} "
        f"({summary['originals']} original, {summary['forks']} forks)",
        f"- Original-repository stars/forks: {summary['original_stars']} / {summary['original_forks']}",
        f"- Original repositories with Actions: {summary['original_repositories_with_actions']}",
        f"- Active original-repository workflows: {summary['original_active_actions_workflows']}",
        "",
        "> Derived discovery inventory only. Repository presence and metrics do not prove",
        "> authorship, proficiency, production use, or interview depth.",
        "",
        "| Repository | Kind | Language | Stars | Forks | Last push | Actions |",
        "|---|---|---|---:|---:|---|---:|",
    ]
    for item in inventory["repositories"]:
        if item["fork"] and not include_forks:
            continue
        lines.append(
            "| [{name}]({url}) | {kind} | {language} | {stars} | {forks} | {pushed} | {actions} |".format(
                name=markdown_cell(item["name"]),
                url=item["url"],
                kind="fork" if item["fork"] else "original",
                language=markdown_cell(item["primary_language"]),
                stars=item["stars"],
                forks=item["forks"],
                pushed=markdown_cell(str(item["pushed_at"] or "")[:10]),
                actions=len(item["actions_workflows"]),
            )
        )
    action_items = [item for item in inventory["repositories"] if item["actions_workflows"]]
    lines.extend(["", "## GitHub Actions", ""])
    for item in action_items:
        lines.append(f"- **{item['name']}**")
        for workflow in item["actions_workflows"]:
            lines.append(f"  - `{workflow['path']}` - {workflow['name']} ({workflow['state']})")
    if inventory.get("errors"):
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in inventory["errors"])
    return "\n".join(lines) + "\n"


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", help="GitHub login; defaults to personal_information.github")
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--format", choices=("json", "markdown"))
    parser.add_argument("--include-forks", action="store_true")
    args = parser.parse_args()

    owner = args.owner or owner_from_master(args.master)
    if not owner:
        print("ERROR: provide --owner or set personal_information.github", file=sys.stderr)
        return 2
    if not shutil.which("gh"):
        print("ERROR: gh CLI is required", file=sys.stderr)
        return 2

    output = args.output or root / "meta" / "inventory" / "github" / f"{dt.date.today().isoformat()}.json"
    try:
        inventory = build_inventory(owner, workers=args.workers)
        output.parent.mkdir(parents=True, exist_ok=True)
        output_format = args.format or ("markdown" if output.suffix.lower() in {".md", ".markdown"} else "json")
        rendered = (
            render_markdown(inventory, include_forks=args.include_forks)
            if output_format == "markdown"
            else json.dumps(inventory, ensure_ascii=False, indent=2) + "\n"
        )
        output.write_text(rendered, encoding="utf-8")
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(render_summary(inventory))
    print(f"Private inventory: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
