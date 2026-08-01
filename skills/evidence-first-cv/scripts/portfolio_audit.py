#!/usr/bin/env python3
"""Compare a GitHub inventory with the governed portfolio in a master CV."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import yaml


PORTFOLIO_TIERS = {"primary", "supporting", "catalog"}


def find_project_root() -> Path:
    candidates = [Path.cwd(), *Path.cwd().parents, Path(__file__).resolve(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if candidate.is_file():
            candidate = candidate.parent
        if (candidate / "templates" / "master_cv.yaml.example").is_file():
            return candidate
    return Path.cwd()


def normalize_repo_url(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    parsed = urlsplit(value.strip())
    path = parsed.path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path.lower(), "", ""))


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read master YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("master YAML root must be a mapping")
    return data


def load_inventory(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read GitHub inventory {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("repositories"), list):
        raise ValueError("GitHub inventory must contain a repositories list")
    return data


def latest_inventory(root: Path) -> Path:
    inventory_dir = root / "meta" / "inventory" / "github"
    candidates = sorted(inventory_dir.glob("*.json"), reverse=True)
    if not candidates:
        raise ValueError("no GitHub JSON inventory found; run ./cv github-audit first")
    return candidates[0]


def _index_unique(items: list[dict[str, Any]], field: str, label: str) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for item in items:
        key = normalize_repo_url(item.get(field))
        if not key:
            continue
        if key in indexed:
            raise ValueError(f"duplicate {label} repository URL: {item.get(field)}")
        indexed[key] = item
    return indexed


def audit_portfolio(master: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    projects = [item for item in master.get("open_source_and_projects", []) if isinstance(item, dict)]
    management = master.get("portfolio_management", {})
    if not isinstance(management, dict):
        raise ValueError("portfolio_management must be a mapping")
    exclusions = [
        item for item in management.get("excluded_repositories", []) if isinstance(item, dict)
    ]
    project_by_url = _index_unique(projects, "repo", "catalogued")
    exclusion_by_url = _index_unique(exclusions, "repo", "excluded")

    evidence_by_url: dict[str, list[str]] = {}
    for evidence in master.get("evidence_registry", []):
        if not isinstance(evidence, dict):
            continue
        url = normalize_repo_url(evidence.get("locator"))
        if url:
            evidence_by_url.setdefault(url, []).append(str(evidence.get("id", "")))

    categories: dict[str, list[dict[str, Any]]] = {
        "claimed": [],
        "catalogued": [],
        "evidence_only": [],
        "missing": [],
        "risk_excluded": [],
    }
    metadata_gaps: list[dict[str, Any]] = []
    inventory_urls: set[str] = set()
    inventory_all_urls: set[str] = set()

    for repository in inventory["repositories"]:
        if not isinstance(repository, dict):
            continue
        url = normalize_repo_url(repository.get("url"))
        if not url:
            continue
        inventory_all_urls.add(url)
        is_fork = bool(repository.get("fork"))
        # Forks are not automatic coverage obligations, but a governed fork still
        # deserves a visible catalog entry with its attribution boundary intact.
        if is_fork and url not in project_by_url and url not in exclusion_by_url and url not in evidence_by_url:
            continue
        inventory_urls.add(url)
        summary = {
            "name": str(repository.get("name", "")),
            "repo": str(repository.get("url", "")),
            "stars": int(repository.get("stars", 0) or 0),
            "forks": int(repository.get("forks", 0) or 0),
            "pushed_at": str(repository.get("pushed_at", "")),
        }
        if url in project_by_url and url in exclusion_by_url:
            raise ValueError(f"repository is both catalogued and excluded: {summary['repo']}")
        if url in exclusion_by_url:
            item = dict(summary)
            item["reason"] = str(exclusion_by_url[url].get("reason", ""))
            categories["risk_excluded"].append(item)
            continue
        if url in project_by_url:
            project = project_by_url[url]
            item = dict(summary)
            item["portfolio_tier"] = project.get("portfolio_tier", "")
            item["claim_ids"] = project.get("claim_ids", [])
            category = "claimed" if project.get("claim_ids") else "catalogued"
            categories[category].append(item)
            missing_fields = [
                field
                for field in ("portfolio_tier", "evidence_ids", "last_reviewed")
                if not project.get(field)
            ]
            if project.get("portfolio_tier") not in PORTFOLIO_TIERS:
                if "portfolio_tier" not in missing_fields:
                    missing_fields.append("portfolio_tier")
            if missing_fields:
                metadata_gaps.append({"name": summary["name"], "missing": sorted(missing_fields)})
            continue
        if url in evidence_by_url:
            item = dict(summary)
            item["evidence_ids"] = evidence_by_url[url]
            categories["evidence_only"].append(item)
            continue
        if not is_fork:
            categories["missing"].append(summary)

    stale_catalog = sorted(
        str(item.get("name", item.get("repo", "")))
        for url, item in project_by_url.items()
        if url not in inventory_all_urls and "github.com" in url
    )
    stale_exclusions = sorted(
        str(item.get("repo", ""))
        for url, item in exclusion_by_url.items()
        if url not in inventory_urls
    )
    for values in categories.values():
        values.sort(key=lambda item: item["name"].lower())
    return {
        "schema_version": "1.0",
        "owner": inventory.get("owner", ""),
        "inventory_captured_at": inventory.get("captured_at", ""),
        "portfolio_last_reviewed": management.get("last_reviewed", ""),
        "summary": {key: len(value) for key, value in categories.items()},
        "categories": categories,
        "metadata_gaps": metadata_gaps,
        "stale_catalog": stale_catalog,
        "stale_exclusions": stale_exclusions,
        "policy": {
            "automatic_claim_promotion": False,
            "forks_reviewed": False,
            "dynamic_metrics_are_snapshot_only": True,
        },
    }


def render_text(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        f"Portfolio audit for {result['owner'] or 'unknown owner'}",
        f"Inventory: {result['inventory_captured_at'] or 'unknown'}; portfolio review: {result['portfolio_last_reviewed'] or 'missing'}",
        "Coverage: " + ", ".join(f"{key}={summary[key]}" for key in ("claimed", "catalogued", "evidence_only", "missing", "risk_excluded")),
    ]
    for category in ("missing", "evidence_only", "risk_excluded"):
        values = result["categories"][category]
        if values:
            lines.append(f"{category.replace('_', ' ').title()}:")
            lines.extend(f"- {item['name']}: {item.get('reason') or item['repo']}" for item in values)
    if result["metadata_gaps"]:
        lines.append("Metadata gaps:")
        lines.extend(
            f"- {item['name']}: {', '.join(item['missing'])}" for item in result["metadata_gaps"]
        )
    if result["stale_catalog"]:
        lines.append("Catalogued GitHub projects absent from this original-repository inventory:")
        lines.extend(f"- {name}" for name in result["stale_catalog"])
    if result["stale_exclusions"]:
        lines.append("Stale exclusions:")
        lines.extend(f"- {url}" for url in result["stale_exclusions"])
    lines.append("Policy: discovery only; no repository or metric was promoted to a CV claim.")
    return "\n".join(lines)


def main() -> int:
    root = find_project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, default=root / "meta" / "master_cv.yaml")
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true", help="Fail on missing repositories or metadata gaps")
    args = parser.parse_args()
    try:
        inventory_path = args.inventory or latest_inventory(root)
        result = audit_portfolio(load_yaml(args.master), load_inventory(inventory_path))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.as_json else render_text(result))
    failed = bool(result["categories"]["missing"] or result["metadata_gaps"])
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
