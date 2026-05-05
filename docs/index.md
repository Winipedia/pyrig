# pyrig Documentation

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

> pyrig is a python toolkit that rigs up your project by standardizing and automating project setup, configuration and maintenance.

---

<!-- rumdl-enable MD013 -->

## Philosophy

pyrig provides **minimal best practices fully working defaults for everything a
python project needs**. Every configuration, workflow, and tool is pre-configured
and working from the start. No templates, no boilerplate - just a complete, tested,
production-ready setup that lets you start developing code immediately.

## More Detailed Documentation

We are keeping the manual documentation restricted to the essentials,
if you want to know more about how pyrig works under the hood or you have
more specific questions about how to use it than we will explain here,
check out the [CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)
for AI-generated documentation about pyrig's codebase, where you can also ask
questions and get code explanations from the AI.

## Architecture Overview

For a high-level description of how pyrig works and some of its key features
and capabilities, see the [Architecture Overview](architecture.md).

## Getting Started

To get started with pyrig, check out the [Getting Started Guide](getting-started.md)
for a complete walkthrough of setting up a new python project from scratch with
pyrig.

## Scaffolding

To see the full file tree of a project scaffolded by pyrig and get detailed descriptions
of each file and configuration, see the [Scaffolding Documentation](scaffolding.md).

## Config File System

pyrig's config file system is built around the `ConfigFile` base class, which defines
how pyrig creates and validates files.
See the [Config File System Documentation](config-files.md) for details.

## CLI System

pyrig provides a fully functional, inheritable and automatically extensible
CLI that every project built on pyrig gets automatically.
Check out the [CLI System Documentation](cli.md) for more information.

## Mirror Test System

pyrig provides a system for automatically generating and maintaining test files
that mirror the structure of the source code and ensure everything is tested.
Find out more about it in the [Mirror Test System Documentation](mirror-tests.md).

## Test Fixture System

pyrig provides a system for automatically sharing and registering pytest fixtures
across all your tests.
See the [Test Fixture System Documentation](fixtures.md) for more information.

## Build System

pyrig provides an extensible build system for generating any artifact you want,
with PyInstaller integration for generating executables.
Check out the [Build System Documentation](build.md) for more details.

## CI/CD Pipeline

pyrig provides a complete end-to-end CI/CD pipeline with GitHub Actions and
integrated repository protection.
See the [CI/CD Pipeline Documentation](ci-cd.md) for a walkthrough of how
it works and how to customize it.
