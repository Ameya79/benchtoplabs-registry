# Bench Test Specification

**Status**: Active  
**Version**: 1.0.0  
**Last Updated**: 2026-10-24  
**Maintainer**: Benchtop Labs ([benchtoplabs.com](https://benchtoplabs.com))  
**License**: CC BY 4.0  
**Canonical URL**: [https://benchtoplabs.com/about](https://benchtoplabs.com/about)

---

## Abstract

The Bench Test Specification defines a reproducible, automated verification framework for evaluating the health, quality, and installability of open-source software projects. It is ecosystem-agnostic — the same six checks apply to a Python library, an npm package, a Rust crate, a Go module, or a desktop binary distributed via GitHub Releases.

A project **passes** the bench test when zero graded checks have a status of `fail`. A passing bench result certifies that the project is documented, licensed, tagged, maintained, installable, and self-tested. It does not certify code quality, security, or fitness for a specific use case.

---

## 1. Terminology

| Term | Definition |
|:-----|:-----------|
| **Check** | A single evaluation criterion that produces one of three outcomes: `pass`, `fail`, or `na`. |
| **Graded Check** | A check whose outcome contributes to the overall pass/fail verdict. Checks with status `na` are excluded from grading. |
| **Bench Run** | A complete, sequential execution of all checks against one project at a specific point in time. |
| **Bench Result** | The structured JSON output of a bench run, conforming to the schema in Section 5. |
| **Bench Pass** | A project whose bench result contains zero graded checks with status `fail`. |
| **Bench Version** | An integer (`benchVersion`) indicating which version of this specification was used. The current version is `1`. |
| **Ecosystem** | The package distribution system for the project (e.g., PyPI, npm, crates.io, Go modules, GitHub Releases). |
| **Slug** | A unique, URL-safe identifier for a project, matching the pattern `^[a-z0-9-]+$`. |

---

## 2. Checks (v1.0)

All checks are executed in order. Each check produces a JSON object with the fields `id`, `label`, `status`, and an optional `value`. The `value` field carries human-readable detail (e.g., the license SPDX identifier, the tag name, or the number of days since last commit).

### 2.1 README Documentation

| Field | Value |
|:------|:------|
| **ID** | `readme` |
| **Label** | README |
| **Graded** | Yes |
| **Method** | Query the GitHub API for the repository's README endpoint (`GET /repos/{owner}/{repo}/readme`). A `200` response indicates presence. |
| **Pass condition** | The repository contains a README file. |
| **Fail condition** | The README endpoint returns a non-200 status. |

### 2.2 OSI-Approved License

| Field | Value |
|:------|:------|
| **ID** | `license` |
| **Label** | License |
| **Graded** | Yes |
| **Method** | Query the GitHub API license endpoint (`GET /repos/{owner}/{repo}/license`). Extract the `license.spdx_id` or `license.name`. |
| **Pass condition** | A recognized license object is returned with a non-null SPDX identifier. |
| **Fail condition** | No license is detected, or the license is not recognized. |
| **Value** | The SPDX identifier (e.g., `MIT`, `Apache-2.0`, `BSD-3-Clause`). |

### 2.3 Tagged Semantic Release

| Field | Value |
|:------|:------|
| **ID** | `release` |
| **Label** | Tagged release |
| **Graded** | Yes |
| **Method** | Query the GitHub API for the latest release (`GET /repos/{owner}/{repo}/releases/latest`), then all releases, then tags. A version tag on any of these endpoints satisfies the check. |
| **Pass condition** | At least one release or tag with a version identifier exists. |
| **Fail condition** | No releases or tags are found. |
| **Value** | The tag name (e.g., `v1.0.1`). |

### 2.4 Active Maintenance (365-Day Commit Window)

| Field | Value |
|:------|:------|
| **ID** | `activity` |
| **Label** | Last commit |
| **Graded** | Yes |
| **Method** | Query the most recent commit on the default branch (`GET /repos/{owner}/{repo}/commits?per_page=1`). Calculate the number of days between the commit date and the current UTC time. |
| **Pass condition** | The most recent commit occurred within the last 365 days. |
| **Fail condition** | The most recent commit is older than 365 days, or no commits exist. |
| **Value** | Human-readable age (e.g., `12d ago`, `Today`). |

### 2.5 Clean Installation Sandbox

| Field | Value |
|:------|:------|
| **ID** | `installs` |
| **Label** | Installs clean |
| **Graded** | Yes |
| **Method** | Varies by ecosystem (see Section 3). The install is performed in an isolated, ephemeral environment. |
| **Pass condition** | The package installs without errors and (where applicable) imports or executes successfully. |
| **Fail condition** | Installation or import fails. |
| **N/A condition** | No supported ecosystem adapter exists for the project. |
| **Value** | Ecosystem-specific detail (e.g., `pip install & import ok`, `npm install ok`). |

### 2.6 Automated Test Suite

| Field | Value |
|:------|:------|
| **ID** | `tests` |
| **Label** | Tests pass |
| **Graded** | Yes |
| **Method** | Query the GitHub check runs and combined commit status for the latest commit on the default branch. |
| **Pass condition** | All check runs have conclusions of `success`, `neutral`, or `skipped`; or the combined status is `success`. |
| **Fail condition** | Any check run has a conclusion of `failure`, `timed_out`, or `action_required`. |
| **N/A condition** | No CI workflows or check runs exist for the repository. |
| **Value** | `Green`, `Failed`, or `Pending`. |

### 2.7 Info Metrics (Non-Graded)

These metrics are collected for informational purposes and never cause a project to fail.

| Metric | Source |
|:-------|:-------|
| `version` | Latest version from the package registry or release tag. |
| `releaseDate` | Publication date of the latest release or package version. |
| `size` | Download size of the wheel, tarball, installer, or binary. |
| `dependencies` | Count of runtime dependencies (excluding dev/optional). |
| `lastCommit` | Date of the most recent commit on the default branch. |

---

## 3. Ecosystem Adapters

Each ecosystem has a specific installation verification method. Adapters are pluggable — new ecosystems can be added without modifying the core check framework.

### 3.1 Python (PyPI)

1. Query the PyPI JSON API (`GET https://pypi.org/pypi/{package}/json`).
2. Create a temporary virtual environment (`python -m venv`).
3. Install the package (`pip install {package}`).
4. Import the module (`python -c "import {module}"`).
5. Pass if both install and import succeed with exit code 0.

### 3.2 JavaScript / TypeScript (npm)

1. Query the npm registry (`GET https://registry.npmjs.org/{package}`).
2. Create a temporary directory.
3. Initialize a minimal `package.json`.
4. Install the package (`npm install {package}`).
5. Require the module (`node -e "require('{package}')"`).
6. Pass if both install and require succeed with exit code 0.

### 3.3 Rust (crates.io)

1. Query the crates.io API (`GET https://crates.io/api/v1/crates/{crate}`).
2. Create a temporary directory as CARGO_HOME.
3. If the crate provides a binary: `cargo install {crate} --root {tmpdir}`. Pass if the binary exists.
4. If library-only: `cargo add {crate}` in a temp project and `cargo check`. Pass if check succeeds.

### 3.4 Go (Go Modules)

1. Verify the module path resolves (`go list -m {module}@latest`).
2. If the module provides a binary: `GOBIN={tmpdir} go install {module}@latest`. Pass if the binary exists.
3. If library-only: create a temp Go file with `import _ "{module}"` and run `go build`. Pass if build succeeds.

### 3.5 Desktop Binaries (GitHub Release Assets)

1. Query the latest GitHub Release for the repository.
2. Search release assets for files matching the `installer` glob pattern (e.g., `*.exe`, `*.dmg`, `*.AppImage`).
3. Pass if at least one matching asset exists with a file size greater than zero bytes.
4. The installer is **not** executed — only its presence and non-zero size are verified.

---

## 4. Scoring

```
graded_checks = [c for c in checks if c.status != "na"]
passed = count(c for c in graded_checks if c.status == "pass")
total  = count(graded_checks)

bench_pass = (passed == total)
```

A project achieves a **Bench Pass** when `passed == total` — that is, every graded check has status `pass`. There are no partial scores, tiers, or rankings. A project either passes or it does not.

---

## 5. Result Schema

Every bench run produces a JSON document conforming to this structure. The formal JSON Schema is provided in [`bench/schema/bench-result.schema.json`](bench/schema/bench-result.schema.json).

```json
{
  "slug": "example-project",
  "checkedAt": "2026-10-24T00:00:00+00:00",
  "benchVersion": 1,
  "checks": [
    {
      "id": "readme",
      "label": "README",
      "status": "pass",
      "value": "Present"
    },
    {
      "id": "license",
      "label": "License",
      "status": "pass",
      "value": "MIT"
    },
    {
      "id": "release",
      "label": "Tagged release",
      "status": "pass",
      "value": "v1.2.0"
    },
    {
      "id": "activity",
      "label": "Last commit",
      "status": "pass",
      "value": "5d ago"
    },
    {
      "id": "installs",
      "label": "Installs clean",
      "status": "pass",
      "value": "pip install & import ok"
    },
    {
      "id": "tests",
      "label": "Tests pass",
      "status": "pass",
      "value": "Green"
    }
  ],
  "info": {
    "version": "1.2.0",
    "releaseDate": "2026-10-20",
    "size": "42.5 KB",
    "dependencies": 3,
    "lastCommit": "2026-10-19"
  },
  "passed": 6,
  "total": 6
}
```

---

## 6. Submission Schema

Projects submitted for bench verification must provide a JSON document conforming to the schema in [`bench/schema/project-submission.schema.json`](bench/schema/project-submission.schema.json).

Required fields:

| Field | Type | Description |
|:------|:-----|:------------|
| `slug` | string | URL-safe identifier (`^[a-z0-9-]+$`) |
| `name` | string | Human-readable project name |
| `line` | string | One-line description (max 120 characters) |
| `repo` | string | GitHub repository in `owner/repo` format |
| `ecosystem` | enum | One of: `pypi`, `npm`, `cargo`, `go`, `binary`, `other` |

Optional fields: `packageName`, `module`, `installCommand`, `installer`, `website`, `docs`.

---

## 7. Versioning Policy

- The bench version is an integer that increments when the check definitions change in a way that could alter results for existing projects.
- Adding a new non-graded info metric does not increment the version.
- Adding a new graded check increments the version.
- Changing the pass/fail logic of an existing check increments the version.
- Adding a new ecosystem adapter does not increment the version.
- All bench results include the `benchVersion` field so consumers can filter by specification version.

---

## 8. Conformance

A bench test implementation is **conformant** with this specification if:

1. It executes all six graded checks defined in Section 2.
2. Each check produces a result with the exact `id` values specified.
3. The `status` field is one of the three allowed values: `pass`, `fail`, `na`.
4. The scoring formula in Section 4 is applied without modification.
5. The output conforms to the JSON schema in Section 5.
6. Installation checks (Section 2.5) run in an isolated, ephemeral environment that is destroyed after the check completes.

---

## 9. References

- **Benchtop Labs**: [https://benchtoplabs.com](https://benchtoplabs.com)
- **Source Repository**: [https://github.com/Ameya79/benchtoplabs-registry](https://github.com/Ameya79/benchtoplabs-registry)
- **GitHub API**: [https://docs.github.com/en/rest](https://docs.github.com/en/rest)
- **PyPI JSON API**: [https://warehouse.pypa.io/api-reference/json.html](https://warehouse.pypa.io/api-reference/json.html)
- **npm Registry API**: [https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md](https://github.com/npm/registry/blob/main/docs/REGISTRY-API.md)
- **crates.io API**: [https://crates.io/policies](https://crates.io/policies)
