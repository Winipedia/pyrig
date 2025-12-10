# pyrig

[![built with pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=python&logoColor=white)](https://github.com/Winipedia/pyrig)
[![PyPI](https://img.shields.io/pypi/v/pyrig)](https://pypi.org/project/pyrig/)
[![Python](https://img.shields.io/badge/python-3.12+-blue)](https://pypi.org/project/pyrig/)
[![License](https://img.shields.io/github/license/winipedia/pyrig)](https://github.com/winipedia/pyrig/blob/main/LICENSE)
[![CI/CD](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml/badge.svg)](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml)

A Python development toolkit that standardizes project configuration and automates development workflows and standards.

## How to Use

```bash
# start a new project
uv init
uv add pyrig
uv run pyrig init
```

## Overview

pyrig eliminates the repetitive setup work involved in starting Python projects. A single command generates a complete project structure with pre-configured tooling:

- **Linting and formatting** with ruff (all rules enabled)
- **Static type checking** with mypy (strict mode)
- **Security scanning** with bandit
- **Test infrastructure** with pytest and coverage enforcement
- **Pre-commit hooks** for automated quality checks
- **GitHub Actions workflows** for CI/CD
- **Branch protection** via GitHub rulesets

The generated configuration stays synchronized automatically. When you run tests, pyrig validates that all config files match expected values and generates test skeletons for any untested code.

## Features

### Configuration Management

pyrig uses a ConfigFile system to manage project files. Each configuration file type (TOML, YAML, text, Python) has a corresponding class that defines the expected content. During initialization and test runs, pyrig ensures actual files match their expected configurations.

Some examples:
- `pyproject.toml` (project metadata, tool configs)
- `.pre-commit-config.yaml`
- `.gitignore`
- `.github/workflows/` (health check, release, publish)
- `conftest.py` and test fixtures

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

Three GitHub Actions workflows are generated:

1. **Health Check** — Runs on every push and PR
   - Executes pre-commit hooks (ruff, mypy, bandit)
   - Runs the full test suite
   - Tests across a matrix of 3 OS × 3 Python versions
   - Updates branch protection rules

2. **Release** — Triggers on health check success (main branch)
   - Optionally builds artifacts across OS matrix
   - Bumps version number
   - Commits and oushes version bump and dependency updates
   - Generates a changelog from PR history
   - Creates a GitHub release

3. **Publish** — Triggers on release creation
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
│       ├── publish.yaml              # Publish to PyPI after release
│       └── release.yaml              # Create GitHub releases
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
│   │   ├── artifacts/
│   │   │   └── builders/             # Custom artifact builders
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
