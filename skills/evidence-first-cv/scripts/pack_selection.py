#!/usr/bin/env python3
"""Rank any number of Packs from evidence-mapped responsibilities, not title tokens.

AI supplies the semantic requirement mapping. Scores diagnose that mapping; they do
not verify meaning, predict recruitment outcomes, or turn a JD into career evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml
from presentation_model import eligible_claims


def select_packs(registry, master, analysis, include_candidates=False):
    claims = eligible_claims(master)
    requirements = analysis.get("requirements", [])
    if not requirements:
        raise ValueError("parsed responsibilities and requirements are required")
    for row in requirements:
        if row.get("match") not in {"direct", "adjacent", "gap"}:
            raise ValueError("requirement needs direct/adjacent/gap assessment")
        if row.get("match") != "gap" and not row.get("claim_ids"):
            raise ValueError("a supported requirement needs eligible claims")
        if row.get("match") == "gap" and row.get("claim_ids"):
            raise ValueError("gap cannot carry supporting claims")
        if not set(row.get("claim_ids", [])) <= claims.keys():
            raise ValueError("requirement cites ineligible or unknown claims")
        if not row.get("reason"):
            raise ValueError("semantic mapping rationale is required")
    results = []
    for pid, pack in registry["packs"].items():
        if pack.get("status") != "approved" and not (include_candidates and pack.get("status") == "freeze-candidate"):
            continue
        roles = set(pack["role_families"])
        represented = set(pack.get("claim_ids", claims.keys()))
        score = 0
        direct = []
        gaps = []
        hard_gaps = []
        total = 0
        for row in requirements:
            weight = 5 if row.get("dominant") else (3 if row.get("priority") == "must" else 1)
            total += weight
            ids = [cid for cid in row.get("claim_ids", []) if cid in represented]
            in_lane = bool(roles & set(row.get("role_families", [])))
            depth_ok = any(claims[cid].get("interview_depth") in {"strong", "moderate"} for cid in ids)
            covered = row["match"] == "direct" and depth_ok and in_lane
            if covered:
                score += weight
                direct.extend(ids)
            elif row["match"] == "adjacent" and ids and in_lane:
                score += weight * 0.35
            else:
                gaps.append(row["text"])
            if row.get("priority") == "must" and not covered:
                hard_gaps.append({"text": row["text"], "blocking": bool(row.get("blocking"))})
        ratio = score / total
        fit = "Strong" if ratio >= .85 else "Good" if ratio >= .6 else "Stretch" if ratio >= .3 else "Weak"
        if hard_gaps and fit in {"Strong", "Good"}:
            fit = "Stretch"
        blocked = any(g["blocking"] for g in hard_gaps)
        if blocked:
            fit = "Weak"
        recommendation = "Defer" if blocked or fit == "Weak" else "Stretch" if hard_gaps or fit == "Stretch" else "Apply"
        results.append({"pack": pid, "status": pack["status"], "score": round(score, 2),
                        "maximum": total, "fit": fit, "recommendation": recommendation,
                        "supporting_claims": sorted(set(direct)), "gaps": gaps, "hard_gaps": hard_gaps})
    results.sort(key=lambda x: (x["recommendation"] != "Defer", x["score"]), reverse=True)
    return {"selected_pack": results[0]["pack"] if results else None,
            "results": results, "diagnostic_only": True,
            "notice": "Responsibility/evidence assessment, not an ATS percentage or hiring prediction."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("analysis", type=Path)
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--include-candidates", action="store_true", help="maintenance comparison only, never approval")
    a = p.parse_args()
    load = lambda path: yaml.safe_load(path.read_text())
    print(json.dumps(select_packs(load(a.root / "meta/golden_packs.yaml"), load(a.root / "meta/master_cv.yaml"),
                                 load(a.analysis), a.include_candidates), indent=2))


if __name__ == "__main__":
    main()
