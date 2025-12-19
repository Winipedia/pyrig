# pyrig Documentation

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

> A Python toolkit that standardizes and automates project setup, configuration and development.

---

Welcome to the pyrig documentation! pyrig is a Python toolkit that standardizes and automates project setup, configuration, and development.

## Quick Navigation

```mermaid
graph TB
    Start[New to pyrig?] --> GS[Getting Started Guide]

    GS --> Choice{What do you want to do?}

    Choice -->|Understand the system| Arch[Architecture Overview]
    Choice -->|Build package ecosystem| Multi[Multi-Package Architecture]
    Choice -->|Customize configs| Configs[Configuration Files Reference]
    Choice -->|Troubleshoot issues| GS

    Arch --> Deep{Go deeper?}
    Deep -->|Yes| Multi
    Deep -->|No| Build[Start building]

    Multi --> Build
    Configs --> Build

    Build --> Success[Build amazing projects]

    style Start fill:#3776AB,color:#fff
    style GS fill:#FF8C00
    style Success fill:#2E7D32,color:#fff
```

## Getting Started

New to pyrig? Start here:

- **[Getting Started](getting-started.md)** - Complete guide to creating your first pyrig project
  - Prerequisites and setup
  - Step-by-step initialization
  - Understanding project structure
  - Your first code and tests
  - Common issues and solutions

## Architecture

- **[Architecture Overview](architecture.md)** - Visual guide to pyrig's architecture
  - System architecture diagrams
  - Data flow visualizations
  - Plugin architecture
  - Component interactions

## Core Concepts

- **[ConfigFile System](configfile-system.md)** - Deep dive into pyrig's living configuration system
  - How ConfigFiles work
  - Subset validation explained
  - Intelligent config merging
  - Format-specific base classes
  - Creating custom ConfigFiles
  - Real-world examples

- **[Builder System](builder-system.md)** - Deep dive into pyrig's artifact build system
  - How Builders work
  - The build process explained
  - Platform suffix handling
  - PyInstallerBuilder for executables
  - Creating custom Builders
  - Real-world examples

- **[Testing System](testing-system.md)** - Deep dive into pyrig's testing and fixture system
  - How fixture discovery works
  - Autouse fixtures that enforce best practices
  - Session, module, and class-scoped fixtures
  - Factory fixtures for isolated testing
  - Creating custom fixtures
  - Real-world examples

- **[Multi-Package Architecture](multi-package-architecture.md)** - Build package ecosystems with cross-package discovery of ConfigFiles, Builders, and fixtures
  - Dependency graph system
  - Cross-package discovery
  - Real-world examples
  - Best practices

## Configuration Files

- **[Configuration Files Reference](config-files/index.md)** - Detailed documentation for every config file managed by pyrig
  - ConfigFile base classes
  - Builder system
  - CLI commands
  - Test fixtures

## Comparison

- **[pyrig vs Other Tools](comparison.md)** - How pyrig compares to other project management tools
  - Cookiecutter comparison
  - Copier comparison
  - Poetry and PDM comparison
  - Feature matrix
  - Use case recommendations

## Drawbacks and Trade-offs

- **[Drawbacks and Trade-offs](drawbacks.md)** - Honest discussion of pyrig's limitations
  - Runtime dev/ folder overhead
  - Automatic CLI handling limitations
  - Forced tool choices (uv, ruff, ty, mypy, pytest, Podman)
  - Fixed project structure
  - Strict quality enforcement
  - GitHub-centric workflow
  - When NOT to use pyrig
