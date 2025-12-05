# pyrig

[![PyPI](https://img.shields.io/pypi/v/pyrig)](https://pypi.org/project/pyrig/)
[![Python](https://img.shields.io/pypi/pyversions/pyrig)](https://pypi.org/project/pyrig/)
[![License](https://img.shields.io/github/license/winipedia/pyrig)](https://github.com/winipedia/pyrig/blob/main/LICENSE)
[![CI](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml/badge.svg)](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml)

**pyrig** is a Python development toolkit that helps you **rig up** your Python projects by standardizing project configurations and automating testing workflows.

---

## Why pyrig?

**The problem:** Starting a new Python project means hours of setup — configuring linters, type checkers, CI/CD, pre-commit hooks, test infrastructure, and keeping it all in sync across projects.

**The solution:** pyrig handles it all automatically:

- **One command setup** — `uv run pyrig init` creates everything
- **Self-maintaining** — configs stay in sync, tests auto-generate, dependencies auto-update
- **Best practices enforced** — strict typing, all ruff rules, security scanning, branch protection

**Before pyrig:**
```
- Create pyproject.toml manually
- Configure ruff, mypy, pytest, bandit
- Write GitHub Actions workflows
- Set up pre-commit hooks
- Create test file structure
- Create Config files (e.g. pyproject.toml, .pre-commit-config.yaml, gitignore, etc.)
- Create CLI entry points if needed
- Create build scripts if needed
- Keep everything in sync... forever
```

**After pyrig:**
```bash
uv add pyrig && uv run pyrig init  # Done. Everything works.
```

---

## Quick Start

```bash
# 1. Create and clone a new GitHub repo
git clone https://github.com/your-username/my-project.git
cd my-project

# 2. Initialize with uv and add pyrig
uv init 
uv add pyrig

# 3. Run pyrig init (creates everything)
uv run pyrig init

# 4. Start coding - your project is ready
# - Write code in my_project/src/
# - Tests auto-generate when you run pytest
# - Pre-commit hooks auto-install
# - CI/CD workflows are ready

# 5. Commit and push
git add . && git commit -m "chore: init project" && git push
```

**That's it.** Your project now has linting, type checking, testing, CI/CD, and branch protection and much more — all configured and working.

---

## Features

### Architecture/File Generation
Pyrig generates your entire project structure, configs, and CI/CD via its Config File Machinery. 

### Testing
Pyrig automatically generates test skeletons for all functions and classes that are missing tests. 

### Autouse Fixtures
Pyrig provides a variety of autouse fixtures that run automatically before every test. They assert certain quality standards and conventions.

### CLI System
Pyrig provides a CLI system that automatically generates a CLI from your `main.py` and `subcommands.py`.

### Multi-Package Support
Pyrig automatically discovers all packages that depend on it, enabling shared configs, builders, fixtures, and resources across the ecosystem.

### CI/CD
Pyrig provides GitHub Actions workflows for continuous integration and delivery.

### Dependency Management
Pyrig automatically manages dependencies and keeps them up to date via uv.

### Security
Pyrig enforces security best practices via bandit and branch protection rulesets.

> For detailed documentation on each feature, see the [docs](docs/) directory.

---

## Requirements

- **uv**: Package and dependency manager
- **Git**: Version control
- **GitHub**: For full CI/CD and repository protection features (optional but recommended)

---

**Note**: pyrig should be added as a regular dependency, not a dev dependency, because the CLI and utility functions require runtime availability. While pyrig manages dev dependencies for tools like ruff, mypy, and pytest, it keeps itself as a regular dependency to ensure full functionality in all environments.

---
## License

pyrig is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

Copyright (c) 2025 Winipedia

---

## Links

- **Repository**: [github.com/winipedia/pyrig](https://github.com/winipedia/pyrig)
- **PyPI**: [pypi.org/project/pyrig](https://pypi.org/project/pyrig/)

---
