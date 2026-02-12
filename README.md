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
<!-- project-info -->
[![pypi](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)
<!-- testing -->
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org)
[![pytest-cov](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
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
[Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/) for detailed setup instructions.

## Features

### Project Scaffolding & Idempotent Init

pyrig's `init` command scaffolds a complete, production-ready Python project
(source layout, tests, CI/CD, docs, configs) and is safe to re-run — it's
idempotent. See the Getting Started guide for details and the full generated
project structure. See the [Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/#what-you-get) for the full layout.

### Config File System

Genrated Files are modeled as Python classes that generate, validate, and
merge automatically. Extend or override configurations by subclassing. See the
[Config Architecture](https://winipedia.github.io/pyrig/configs/architecture/) documentation for details.

### Dynamic Multi-Package CLI Discovery

Commands are discovered automatically from `<package>.rig.cli.subcommands` and
shared modules across the dependency chain, so projects add CLI commands with
no registration required — see the [CLI docs](https://winipedia.github.io/pyrig/cli/) for details.

### Pytest Enforcement & Autouse Fixtures

Autouse fixtures validate project invariants during tests, auto-generate
missing test skeletons, and ensure configs and separation rules are enforced.
See the [Autouse fixtures](https://winipedia.github.io/pyrig/tests/autouse/) documentation for details.

### Multi-Package Inheritance Model

Define multiproject-wide standards in a base package (configs, fixtures, CLI)
that downstream projects inherit and can override, enabling consistent policies
across multiple services — see the
[CLI architecture](https://winipedia.github.io/pyrig/cli/architecture/)
documentation for more on inheritance and command discovery.

### Tool Wrappers

pyrig provides type-safe Python wrappers for all tools that are used (`uv`,
`git`, `ruff`, `pytest`, etc.) to standardize usage and expose clear, typed
interfaces. Via pyrig's multi-package inheritance model, projects can adjust or
replace tool implementations by subclassing and overriding the provided tool
classes — this allows organization-wide customization or per-project overrides,
making tool behavior highly flexible — see the
[Tools docs](https://winipedia.github.io/pyrig/tools/) for details.

### Builders

pyrig includes a builders system (for example, PyInstaller integration) to
create distributables, standardize build processes, and integrate with
packaging back-ends — see the [Builders docs](https://winipedia.github.io/pyrig/builders/) for details.

### Resource Abstraction (Dev + PyInstaller)

Helpers provide reliable access to package resource files in development and
when bundled with PyInstaller. See the
[Resources docs](https://winipedia.github.io/pyrig/resources/) for resource
handling details.

### CI/CD & Repository Automation

pyrig generates GitHub workflows, branch protection configs, issue/PR templates
and includes commands to help configure repository protections and release flows
— see the
[Branch protection docs](https://winipedia.github.io/pyrig/configs/branch_protection/)
for repository automation details.

### Logging & CLI UX Controls

Global CLI verbosity flags (`-v`, `-vv`, `-q`) provide flexible logging
formatting and levels to improve developer ergonomics for commands and tools —
see the [CLI docs](https://winipedia.github.io/pyrig/cli/).

### Packaging & Distribution Integration

pyrig integrates with packaging and build back-ends (console scripts,
`uv_build`) to simplify publishing and distribution. See `pyproject.toml` and
the [Builders docs](https://winipedia.github.io/pyrig/builders/) for packaging and build details.

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
