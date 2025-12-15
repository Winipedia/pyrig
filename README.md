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


## How to Use

```bash
# start a new project
uv init
uv add pyrig
uv run pyrig init
```

## Philosophy

pyrig is built on the following principles:

1. **Opinionated Defaults**: pyrig enforces a set of best practices and standards across all projects.
2. **Automation**: pyrig automates repetitive tasks like setting up CI/CD, managing dependencies, and enforcing standards.
3. **Extensibility**: pyrig can be extended by dependent packages to enforce additional standards.
4. **Simplicity**: pyrig should require minimal configuration to get started.
5. **Consistency**: pyrig ensures all projects adhere to the same standards and best practices.
6. **Stay up to date**: pyrig projects should stay up to date with the latest tools and best practices.

Note:
pyrig does it enforce specific tools, like e.g. uv, podman, git and github.
We keep pyrig up to a standard where we think we are using the best tools for the job.
E.g. We switched to uv but started with poetry for dependency management.
If a genuine better tool comes along for a specific task, we will switch and enforce it.
pyrigs most important principle is to stay up to date and do not stagnate on legacy code and tools.

## Overview

pyrig eliminates the repetitive setup work involved in starting Python projects. A single command generates a complete project structure with pre-configured tooling:

- **Linting and formatting** with ruff (all rules enabled)
- **Static type checking** with ty and mypy (strict mode)
- **Security scanning** with bandit
- **Test infrastructure** with pytest and coverage enforcement
- **Pre-commit hooks** for automated quality checks
- **GitHub Actions workflows** for CI/CD
- **Branch protection** via GitHub rulesets

> **Note on Type Checking:** pyrig currently uses both `ty` (a modern, fast type checker) and `mypy` (the established standard). In the future, we plan to transition to using only `ty` once it matures further. For now, both type checkers run in pre-commit hooks and CI to ensure maximum type safety.

The generated configuration stays synchronized automatically. When you run tests, pyrig validates that all config files match expected values and generates test skeletons for any untested code.

## Features

### Configuration Management

pyrig uses a ConfigFile system to manage project files. Each configuration file type (TOML, YAML, text, Python) has a corresponding class that defines the expected content. During initialization and test runs, pyrig ensures actual files match their expected configurations.

Some examples:
- `pyproject.toml` (project metadata, tool configs)
- `.pre-commit-config.yaml`
- `.gitignore` (fetched from GitHub with offline fallback)
- `LICENSE` (auto-generated MIT license with year and owner)
- `.github/workflows/` (health check, release, publish)
- `conftest.py` and test fixtures

### Network Resilience and Offline Capability

pyrig works reliably even without internet access. External resources (GitHub's .gitignore template, MIT license text, latest Python version) are fetched when online but fall back to cached local resources when offline or when services are unavailable. This ensures:

- Projects can be initialized offline
- Service outages don't break pyrig
- Consistent behavior across all environments
- Automatic resource updates when online

### Test Generation

pyrig automatically generates test file skeletons that mirror your source structure:

```
my_project/src/utils.py    →    tests/test_my_project/test_src/test_utils.py
```

Each function, class, and method gets a corresponding test stub that raises `NotImplementedError`. Autouse fixtures enforce that all code has tests—if something is untested, the test run fails with a clear message.

### CLI System

Projects using pyrig get a CLI automatically. Commands are defined as functions in `your_project/dev/cli/subcommands.py`:

```python
def deploy() -> None:
    """Deploy the application."""
    ...
```

This becomes available as `your-project deploy`. Function names convert from snake_case to kebab-case.

Built-in pyrig commands:
- `pyrig init` — Initialize project structure
- `pyrig mkroot` — Regenerate config files
- `pyrig mktests` — Generate missing test files
- `pyrig mkinits` — Create missing `__init__.py` files
- `pyrig build` — Create distributable artifacts
- `pyrig protect-repo` — Apply GitHub branch protection

### Multi-Package Architecture

pyrig supports a plugin-style architecture where dependent packages can extend its functionality. Packages that depend on pyrig can define their own:

- ConfigFile subclasses (custom configuration files)
- Builder subclasses (custom artifact builders)
- Pytest fixtures (shared test utilities)
- CLI commands (additional tooling)

pyrig discovers these extensions automatically by traversing the dependency graph. This enables base packages that enforce organizational standards across multiple projects.

### CI/CD Integration

Four GitHub Actions workflows are generated:

1. **Health Check** — Runs on every push and PR
   - Executes pre-commit hooks (ruff, ty, mypy, bandit)
   - Runs the full test suite
   - Tests across a matrix of 3 OS × 3 Python versions
   - Uploads coverage reports to Codecov
   - Updates branch protection rules

2. **Build** — Triggers on health check success (main branch)
   - Builds artifacts across OS matrix
   - Uploads artifacts for downstream workflows

3. **Release** — Triggers on build success
   - Downloads artifacts from build workflow
   - Bumps version number
   - Commits and pushes version bump and dependency updates
   - Generates a changelog from PR history
   - Creates a GitHub release

4. **Publish** — Triggers on release creation
   - Builds distribution packages
   - Publishes to PyPI

### Dependency Management

pyrig uses [uv](https://github.com/astral-sh/uv) for package management with a version-free approach:

- Dependencies in `pyproject.toml` omit version specifiers
- Exact versions are tracked in `uv.lock`
- CI automatically runs `uv lock --upgrade` to keep dependencies current

### Security

Security is enforced at multiple levels:

- **Bandit** scans code for common vulnerabilities before each commit
- **Branch protection** requires PR reviews, signed commits, and passing CI
- **Required status checks** prevent merging without green builds
- **Linear history** is enforced (squash or rebase merging only)

## Project Structure

After running `pyrig init`, your project will have this structure:

```
my_project/
├── .env                              # Environment variables (gitignored)
├── .experiment.py                    # Local experimentation file (gitignored)
├── .github/
│   └── workflows/
│       ├── health_check.yaml         # CI: tests, linting, type checking
│       ├── build.yaml                # Build artifacts across OS matrix
│       ├── release.yaml              # Create GitHub releases
│       └── publish.yaml              # Publish to PyPI after release
├── .gitignore                        # Git ignore patterns
├── .pre-commit-config.yaml           # Pre-commit hooks configuration
├── .python-version                   # Python version for pyenv/uv
├── docs/
│   └── index.md                      # Documentation index
├── LICENSE                           # License file
├── README.md                         # Project readme
├── pyproject.toml                    # Central project configuration
├── uv.lock                           # Locked dependencies
│
├── my_project/                       # Source package
│   ├── __init__.py
│   ├── main.py                       # CLI entry point
│   ├── py.typed                      # PEP 561 type marker
│   ├── dev/
│   │   ├── builders/                 # Custom artifact builders
│   │   ├── cli/
│   │   │   └── subcommands.py        # Custom CLI commands
│   │   ├── configs/                  # Custom ConfigFile classes
│   │   └── tests/
│   │       └── fixtures/             # Custom fixtures (auto-discovered)
│   ├── resources/                    # Build resources (icons, etc.)
│   └── src/                          # Your source code goes here
│
└── tests/
    ├── conftest.py                   # Pytest configuration
    ├── test_zero.py                  # Placeholder test
    └── test_my_project/              # Auto-generated test structure
```

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- Git
- GitHub (for CI/CD and branch protection features)

## Documentation

Detailed documentation is available in the [docs/](docs/) directory:

- [Architecture and File Generation](docs/architecture-file-generation.md)
- [Testing and Test Generation](docs/testing-test-generation.md)
- [Autouse Fixtures](docs/autouse-fixtures-validation.md)
- [CLI System](docs/cli-command-line-interface.md)
- [Builder System](docs/builder-system.md)
- [CI/CD Integration](docs/cicd-continuous-integration.md)
- [Dependency Management](docs/dependency-management.md)
- [Multi-Package Support](docs/multi-package-support.md)
- [Security](docs/security.md)

## License

MIT License. See [LICENSE](LICENSE) for details.
