# 🧪 Benchtop Labs Registry

> **The open verification registry and submission intake for [Benchtop Labs](https://benchtoplabs.com).**

[![Bench Spec v1.0](https://img.shields.io/badge/bench--spec-v1.0.0-FF6B14.svg)](BENCH_SPEC.md)
[![Submissions Open](https://img.shields.io/badge/submissions-open-059669.svg)](https://github.com/Ameya79/benchtoplabs-registry/issues/new?template=submit-project.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Benchtop Labs is an automated quality verification directory dedicated to curating high-craft, single-purpose open source tools. This repository hosts the public intake issue templates, the open-source **6-Point Bench Test Suite**, the canonical [Bench Test Specification](BENCH_SPEC.md), and verified project metadata.

---

## 🚀 How to Submit a Project

We welcome open-source tools across **Python (PyPI)**, **Node (npm)**, **Rust (Cargo)**, **Go Modules**, and **Desktop Binaries**.

1. **Submit via GitHub Issue**:  
   👉 [**Open a Submission Issue**](https://github.com/Ameya79/benchtoplabs-registry/issues/new?template=submit-project.yml)  
   *(Or fill out the web form at [benchtoplabs.com/submit](https://benchtoplabs.com/submit))*

2. **Automated Verification**:  
   Our sandbox bot parses your repository, clones it in an isolated container, and evaluates it against our 6 automated checks. Within 60 seconds, the bot posts a complete **Verification Scorecard** table directly on your issue.

3. **Approval & Publication**:  
   Once all checks pass, a maintainer applies the `approved` label. Your project is automatically merged, assigned a dedicated spec page at `https://benchtoplabs.com/p/<your-slug>`, and listed in the [Public Directory](https://benchtoplabs.com/showcase).

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

# 4. Or test a specific submission payload
python bench/check_submission.py
```

> **Tip**: Set `export GITHUB_TOKEN=your_token` to avoid GitHub API rate limits.

---

## 📁 Repository Structure

```
benchtoplabs-registry/
├── .github/
│   └── ISSUE_TEMPLATE/
│       └── submit-project.yml       # Community submission issue form
├── bench/
│   ├── checks.py                    # Core 6-point verification implementations
│   ├── check_submission.py          # Automated issue parser and comment generator
│   ├── run.py                       # Batch test runner
│   └── schema/                      # JSON schemas for projects and bench results
├── projects/                        # Verified project metadata (JSON)
├── bench_results/                   # Test execution results (JSON)
├── BENCH_SPEC.md                    # Formal Bench Test Specification v1.0
├── LICENSE                          # MIT License
└── README.md
```

---

## 🌐 Community & Links

- **Website**: [benchtoplabs.com](https://benchtoplabs.com)
- **Directory Showcase**: [benchtoplabs.com/showcase](https://benchtoplabs.com/showcase)
- **Founder**: [Ameya Kulkarni](https://github.com/Ameya79)
- **License**: [MIT](LICENSE)