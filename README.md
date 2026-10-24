<div align="center">
  <a href="https://benchtoplabs.vercel.app">
    <img src="https://benchtoplabs.vercel.app/icon.svg" width="120" alt="Benchtop Labs Logo" />
  </a>
  <h1>Benchtop Labs Registry</h1>
  <p><strong>The open verification registry and community submission intake for <a href="https://benchtoplabs.vercel.app">Benchtop Labs</a>.</strong></p>
  <p>Automated quality verification and diagnostic scorecards for modern open-source software.</p>

  <p>
    <a href="https://benchtoplabs.vercel.app"><strong>Live Directory</strong></a> •
    <a href="https://github.com/Ameya79/benchtoplabs-registry/issues/new?template=submit-project.yml"><strong>Submit Your Tool</strong></a> •
    <a href="https://benchtoplabs.vercel.app/showcase"><strong>Project Showcase</strong></a> •
    <a href="BENCH_SPEC.md"><strong>Bench Spec v1.0</strong></a>
  </p>

  <p>
    <a href="BENCH_SPEC.md"><img src="https://img.shields.io/badge/bench--spec-v1.0.0-FF6B14.svg" alt="Bench Spec" /></a>
    <a href="https://github.com/Ameya79/benchtoplabs-registry/issues/new?template=submit-project.yml"><img src="https://img.shields.io/badge/submissions-open-059669.svg" alt="Submissions Open" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
    <img src="https://img.shields.io/badge/checks-6%2F6%20automated-2ea44f.svg" alt="Automated Checks" />
  </p>
</div>

---

Benchtop Labs is an automated quality verification directory dedicated to curating high-craft, single-purpose open source tools. This repository hosts the public intake issue templates, the open-source **6-Point Bench Test Suite**, the canonical [Bench Test Specification](BENCH_SPEC.md), and verified project metadata.

---

## 🚀 How to Submit a Project

We welcome open-source tools across **Python (PyPI)**, **Node (npm)**, **Rust (Cargo)**, **Go Modules**, and **Desktop Binaries**.

1. **Submit via GitHub Issue**:  
   👉 [**Open a Submission Issue**](https://github.com/Ameya79/benchtoplabs-registry/issues/new?template=submit-project.yml)  
   *(Or fill out the web form at [benchtoplabs.vercel.app/submit](https://benchtoplabs.vercel.app/submit))*

2. **Automated Sandbox Verification**:  
   Our sandbox bot parses your repository, clones it in an isolated container, and evaluates it against our 6 automated checks. Within 60 seconds, the bot posts a complete **Verification Scorecard** table directly on your issue.

3. **Approval & Publication**:  
   Once all checks pass, a maintainer applies the `approved` label. Your project is automatically merged, assigned a dedicated spec page at `https://benchtoplabs.vercel.app/p/<your-slug>`, and listed in the [Public Directory](https://benchtoplabs.vercel.app/showcase).

---

## 🔬 The 6-Point Bench Suite (v1.0)

Every project on the bench is verified against 6 transparent criteria:

| ID | Check | Description |
|:---|:---|:---|
| `readme` | **Documentation** | A well-structured `README.md` explaining installation, intent, and usage. |
| `license` | **OSI License** | A recognized open-source license (`MIT`, `Apache-2.0`, `GPL-3.0`, `BSD`, etc.) in the repo root. |
| `release` | **Tagged Release** | At least one semantic version tag (e.g. `v1.0.0`) on GitHub releases. |
| `activity` | **Maintenance** | At least one commit to the default branch in the last 365 days. |
| `installs` | **Clean Sandbox Install** | Installs cleanly without errors in a virgin ephemeral environment. |
| `tests` | **CI Status** | Automated check-runs or CI workflows on default branch are 100% green. |

For full technical invariants, see the [Bench Test Specification v1.0](BENCH_SPEC.md).

---

## 💻 Running the Bench Locally

You can evaluate any project or test your own submission locally using the Python test suite:

```bash
# 1. Clone this repository
git clone https://github.com/Ameya79/benchtoplabs-registry.git
cd benchtoplabs-registry

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full verification suite against all projects
python bench/run.py
```

### Run Checks on a Specific Submission Body
```bash
python bench/check_submission.py --body "### GitHub Repository\nastral-sh/uv\n### Package Ecosystem\npypi"
```

---

## 📦 Directory Structure

```
benchtoplabs-registry/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── submit-project.yml     # Interactive GitHub Issue submission form
│   └── workflows/
│       ├── submission-check.yml   # Sandbox bot evaluator for incoming issues
│       └── approve-submission.yml # One-click maintainer approval workflow
├── bench/
│   ├── checks.py                  # Multi-ecosystem checks (pypi, npm, cargo, go, binary)
│   ├── check_submission.py        # Issue parser & scorecard markdown generator
│   ├── run.py                     # Local test runner for all projects
│   └── schema/                    # JSON schemas for projects and bench results
├── projects/                      # Verified project metadata manifests (<slug>.json)
├── bench_results/                 # Automated test scorecards (<slug>.json)
├── BENCH_SPEC.md                  # Canonical Bench Test Specification v1.0
├── LICENSE                        # Open source MIT license
└── README.md                      # Registry documentation & intake guide
```

---

## 🛡️ Security & Sandbox Isolation

The verification engine executes package evaluations under strict isolation:
- All package identifier names and install targets are validated against alphanumeric whitelists.
- Subprocess arguments are isolated via safe array passing and strict PEP 508 parsing.
- File lookups enforce path traversal guards (`isValidSlug`) and reject Windows device names.

---

## License

[MIT](LICENSE) © 2026 Benchtop Labs. Curated by [Ameya Kulkarni](https://github.com/Ameya79).