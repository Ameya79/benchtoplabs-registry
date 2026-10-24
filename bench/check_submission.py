"""
Parse a GitHub Issue submission, run the Benchtop Labs verification suite against it,
and generate a structured markdown report for the GitHub Action to comment back.
Conforms to Bench Test Specification v1.0.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

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

def parse_issue_body(body_text):
    """Parse structured fields from GitHub Issue Form body."""
    fields = {}
    current_key = None
    buffer = []

    for line in body_text.splitlines():
        header_match = re.match(r"^###\s+(.*)", line.strip())
        if header_match:
            if current_key:
                val = "\n".join(buffer).strip()
                if val and val != "_No response_":
                    fields[current_key] = val
            current_key = header_match.group(1).strip()
            buffer = []
        else:
            buffer.append(line)

    if current_key:
        val = "\n".join(buffer).strip()
        if val and val != "_No response_":
            fields[current_key] = val

    # Map header names to project attributes
    repo_raw = fields.get("GitHub Repository", "").strip()
    # Normalize repo format (handle full github.com URL or owner/repo)
    repo_match = re.search(r"github\.com/([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)", repo_raw)
    if repo_match:
        repo = repo_match.group(1)
    else:
        repo = repo_raw.replace("https://", "").replace("http://", "").strip("/").split("/")[-2:]
        repo = "/".join(repo) if len(repo) == 2 else repo_raw

    name = fields.get("Project Name", "").strip() or (repo.split("/")[-1] if "/" in repo else "Unnamed Project")
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        slug = re.sub(r"[^a-z0-9]+", "-", repo.replace("/", "-").lower()).strip("-")

    ecosystem = fields.get("Package Ecosystem", "other").strip().lower()
    package_name = fields.get("Package Name", "").strip() or None
    line = fields.get("One-Line Summary", "").strip()
    install_command = fields.get("Install Command", "").strip()
    website = fields.get("Website / Landing Page", "").strip()
    docs = fields.get("Documentation URL", "").strip()
    author_name = fields.get("Primary Author Name", "Community Contributor").strip()
    author_github = fields.get("Author GitHub Profile", "").strip()

    # Fallback URLs
    if not website:
        website = f"https://github.com/{repo}"
    if not docs:
        docs = website
    if not author_github:
        author_github = f"https://github.com/{repo.split('/')[0]}" if "/" in repo else "https://github.com"
    if not author_github.startswith("http"):
        author_github = f"https://github.com/{author_github.lstrip('@')}"

    # Package URL determination
    package_url = f"https://github.com/{repo}"
    if ecosystem == "pypi" and (package_name or slug):
        package_url = f"https://pypi.org/project/{package_name or slug}/"
        if not install_command:
            install_command = f"pip install {package_name or slug}"
    elif ecosystem == "npm" and (package_name or slug):
        package_url = f"https://www.npmjs.com/package/{package_name or slug}"
        if not install_command:
            install_command = f"npm install {package_name or slug}"
    elif ecosystem == "cargo" and (package_name or slug):
        package_url = f"https://crates.io/crates/{package_name or slug}"
        if not install_command:
            install_command = f"cargo install {package_name or slug}"
    elif ecosystem == "go":
        if not install_command:
            install_command = f"go install {package_name or f'github.com/{repo}@latest'}"

    # Logo determination:
    # 1. Custom logo URL from issue field
    # 2. Local file if present in public/projects/<slug>.png
    # 3. Automatic GitHub avatar fallback: https://github.com/<owner>.png
    owner = repo.split("/")[0] if "/" in repo else repo
    custom_logo = fields.get("Logo URL", "").strip()
    local_logo = ROOT_DIR / "public" / "projects" / f"{slug}.png"
    if custom_logo and custom_logo.startswith("http"):
        logo = custom_logo
    elif local_logo.exists():
        logo = f"/projects/{slug}.png"
    else:
        logo = f"https://github.com/{owner}.png"

    project = {
        "slug": slug,
        "ecosystem": ecosystem,
        "name": name,
        "line": line[:120] if line else f"Open-source {ecosystem} project.",
        "logo": logo,
        "website": website,
        "authors": [
            {
                "name": author_name,
                "github": author_github
            }
        ],
        "repo": repo,
        "packageName": package_name,
        "pypi": package_name if ecosystem == "pypi" else None,
        "module": None,
        "installer": None,
        "installCommand": install_command,
        "docs": docs,
        "package": package_url,
    }

    return project

def generate_markdown_report(project, checks, info, passed, total):
    """Generate GitHub comment markdown report."""
    is_passing = (passed == total and total > 0)
    badge_status = "PASSING" if is_passing else "NEEDS WORK"
    badge_color = "brightgreen" if is_passing else "red"

    rows = []
    for c in checks:
        if c["status"] == "pass":
            status_icon = "✅ **PASS**"
        elif c["status"] == "fail":
            status_icon = "❌ **FAIL**"
        else:
            status_icon = "⚪ *N/A*"
        val = c.get("value", "")
        rows.append(f"| {c['label']} | {status_icon} | `{val}` |")

    table = "\n".join(rows)

    comment = f"""## 🧪 Benchtop Labs Verification Report

**Project**: [{project['name']}]({project['website']}) (`{project['repo']}`)  
**Ecosystem**: `{project.get('ecosystem', 'other')}`  
**Verdict**: **{passed} of {total} checks passed** ({badge_status})  
**Bench Version**: `1.0.0` (Conforms to [BENCH_SPEC.md](https://github.com/Ameya79/benchtoplabs-registry/blob/main/BENCH_SPEC.md))

### Verification Results

| Check | Status | Details |
|:------|:------:|:--------|
{table}

### Metrics
- **Version**: `{info.get('version', 'N/A')}`
- **Release Date**: `{info.get('releaseDate', 'N/A')}`
- **Download Size**: `{info.get('size', 'N/A')}`
- **Dependencies**: `{info.get('dependencies', 0)}`
- **Last Commit**: `{info.get('lastCommit', 'N/A')}`

---

"""
    if is_passing:
        comment += f"""### 🎉 All Bench Checks Passed!
This project satisfies the **Bench Test Specification v1.0**.
A maintainer will review the submission. Once approved, the project will be added to the [Benchtop Labs Directory](https://benchtoplabs.com) automatically.

Maintainers: Label this issue with `approved` to merge and deploy.
"""
    else:
        comment += f"""### ⚠️ Some Checks Failed
To pass the bench, your project must address the failing checks above:
- Ensure your repository has an OSI-approved license.
- Ensure at least one tagged release or version tag exists.
- Ensure installation succeeds in a clean sandbox.
- Ensure your default branch CI workflows are passing.

Once resolved, leave a comment or re-run the workflow to re-verify.
"""

    return comment, is_passing

def main():
    body = os.environ.get("ISSUE_BODY", "")
    token = os.environ.get("GITHUB_TOKEN")

    if not body:
        print("Error: ISSUE_BODY environment variable is empty.", file=sys.stderr)
        sys.exit(1)

    project = parse_issue_body(body)
    repo = project["repo"]
    slug = project["slug"]

    print(f"Parsed submission: {project['name']} ({repo}) [ecosystem: {project.get('ecosystem')}]")

    checks = [
        check_readme(repo, token),
        check_license(repo, token),
        check_release(repo, token),
        check_activity(repo, token),
        check_installs(project, token),
        check_tests(repo, token),
    ]

    graded = [c for c in checks if c["status"] != "na"]
    passed = len([c for c in graded if c["status"] == "pass"])
    total = len(graded)
    info = get_project_info(project, token)

    bench_result = {
        "slug": slug,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "benchVersion": 1,
        "checks": checks,
        "info": info,
        "passed": passed,
        "total": total,
    }

    comment_body, is_passing = generate_markdown_report(project, checks, info, passed, total)

    # Write artifacts for GitHub Actions
    with open("submission_comment.md", "w", encoding="utf-8") as f:
        f.write(comment_body)

    with open("submission_project.json", "w", encoding="utf-8") as f:
        json.dump(project, f, indent=2)

    with open("submission_bench.json", "w", encoding="utf-8") as f:
        json.dump(bench_result, f, indent=2)

    # Set GITHUB_OUTPUT if present
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"slug={slug}\n")
            f.write(f"passed={'true' if is_passing else 'false'}\n")
            f.write(f"score={passed}/{total}\n")

    print(f"Bench result: {passed}/{total} passed. Written comment to submission_comment.md")
    print(comment_body)

if __name__ == "__main__":
    main()
