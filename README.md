# pyrig

<!-- security -->
[![bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pip-audit](https://img.shields.io/badge/security-pip--audit-blue?logo=python)](https://github.com/pypa/pip-audit)
<!-- tooling -->
[![git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
[![github](https://img.shields.io/github/stars/Winipedia/pyrig?style=social)](https://github.com/Winipedia/pyrig)
[![podman](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io)
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
<!-- documentation -->
[![mkdocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org)
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://Winipedia.github.io/pyrig)
<!-- code-quality -->
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
<!-- testing -->
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org)
[![codecov](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
<!-- project-info -->
[![PyPI](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![Python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yml)

---

> pyrig is python toolkit that rigs up your project by standardizing and automating project setup, configuration and maintanence <!-- rumdl-disable-line MD013 -->

---

## What is pyrig?

pyrig generates and maintains a complete, production-ready Python project from a
single command. It creates all the files you need — source structure, tests,
CI/CD, documentation, configs — and keeps them in sync as your project evolves.
Rerun it anytime: pyrig is idempotent.

## Quick Start

```bash
uv init
uv add pyrig
uv run pyrig init
```

See the
[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/)
for detailed setup instructions.

## Key Features

### Config File System

Every config file (pyproject.toml, prek.toml, GitHub workflows, etc.) is a
Python class that generates, validates, and merges automatically. Extend any
config by subclassing — pyrig discovers it with no registration needed:

```python
# my_project/rig/configs/pre_commit.py
from pyrig.rig.configs.pre_commit import PrekConfigFile as Base

class PrekConfigFile(Base):
    def _get_configs(self):
        configs = super()._get_configs()
        configs[0]["hooks"].append({"id": "my-hook", "name": "My Hook", ...})
        return configs
```

For more information, see [Config Architecture](https://winipedia.github.io/pyrig/configs/architecture/).

### Multi-Package Inheritance

Build on pyrig to create multiproject-wide standards. Your base package defines
configs, fixtures, and CLI commands that all dependent projects inherit:

```text
pyrig → service-base → auth-service
                     → payment-service
                     → notification-service
```

Override any config by subclassing with the same class name. Leaf classes win.

### Automatic Discovery

Everything is discovered automatically across the dependency chain — CLI
commands, config files, test fixtures, builders, and tools. For example, any
public function in `subcommands.py` becomes a CLI command:

```python
# my_project/rig/cli/subcommands.py
def greet(name: str) -> None:
    """Say hello."""
    print(f"Hello, {name}!")
```

```bash
$ uv run my-project greet --name World
Hello, World!
```

No registration required. Just define and it works.

### Pytest Enforcement

pytest itself enforces project correctness. Autouse session fixtures run before
your tests to check invariants — missing test modules are auto-generated,
configs are validated, namespace packages are prevented, and rig/src dependency
separation is verified. See
[Autouse Fixtures](https://winipedia.github.io/pyrig/tests/autouse/).

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
| **Config** | pyproject.toml, .gitignore, prek.toml, Containerfile |

See the [full project structure](https://winipedia.github.io/pyrig/more/getting-started/#what-you-get) in the Getting Started guide.

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

## Documentation

- **[Getting Started](https://winipedia.github.io/pyrig/more/getting-started/)** - Complete setup guide
- **[Full Documentation](https://winipedia.github.io/pyrig/)** - Comprehensive
  reference
- **[Trade-offs](https://winipedia.github.io/pyrig/more/drawbacks/)** -
  What you give up and what you gain
- **[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)** -
  AI-generated docs
- **[Tutorials](https://www.youtube.com/@Winipedia-py/playlists)** - YouTube tutorials for pyrig
