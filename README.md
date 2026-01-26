# pyrig

<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![MkDocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org/)
<!-- code-quality -->
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
<!-- package-info -->
[![PyPI](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![Python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yml)
<!-- documentation -->
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://Winipedia.github.io/pyrig)

---

> A Python toolkit to rig up your project that standardizes and automates project setup, configuration and development.

---

## What is pyrig?

pyrig generates and maintains a complete, production-ready Python project from a
single command. It creates all the files you need—source structure, tests,
CI/CD, documentation, configs—and keeps them in sync as your project evolves.

**Run once, stay current**: pyrig is idempotent. Rerun it anytime to update
configs, add missing files, or sync with the latest best practices.

## Quick Start

```bash
# Initialize project with uv and pyrig
uv init
uv add pyrig
uv run pyrig init
```

That's it. You now have a complete project with:

- Source code structure with CLI entry point
- Test framework with 90% coverage enforcement
- GitHub Actions (CI/CD, releases, docs deployment)
- Pre-commit hooks (linting, formatting, type checking)
- MkDocs documentation site
- Container support (Podman/Docker)

See the
[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/)
for detailed setup instructions.

## Key Features

### Config File System

pyrig's core is a declarative config file system. Each config file
(pyproject.toml, .pre-commit-config.yaml, GitHub workflows, etc.) is a Python
class that:

- **Generates** the file with working sensible defaults
- **Validates** existing files against expected structure
- **Merges** missing values without removing your customizations (overrides are
  possible, read the docs for details)

Create custom configs by subclassing—pyrig discovers them automatically.

### Multi-Package Inheritance

Build on pyrig to create multiproject-wide standards. Your base package defines
configs, fixtures, and CLI commands that all dependent projects inherit:

```text
pyrig → company-base → auth-service
                     → payment-service
                     → notification-service
```

Override any config by subclassing with the same class name. Leaf classes win.

### Automatic Discovery

Everything is discovered automatically across the dependency chain:

- **CLI commands** from `<package>.dev.cli.subcommands`
- **Config files** from `<package>.dev.configs`
- **Test fixtures** from `<package>.dev.tests.fixtures`
- **Builders** from `<package>.dev.builders`
- **Tools** from `<package>.dev.management`

No registration required. Just define and it works.

### What Gets Generated

After `pyrig init`, your project includes:

| Category | Files |
|----------|-------|
| **Source** | Package structure, `main.py` CLI, `py.typed` marker |
| **Tests** | Mirror structure, `conftest.py`, test skeletons |
| **CI/CD** | Health check, build, release, deploy workflows |
| **Docs** | MkDocs config, index, API reference |
| **GitHub** | Issue templates, PR template, branch protection |
| **Community** | CODE_OF_CONDUCT, CONTRIBUTING, SECURITY |
| **Config** | pyproject.toml, .gitignore, .pre-commit-config.yaml, Containerfile |

## CLI Commands

```bash
uv run pyrig init         # Complete project initialization
uv run pyrig mkroot       # Create/update all config files
uv run pyrig mktests      # Generate test skeletons
uv run pyrig mkinits      # Create __init__.py files
uv run pyrig build        # Build artifacts (PyInstaller, etc.)
uv run pyrig protect-repo # Configure repository protection
uv run my-project --help  # Your project's CLI
```

## Opinionated Defaults

pyrig enforces modern Python best practices:

- **Python 3.12+** with full type hints
- **All ruff rules** enabled (with sensible exceptions)
- **Strict type checking** with ty
- **90% test coverage** minimum
- **Linear git history** with branch protection

## Documentation

- **[Getting Started](https://winipedia.github.io/pyrig/more/getting-started/)** -
  Complete setup guide
- **[Full Documentation](https://winipedia.github.io/pyrig/)** - Comprehensive
  reference
- **[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)** -
  AI-generated docs

---
