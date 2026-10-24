"""
Benchtop Labs test runner.
Scans content/projects, evaluates each project against the bench suite,
and outputs standardized bench results to content/bench/<slug>.json.
"""

import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from bench.checks import (
    check_readme,
    check_license,
    check_release,
    check_activity,
    check_installs,
    check_tests,
    get_project_info,
)

def run_bench():
    projects_dir = ROOT_DIR / "projects"
    if not projects_dir.exists():
        projects_dir = ROOT_DIR / "content" / "projects"

    bench_dir = ROOT_DIR / "bench_results"
    if not bench_dir.exists():
        bench_dir = ROOT_DIR / "content" / "bench"
    bench_dir.mkdir(parents=True, exist_ok=True)

    token = os.environ.get("GITHUB_TOKEN")
    project_files = sorted(projects_dir.glob("*.json"))

    print(f"=== Benchtop Labs Runner: evaluating {len(project_files)} projects ===")

    for p_path in project_files:
        with open(p_path, "r", encoding="utf-8") as f:
            project = json.load(f)

        slug = project["slug"]
        repo = project["repo"]
        name = project["name"]
        print(f"\nEvaluating [{name}] ({repo})...")

        checks = [
            check_readme(repo, token),
            check_license(repo, token),
            check_release(repo, token),
            check_activity(repo, token),
            check_installs(project, token),
            check_tests(repo, token),
        ]

        # Graded checks count (exclude 'na')
        graded = [c for c in checks if c["status"] != "na"]
        passed = len([c for c in graded if c["status"] == "pass"])
        total = len(graded)

        info = get_project_info(project, token)

        result = {
            "slug": slug,
            "checkedAt": datetime.now(timezone.utc).isoformat(),
            "benchVersion": 1,
            "checks": checks,
            "info": info,
            "passed": passed,
            "total": total,
        }

        out_path = bench_dir / f"{slug}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"  -> Result: {passed} of {total} passed. Written to {out_path.name}")
        for c in checks:
            mark = "PASS" if c["status"] == "pass" else ("FAIL" if c["status"] == "fail" else "NA")
            print(f"     [{mark:4s}] {c['label']}: {c.get('value', '')}")

    print("\n=== Bench run complete ===")

if __name__ == "__main__":
    run_bench()
