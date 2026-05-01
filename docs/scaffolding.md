# Scaffolded Project Structure

This page documents the complete file tree that `pyrig init` produces when run
inside a fresh project directory. The example below was generated from a project
named **`my-project`**

## Quick Start Recap

```bash
uv init my-project
cd my-project
uv add pyrig
uv run pyrig init
```

## Generated File Tree

Each file is fully configured and ready to use, with sensible defaults that
follow best practices.

```text
my-project/
├── .env                                    # Environment variables template
├── .gitignore                              # Git ignore rules, fully configured
├── .python-version                         # Python version pin (e.g. 3.13)
├── .scratch.py                             # Scratch file for code experimentation
├── branch-protection.json                  # GitHub branch protection ruleset definition
├── CODE_OF_CONDUCT.md                      # Contributor Covenant code of conduct
├── Containerfile                           # Podman container image definition
├── CONTRIBUTING.md                         # Contribution guidelines
├── LICENSE                                 # MIT license
├── mkdocs.yml                              # MkDocs documentation site configuration
├── prek.toml                               # Pre-commit hook definitions
├── pyproject.toml                          # Package metadata, configuration, etc.
├── README.md                               # Project README
├── SECURITY.md                             # Security policy
├── uv.lock                                 # Locked dependency manifest
│
├── .github/
│   ├── pull_request_template.md            # Pull request description template
│   └── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml                  # Bug report issue form
│   │   ├── config.yml                      # Issue template chooser configuration
│   │   └── feature_request.yml             # Feature request issue form
│   └── workflows/
│       ├── health_check.yml                # CI: runs tests and more
│       ├── build.yml                       # CI: triggered after health check passes
│       ├── release.yml                     # CI: triggered after build passes
│       └── deploy.yml                      # CI: triggered after release passes
│
├── docs/
│   ├── api.md                              # API reference page (mkdocstrings)
│   └── index.md                            # Documentation home page
│
├── src/
│   └── my_pr/                              # Package root (project name → snake_case)
│       ├── __init__.py                     # Top-level package module
│       └── py.typed                        # PEP 561 marker (typed package)
│
└── tests/
    ├── __init__.py                         # Tests package init
    ├── conftest.py                         # Pytest plugin registration for pyrig
    └── test_zero.py                        # Placeholder test for pyrig
```

## File Descriptions

### Root Config Files

| File | Purpose |
|---|---|
| `pyproject.toml` | Central project config: package metadata, dependencies, build backend (`uv`), and tool settings for ruff, bandit, pytest, and mypy/ty |
| `uv.lock` | Fully resolved, reproducible dependency lock file managed by uv |
| `.python-version` | Pins the Python version used by uv for this project |
| `prek.toml` | Pre-commit hooks: `ruff format`, `ruff check --fix`, `ty check`, `bandit`, `rumdl check --fix` on pre-commit; `uv self update`, `uv lock --upgrade`, `uv sync` on pre-push/checkout/merge |
| `mkdocs.yml` | MkDocs + Material theme configuration with mkdocstrings and mermaid2 plugins |
| `branch-protection.json` | Declarative GitHub branch protection rules applied via `pyrig protect-repo` |
| `.env` | Environment variable template (empty by default) |
| `.scratch.py` | Local scratch file for experimentation (gitignored) |

### Markdown Files

| File | Purpose |
|---|---|
| `README.md` | Project overview with badges for CI status, coverage, PyPI version, Python version, and license |
| `CONTRIBUTING.md` | Guidelines for contributors: setup, workflow, and standards |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 code of conduct |
| `SECURITY.md` | Security vulnerability reporting policy |
| `LICENSE` | MIT license |

### Containerization

| File | Purpose |
|---|---|
| `Containerfile` | Podman-compatible container image definition for running the project |

### `.github/`

| File | Purpose |
|---|---|
| `pull_request_template.md` | Default PR description template with change overview structure |
| `ISSUE_TEMPLATE/bug_report.yml` | Structured bug report form |
| `ISSUE_TEMPLATE/feature_request.yml` | Structured feature request form |
| `ISSUE_TEMPLATE/config.yml` | Configures the issue template chooser |
| `workflows/health_check.yml` | Runs the full test suite on every PR, push to `main`, and on a nightly schedule |
| `workflows/build.yml` | Builds distributable artifacts after a successful health check |
| `workflows/release.yml` | Creates a GitHub release after a successful build |
| `workflows/deploy.yml` | Deploys documentation and packages after a successful release |

The four workflows form a chain that is a comprehensive CI/CD pipeline for
testing, building, releasing and deploying the project:

```text
Health Check ──► Build ──► Release ──► Deploy
```

### `src/my_pr/`

| File | Purpose |
|---|---|
| `__init__.py` | Top-level package module with a module-level docstring |
| `py.typed` | Empty PEP 561 marker file declaring the package as typed |

### `tests/`

| File | Purpose |
|---|---|
| `__init__.py` | Makes `tests/` a Python package |
| `conftest.py` | Registers pyrig's fixture plugins with pytest via `pytest_plugins` |
| `test_zero.py` | A single empty `test_zero` function so pytest never reports "no tests collected" |

## Tool-Generated Artifacts

These files and directories are created as side effects of the tools that
`pyrig init` runs (test suite, linters, etc.). They are gitignored and are
not directly managed by pyrig:

| Path | Created by |
|---|---|
| `.venv/` | uv — virtual environment |
| `.pytest_cache/` | pytest — test result cache |
| `.ruff_cache/` | ruff — linter cache |
| `.rumdl_cache/` | rumdl — Markdown linter cache |
| `.coverage` | pytest-cov — coverage measurement data |
