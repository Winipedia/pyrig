# Home

<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/deploy.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/deploy.yml)
<!-- testing -->
[![CoverageTester](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
[![ProjectTester](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org)
<!-- code-quality -->
[![DependencyAuditor](https://img.shields.io/badge/security-pip--audit-blue?logo=python)](https://github.com/pypa/pip-audit)
[![DependencyChecker](https://img.shields.io/badge/dependencies-deptry-blue)](https://github.com/osprey-oss/deptry)
[![MarkdownLinter](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SecretsChecker](https://img.shields.io/badge/secrets-detect--secrets-blue)](https://github.com/Yelp/detect-secrets)
[![SecurityLinter](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![SpellChecker](https://img.shields.io/badge/spell--check-typos-blue)](https://github.com/crate-ci/typos)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![VersionControlHookManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
<!-- tooling -->
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pyrigger](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig?style=social)](https://github.com/Winipedia/pyrig)
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
<!-- project-info -->
[![DocsBuilder](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://Winipedia.github.io/pyrig)
[![PackageIndex](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)

<!-- rumdl-disable MD013 -->
---

> A tool that standardizes and automates Python project setup, configuration, development, and maintenance.

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
more specific questions about how to use it than we explain here, check out the
[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig) for AI-generated
documentation about pyrig's codebase, where you can also ask questions and get
more detailed explanations from the AI.

## Architecture Overview

For a high-level description of how pyrig works and some of its key features
and capabilities, see the [Architecture Overview](architecture.md).

## Getting Started

To get started with pyrig, check out the [Getting Started Guide](getting-started.md)
for a complete walkthrough of setting up a new python project from scratch with
pyrig.

## Plugins

pyrig has a range of plugins that extend your project with extra capabilities —
publishing to PyPI, building executables, container images, coverage uploads,
and more. Just add one as a dev dependency and it wires itself in automatically.
Check them out in the [Plugins Documentation](plugins.md).

## Scaffolding

To see the full file tree of a project scaffolded by pyrig and get detailed descriptions
of each file and configuration, see the [Scaffolding Documentation](scaffolding.md).

## Config File System

pyrig's config file system is built around the `ConfigFile` base class, which defines
how pyrig creates and validates files.
See the [Config File System Documentation](config-files.md) for details.

## Tool System

Every external CLI tool pyrig interacts with is wrapped in a `Tool` subclass with
typed command builders, badge metadata, and full override support.
See the [Tool System Documentation](tools.md) for details.

## CLI System

pyrig provides a fully functional, inheritable and automatically extensible
CLI that every project built on pyrig gets automatically.
Check out the [CLI System Documentation](cli.md) for more information.

## Mirror Test System

pyrig provides a system for automatically generating and maintaining test files
that mirror the structure of the source code and ensure everything is tested.
Find out more about it in the [Mirror Test System Documentation](mirror-tests.md).

## CI/CD Pipeline

pyrig provides a complete end-to-end CI/CD pipeline with GitHub Actions and
integrated repository protection.
See the [CI/CD Pipeline Documentation](ci-cd.md) for a walkthrough of how
it works and how to customize it.
