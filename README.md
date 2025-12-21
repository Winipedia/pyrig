# pyrig

<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
[![MkDocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org/)
<!-- code-quality -->
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)[![mypy](https://img.shields.io/badge/type%20checked-mypy-039dfc.svg)](https://mypy-lang.org/)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
<!-- package-info -->
[![PyPI](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig/)
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

pyrig is an opinionated Python project toolkit that eliminates setup time and enforces best practices. Run one command to get a complete, production-ready project structure with CI/CD, testing, documentation, and more. Pyrig configures everything a serious new project needs out of the box, so that you can focus on writing code and start immediately developing your application, project or library.

### Key Features

**Zero Configuration Setup**:
- Complete project structure in minutes
- Pre-configured tools (uv, ruff, mypy, pytest, MkDocs)
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
- Strict mypy type checking
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

**Complete Project Structure**:
```
my-project/
├── my_project/                      # Source code package
│   ├── __init__.py
│   ├── main.py                      # CLI entry point
│   ├── py.typed                     # PEP 561 type marker
│   ├── dev/                         # Development infrastructure
│   │   ├── __init__.py
│   │   ├── builders/                # Build artifact definitions
│   │   │   ├── __init__.py
│   │   ├── cli/                     # CLI command system
│   │   │   ├── __init__.py
│   │   │   ├── subcommands.py       # Project commands
│   │   │   ├── shared_subcommands.py # Shared commands
│   │   ├── configs/                 # Config file managers
│   │   │   ├── __init__.py
│   │   ├── tests/                   # Test infrastructure
│   │   │   ├── __init__.py
│   │   │   └── fixtures/
│   │   │       └── __init__.py
│   ├── resources/                   # Static resources
│   │   └── __init__.py
│   └── src/                         # Application logic
│       └── __init__.py
│
├── tests/                           # Test files (mirrors source)
│   ├── __init__.py
│   ├── conftest.py                  # Pytest configuration
│   ├── test_zero.py                 # Initial test
│   └── test_my_project/             # Mirrors my_project/ structure
│       ├── __init__.py
│       ├── test_main.py
│       ├── test_dev/                # Mirrors my_project/dev/
│       │   ├── __init__.py
│       │   ├── test_builders/
│       │   │   └── __init__.py
│       │   ├── test_cli/
│       │   │   ├── __init__.py
│       │   │   ├── test_subcommands.py
│       │   │   └── test_shared_subcommands.py
│       │   ├── test_configs/
│       │   │   └── __init__.py
│       │   └── test_tests/
│       │       └── __init__.py
│       ├── test_resources/          # Mirrors my_project/resources/
│       │   └── __init__.py
│       └── test_src/                # Mirrors my_project/src/
│           └── __init__.py
│
├── docs/                            # MkDocs documentation
│   └── index.md                     # Documentation homepage
│
├── .github/                         # GitHub configuration
│   └── workflows/                   # CI/CD workflows
│       ├── health_check.yaml        # Tests, linting, type checking
│       ├── build.yaml               # Build artifacts
│       ├── release.yaml             # Version and release
│       └── publish.yaml             # PyPI and docs publishing
│
├── .env                             # Environment variables (not committed)
├── .experiment.py                   # Scratch file for local experiments (not committed)
├── .gitignore                       # Git ignore patterns
├── .pre-commit-config.yaml          # Pre-commit hooks
├── .python-version                  # Python version (3.12+)
├── Containerfile                    # Podman/Docker image definition
├── LICENSE                          # MIT license
├── README.md                        # Project readme
├── mkdocs.yml                       # MkDocs configuration
├── pyproject.toml                   # Project metadata and tool configs
└── uv.lock                          # Dependency lock file
```

**CI/CD Workflows**:
- **Health Check** - Tests, linting, type checking on every PR
- **Build** - Creates executables and container images
- **Release** - Automated version bumping and GitHub releases
- **Publish** - PyPI and GitHub Pages deployment

**Development Tools**:
- **uv** - Fast package management (10-100x faster than pip)
- **ruff** - Linting and formatting (all rules enabled)
- **mypy** - Static type checking (strict mode)
- **pytest** - Testing with coverage reporting
- **MkDocs** - Documentation generation
- **Podman** - Container support

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

**[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/)** - Complete setup from zero to fully configured project

**[Full Documentation](https://winipedia.github.io/pyrig/)** - Comprehensive documentation on GitHub Pages

---
