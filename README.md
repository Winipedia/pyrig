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

> pyrig is a python toolkit that rigs up your project by standardizing and automating project setup, configuration and maintenance <!-- rumdl-disable-line MD013 -->

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

### Idempotent Project Scaffolding

`pyrig init` generates a complete project in one command — source tree, tests,
CI/CD workflows, documentation, configs, and a working CLI. Run it again
anytime to sync everything; pyrig never overwrites your customizations.

→ [Getting Started](https://winipedia.github.io/pyrig/more/getting-started/)
· [Generated Structure](https://winipedia.github.io/pyrig/more/getting-started/#what-you-get)

### Config File System

Every generated file is backed by a Python class that validates and merges
automatically. Override any config by subclassing, or define entirely new
config files — pyrig discovers and manages them for you.

→ [Config Architecture](https://winipedia.github.io/pyrig/configs/architecture/)

### Automatic CLI

`pyrig init` sets up a CLI for your project that works immediately. Add
commands by defining functions in `<package>.rig.cli.subcommands` — they're
discovered automatically. Shared commands propagate across the entire
dependency chain.

→ [CLI docs](https://winipedia.github.io/pyrig/cli/)

### Testing Infrastructure

- **pytest** as the test runner with autouse fixtures that enforce best
  practices
- **`pyrig mktests`** generates test skeletons mirroring your source
  structure
- **Autouse fixtures** validate project invariants — init files, config
  correctness, dependency freshness

→ [Test Structure](https://winipedia.github.io/pyrig/tests/structure/)
· [Autouse Fixtures](https://winipedia.github.io/pyrig/tests/autouse/)

### Multi-Package Inheritance (`.I` pattern)

Override almost any behavior — configs, tools, CLI commands, builders — by
subclassing the pyrig-provided class. pyrig discovers your implementation
automatically and uses it instead of the default.

This enables creating a **personal pyrig package** with your own standards,
adding it as a dependency to any project, and having `pyrig init` apply
everything automatically.

→ [Tool Architecture](https://winipedia.github.io/pyrig/tools/architecture/#two-extension-mechanisms)
· [Config Architecture](https://winipedia.github.io/pyrig/configs/architecture/#automatic-discovery)

### Tool Wrappers

Type-safe wrappers around `uv`, `git`, `ruff`, `pytest`, `bandit`, and more.
Customizable via subclassing for organization-wide or per-project overrides.

→ [Tools](https://winipedia.github.io/pyrig/tools/)
· [Tooling Choices](https://winipedia.github.io/pyrig/more/tooling/)

### Builders, Resources & Packaging

- **Builders** — PyInstaller integration and extensible build system
- **Resources** — Reliable file access in both development and PyInstaller
  bundles
- **Packaging** — `uv_build` backend with console script integration

→ [Builders](https://winipedia.github.io/pyrig/builders/)
· [Resources](https://winipedia.github.io/pyrig/resources/)

### CI/CD & Repository Automation

Generates GitHub Actions workflows, branch protection configs, issue/PR
templates, and release flows. Verbosity flags (`-v`, `-vv`, `-q`) provide
flexible logging across all commands.

→ [Workflows](https://winipedia.github.io/pyrig/configs/workflows/)
· [Branch Protection](https://winipedia.github.io/pyrig/configs/branch_protection/)

## CLI Commands

```bash
uv run pyrig init           # Full project initialization
uv run pyrig mkroot         # Create/update all config files
uv run pyrig mktests        # Generate test skeletons
uv run pyrig mkinits        # Create missing __init__.py files
uv run pyrig build          # Build artifacts (PyInstaller, etc.)
uv run pyrig protect-repo   # Configure repository protection
uv run my-project --help    # Your project's CLI
```

→ [CLI Reference](https://winipedia.github.io/pyrig/cli/)

## Documentation

| | |
|---|---|
| **[Getting Started](https://winipedia.github.io/pyrig/more/getting-started/)** | Complete setup guide |
| **[Full Documentation](https://winipedia.github.io/pyrig/)** | Comprehensive reference |
| **[Trade-offs](https://winipedia.github.io/pyrig/more/drawbacks/)** | What you give up and what you gain |
| **[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)** | AI-generated docs |
| **[Tutorials](https://www.youtube.com/@Winipedia-py/playlists)** | YouTube tutorials for pyrig |
