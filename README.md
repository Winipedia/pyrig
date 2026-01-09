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
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yaml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yaml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yaml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yaml)
<!-- documentation -->
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://Winipedia.github.io/pyrig)

---

> A Python toolkit to rig up your project that standardizes and automates project setup, configuration and development.

---

## What is pyrig?

pyrig is an opinionated toolkit for Python projects that removes setup friction
and enforces best practices. With a single command, it scaffolds a complete,
production-ready project with CI/CD, testing, documentation, and more. It’s
designed to be rerun safely to keep your repository up to date as standards
evolve.

**Philosophy**: pyrig ships minimal, best-practice defaults that work together
out of the box. Every configuration, workflow, and tool is preconfigured and
ready from day one—while still being customizable through pyrig’s extension
points.

### Key Features

**Zero Configuration Setup**:

- Complete project structure in minutes
- Pre-configured tools (uv, ruff, ty, pytest, MkDocs)
- GitHub Actions workflows (health check, build, release, publish)
- 90% test coverage enforcement
- Pre-commit hooks with all quality checks

**Automated Project Management**:

- CLI framework with automatic command discovery
- Configuration file system with validation
- Automatic test skeleton generation
- PyInstaller executable building
- Multi-package architecture support

**Opinionated Best Practices**:

- Python >=3.12 with modern type hints
- All ruff linting rules enabled
- Strict type checking with ty
- Signed commits and linear history
- Repository protection rules

### Quick Example

```bash
# Create repository on GitHub
git clone https://github.com/username/my-project.git
cd my-project

# Initialize with uv and pyrig
uv init
uv add pyrig
uv run pyrig init

# Complete project ready in minutes:
# ✓ Source code structure
# ✓ Test framework with 90% coverage
# ✓ CI/CD workflows
# ✓ Documentation site
# ✓ Pre-commit hooks
# ✓ Container support
```

### What You Get

After running `uv run pyrig init`, you get a complete project with:

- **Complete directory structure** with source code, tests, docs, and CI/CD
- **Pre-configured tools** (uv, ruff, ty, pytest, MkDocs, Podman)
- **GitHub Actions workflows** (health check, build, release, publish)
- **90% test coverage** enforcement
- **Pre-commit hooks** with all quality checks

See the
[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/)
for the complete project structure and detailed setup instructions.

### CLI Commands

```bash
uv run pyrig init        # Complete project initialization
uv run pyrig mkroot      # Update project structure
uv run pyrig mktests     # Generate test skeletons
uv run pyrig build       # Build all artifacts
uv run my-project --help # Your custom CLI
```

## Quick Start

New to pyrig? Start here:

- *[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/)*
- Complete setup from zero to fully configured project

**[Full Documentation](https://winipedia.github.io/pyrig/)** - Comprehensive documentation on GitHub Pages

**[CodeWiki Documentation](https://codewiki.google/github.com/winipedia/pyrig)** - AI-generated documentation

---
