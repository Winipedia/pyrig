# pyrig

<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
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

---

> A Python toolkit that standardizes and automates project setup, configuration and development.

---

## What is pyrig?

**pyrig** is an opinionated Python project framework that enforces best practices and keeps your projects up-to-date automatically. Unlike traditional project templates, pyrig is a living system that manages your entire development lifecycle. Pyrig makes project development seamless and keeps you focused on your code. It allows even in bigger projects to not lose the overview. Its opinionated and best practices approach allows you to always know what belongs where and where to find things.

### Key Features

- **Automated Setup** - Initialize production-ready projects in seconds with `pyrig init`
- **Living Configuration** - Configs stay synchronized automatically, no manual maintenance
- **Enforced Quality** - Strict linting, type checking, testing, and security scanning out of the box
- **Always Current** - Automatic dependency updates and latest tool versions via CI/CD
- **Multi-Package Support** - Build package ecosystems with cross-package discovery of ConfigFiles, Builders, fixtures, and CLI commands
- **Extensible Architecture** - Plugin system for custom ConfigFiles and Builders

### Philosophy

pyrig is designed for **serious, long-term Python projects** where code quality and maintainability matter. It makes opinionated choices about tooling and enforces best practices, so you can focus on building features instead of configuring tools and wondering what is the best way to do something.

## Quick Start

### Prerequisites

- **Git** with username matching your GitHub username
- **uv** package manager
- **Podman** (for containerization)

### Installation

```bash
# Create a new GitHub repository (don't initialize with README)
# Clone it locally
git clone https://github.com/YourUsername/your-project.git
cd your-project

# Initialize with uv
uv init

# Add pyrig
uv add pyrig

# Initialize your project (this does everything!)
uv run pyrig init
```

That's it! You now have a fully configured project with:
- Automated testing with pytest (90% coverage requirement)
- Linting and formatting with ruff (ALL rules enabled)
- Type checking with ty and mypy (strict mode)
- Security scanning with bandit
- Pre-commit hooks for quality enforcement
- GitHub Actions CI/CD workflows
- Branch protection and repository security
- Containerfile for deployment
- Custom CLI commands via `dev/cli/subcommands.py` and `dev/cli/shared_subcommands.py`

### Next Steps

After initialization, start coding in `<package>/src/` and run:

```bash
uv run pyrig mktests    # Generate test skeletons
uv run pytest           # Run tests
git add .
git commit -m "Add feature"  # Pre-commit hooks run automatically
git push
```

## Documentation

- **[Documentation Index](docs/index.md)** - Full documentation
- **[Getting Started Guide](docs/getting-started.md)** - Complete guide to creating your first pyrig project
- **[Multi-Package Architecture](docs/multi-package-architecture.md)** - Build package ecosystems with cross-package discovery
- **[Configuration Files Reference](docs/config-files/index.md)** - Detailed documentation for every config file

## Technology Stack

pyrig uses cutting-edge Python tooling:

- **[uv](https://github.com/astral-sh/uv)** - Fast Python package manager
- **[ruff](https://github.com/astral-sh/ruff)** - Extremely fast linter and formatter
- **[ty](https://github.com/astral-sh/ty)** - Fast type checker
- **[mypy](https://mypy-lang.org/)** - Static type checker
- **[pytest](https://pytest.org/)** - Testing framework
- **[bandit](https://github.com/PyCQA/bandit)** - Security scanner
- **[pre-commit](https://pre-commit.com/)** - Git hook framework
- **[Podman](https://podman.io/)** - Daemonless container runtime
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD platform

## What Makes pyrig Different?

Unlike cookiecutter, copier, or other project templates:

- **Living** - Configs stay synchronized automatically, not just at creation time
- **Opinionated** - Best practices enforced, not suggested
- **Comprehensive** - Handles everything from init to deployment
- **Current** - Automatically updates to latest tools and standards
- **Extensible** - Plugin architecture for custom functionality

## Project Structure

pyrig creates a clean, organized structure:

```
your-project/
├── <package>/
│   ├── dev/        # Development tools (not in production)
│   ├── src/        # Your application code
│   └── resources/  # Static files
├── tests/          # Test suite (mirrors src/)
├── docs/           # Documentation
├── .github/        # CI/CD workflows
└── ...             # Config files
```

## Requirements

- Git (any recent version)
- uv package manager
- GitHub account (for CI/CD and repository protection)
- Podman (optional, for containerization)

## Contributing

Contributions are welcome! pyrig is built with pyrig itself, so you can explore the codebase to see how it works.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **PyPI**: [pypi.org/project/pyrig](https://pypi.org/project/pyrig/)
- **Documentation**: [docs/](docs/)
- **Issues**: [github.com/Winipedia/pyrig/issues](https://github.com/Winipedia/pyrig/issues)
- **Source**: [github.com/Winipedia/pyrig](https://github.com/Winipedia/pyrig)
