# pyrig

<!-- security -->
[![SecurityChecker](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![DependencyAuditor](https://img.shields.io/badge/security-pip--audit-blue?logo=python)](https://github.com/pypa/pip-audit)
<!-- tooling -->
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig?style=social)](https://github.com/Winipedia/pyrig)
[![ContainerEngine](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io)
[![Pyrigger](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
<!-- documentation -->
[![DocsBuilder](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org)
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://Winipedia.github.io/pyrig)
<!-- code-quality -->
[![VersionControlHookManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![MarkdownLinter](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
<!-- project-info -->
[![PackageIndex](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)
<!-- testing -->
[![ProjectTester](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org)
[![ProjectCoverageTester](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yml)

<!-- rumdl-disable MD013 -->
---

> Pyrig is a toolkit that standardizes and automates Python project setup, configuration, development, and maintenance.

---

<!-- rumdl-enable MD013 -->

## What is pyrig?

pyrig is a package and tool that **rigs up** your project.
It scaffolds and initializes a complete, fully configured, installed and
working Python project with one command and makes the process of developing
and maintaining it more seamless and efficient by automating things like
configuration management, CLI generation, testing infrastructure, and more.

## Requirements

- Python 3.12+
- Git
- uv

## Quick Start

```bash
uv init
uv add pyrig
uv run pyrig init
```

See the [Getting Started Guide](https://winipedia.github.io/pyrig/getting-started)
for detailed setup instructions to also fully integrate with GitHub and
CI/CD from the start.

## Features

### [Project Scaffolding & Initialization](https://winipedia.github.io/pyrig/scaffolding)

`pyrig init` generates a complete project in one command that works out of the box.
This includes everything a modern python project needs:

- Standardized directory structure
- Fully configured dev tools (linters, formatters, type checkers, test
frameworks, git hooks, etc.)
- End-to-end CI/CD pipeline with GitHub Actions and integrated repository protection
- Complete and working CLI
- And much more...

### [File & Configuration Management](https://winipedia.github.io/pyrig/config-files)

Every generated file is backed by a Python class that validates and merges
automatically. Override any config by subclassing, or define entirely new
config files — pyrig discovers and manages them for you.
Run `pyrig mkroot` to create or update all config files at once.
Run `pyrig subcls` to generate a subclass for overriding a specific file.

### [Automatic CLI](https://winipedia.github.io/pyrig/cli)

`pyrig init` sets up a CLI for your project that works immediately.
Generate and add new commands by running `pyrig mkcmd <name>`.
An automatic version command is included that shows the version of your project.
Run `my-project version` to see it in action.

### [Mirror Test Generation & Maintenance](https://winipedia.github.io/pyrig/mirror-tests)

Generate test skeletons with `pyrig mktests`.
This will generate test skeletons for all source modules
and update them automatically as your project evolves.

### [Test Fixtures](https://winipedia.github.io/pyrig/fixtures)

pyrig enables automatic sharing and registration of pytest fixtures.
Run `pyrig mkfixture <name>` to generate a new fixture that is
automatically registered and available across all your tests.

### [Build Artifacts](https://winipedia.github.io/pyrig/build)

PyInstaller integration and extensible build system for generating executables,
distributable packages, and more.
Run `pyrig subcls` to create a custom builder for your specific build needs.
Run `pyrig build` to execute the build process and generate artifacts.
Run `pyrig resources` to create a resources package for your project.

### [Multi-Package Inheritance and Extensibility Architecture](https://winipedia.github.io/pyrig/architecture)

Override and customize any and all behaviour to suit your project's needs.
pyrig's classes are designed for inheritance and composition, allowing you to
create custom configurations, tools, builders, and more by subclassing and simply
overriding methods. pyrig will automatically discover and use your custom classes
without any additional configuration.
Run `pyrig subcls` to generate a subclass for any pyrig class.

### [CI/CD & Repository Protection](https://winipedia.github.io/pyrig/ci-cd)

Pyrig generates GitHub Actions workflows for CI/CD and automatically configures
and applies repository protection settings and branch protection rules to ensure
your repository is protected.
Run `pyrig protect-repo` to apply or update repository protection settings or
simply use the fully working CI/CD pipeline to apply them automatically.

## Commands

Run `pyrig <command> --help` for more information about a specific command and
its usage.

```bash
uv run pyrig init                    # Full project initialization
uv run pyrig mkroot                  # Create/update all concrete config files
uv run pyrig mktests                 # Generate test skeletons
uv run pyrig mkinits                 # Create missing __init__.py files
uv run pyrig mkfixture <name>        # Generate a new pytest fixture
uv run pyrig mkcmd <name>            # Create a new CLI subcommand stub
uv run pyrig subcls                  # generate and override subclasses
uv run pyrig build                   # Build artifacts (PyInstaller, etc.)
uv run pyrig resources               # Scaffold the resources package
uv run pyrig protect-repo            # Configure repository protection
uv run pyrig scratch                 # Execute the project's .scratch.py file
uv run pyrig rmpyc                   # Remove __pycache__ directories
uv run pyrig version                 # Show pyrig version
uv run my-project --help             # Your project's CLI
uv run my-project version            # Show your project's version
```

## Documentation

| | |
|---|---|
| **[Full Documentation](https://winipedia.github.io/pyrig)** | The manually written documentation |
| **[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)** | AI-generated documentation |
| **[Tutorials](https://www.youtube.com/@Winipedia-py/playlists)** | YouTube tutorials for pyrig |
