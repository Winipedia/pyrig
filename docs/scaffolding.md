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
├── CODE_OF_CONDUCT.md                      # Contributor Covenant code of conduct
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
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml                  # Bug report issue form
│   │   ├── config.yml                      # Issue template chooser configuration
│   │   └── feature_request.yml             # Feature request issue form
│   └── workflows/
│       ├── health_check.yml                # CI: runs tests and more
│       ├── release.yml                     # CI: triggered after health check passes
│       └── deploy.yml                      # CI: triggered after release passes
│
├── docs/
│   ├── api.md                              # API reference page (mkdocstrings)
│   └── index.md                            # Documentation home page
│
├── src/
│   └── my_project/                         # Package root (project name → snake_case)
│       ├── __init__.py                     # Top-level package module
│       └── py.typed                        # PEP 561 marker (typed package)
```
