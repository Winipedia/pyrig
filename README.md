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

> A Python toolkit that standardizes and automates project setup, configuration and development.

---

## What is pyrig?

**pyrig** is an opinionated Python project framework that enforces best practices and keeps your projects up-to-date automatically. Unlike traditional project templates, pyrig is a living system that manages your entire development lifecycle. Pyrig makes project development seamless and keeps you focused on your code. It allows even in bigger projects to not lose the overview. Its opinionated and best practices approach allows you to always know what belongs where and where to find things.

<table>
<tr>
<td width="50%">

**Traditional Templates**
```mermaid
graph TB
    T1[Generate once] --> T2[Manual updates]
    T2 --> T3[Config drift]
    T3 --> T4[Maintenance burden]
    style T4 fill:#FF6B6B,color:#fff
```

</td>
<td width="50%">

**pyrig**
```mermaid
graph TB
    P1[Living system] --> P2[Auto-sync configs]
    P2 --> P3[Always current]
    P3 --> P4[Focus on code]
    style P4 fill:#2E7D32,color:#fff
```

</td>
</tr>
</table>

### Key Features

- **Automated Setup** - Initialize production-ready projects in seconds with `pyrig init`
- **Living Configuration** - Configs stay synchronized automatically, no manual maintenance
- **Enforced Quality** - Strict linting, type checking, testing, and security scanning out of the box
- **Always Current** - Automatic dependency updates and latest tool versions via CI/CD
- **Multi-Package Support** - Build package ecosystems with cross-package discovery of ConfigFiles, Builders, fixtures, and CLI commands
- **Extensible Architecture** - Plugin system for custom ConfigFiles and Builders

### Philosophy

pyrig is designed for **serious, long-term Python projects** where code quality and maintainability matter. It makes opinionated choices about tooling and enforces best practices, so you can focus on building features instead of configuring tools and wondering what is the best way to do something.

**Core principle:** Use the best tools available that work correctly. pyrig chooses modern, fast, reliable tools and enforces them consistently across all projects. This eliminates tool debates and ensures every pyrig project follows the same high standards.

## Quick Start

### Prerequisites

- **GitHub account and repository** - pyrig is GitHub-only (no GitLab/Bitbucket support)
- **Git** with username matching your GitHub username
- **uv** package manager (10-100x faster than pip)
- **Podman** (for containerization, preferred over Docker)

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

<table>
<tr>
<td width="50%">

**Other Templates**
```mermaid
graph TB
    O1[Generate once] --> O2[Manual sync]
    O2 --> O3[Config drift]
    O3 --> O4[Outdated tools]
    style O4 fill:#FF6B6B,color:#fff
```

</td>
<td width="50%">

**pyrig**
```mermaid
graph TB
    P1[Living system] --> P2[Auto-sync]
    P2 --> P3[Always current]
    P3 --> P4[Enforced quality]
    style P4 fill:#2E7D32,color:#fff
```

</td>
</tr>
</table>

**Key Differences:**

| Feature | Other Templates | pyrig |
|---------|----------------|-------|
| Configuration | One-time generation | Living, auto-syncing |
| Best Practices | Suggested | Enforced |
| Updates | Manual | Automatic via CI/CD |
| Scope | Initial setup | Full lifecycle |
| Extensibility | Limited | Plugin architecture |

## Project Structure

pyrig creates a clean, organized structure:

```mermaid
graph TB
    Root[your-project/]

    Root --> Pkg[package/]
    Root --> Tests[tests/]
    Root --> Docs[docs/]
    Root --> GH[.github/workflows/]
    Root --> Configs[Config Files]

    Pkg --> Dev[dev/<br/>Development tools]
    Pkg --> Src[src/<br/>Application code]
    Pkg --> Res[resources/<br/>Static files]

    Dev --> Builders[builders/]
    Dev --> CLI[cli/]
    Dev --> ConfigFiles[configs/]
    Dev --> Fixtures[tests/fixtures/]

    Tests --> TestPkg[test_package/<br/>Mirrors src/]
    Tests --> Conftest[conftest.py]

    GH --> Build[build.yaml]
    GH --> Health[health_check.yaml]
    GH --> Publish[publish.yaml]
    GH --> Release[release.yaml]

    style Src fill:#2E7D32,color:#fff
    style Dev fill:#FF8C00
    style Tests fill:#FF6B6B,color:#fff
    style GH fill:#3776AB,color:#fff
```

## Requirements

- **Git** (any recent version)
- **uv** package manager (10-100x faster than pip)
- **GitHub account** (required - pyrig is GitHub-only)
- **Podman** (optional, for containerization - preferred over Docker)

## Tool Philosophy

pyrig makes opinionated choices about tooling:

- **Package Manager:** uv (10-100x faster than pip/poetry)
- **Linter/Formatter:** ruff (10-100x faster than black/pylint)
- **Type Checker:** ty + mypy (ty is fast, mypy is comprehensive)
- **Testing:** pytest (industry standard)
- **CI/CD:** GitHub Actions (best integration)
- **Container:** Podman preferred (daemonless, rootless, more secure)

**Why?** pyrig's philosophy is to use the best tools available that work correctly, and integrate deeply with them. This eliminates tool debates, ensures consistency, and provides the best performance.

**Will other tools be supported?** Very unlikely—supporting multiple tools would defeat pyrig's purpose. However, pyrig **will** switch tools when superior alternatives emerge (e.g., we switched from poetry to uv because uv is 10-100x faster).

**Can I customize?** Yes! You can override configs via subclassing or create empty config files to opt-out of specific tools. See [drawbacks documentation](docs/drawbacks.md#3-forced-tool-choices) for details.

## Contributing

Contributions are welcome! pyrig is built with pyrig itself, so you can explore the codebase to see how it works.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **PyPI**: [pypi.org/project/pyrig](https://pypi.org/project/pyrig/)
- **Documentation**: [docs/](docs/)
- **Issues**: [github.com/Winipedia/pyrig/issues](https://github.com/Winipedia/pyrig/issues)
- **Source**: [github.com/Winipedia/pyrig](https://github.com/Winipedia/pyrig)
