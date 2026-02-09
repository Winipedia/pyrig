# pyrig Documentation

<!-- rumdl-disable MD013 -->
<!-- tooling -->
[![pyrig](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Container](https://img.shields.io/badge/Container-Podman-A23CD6?logo=podman&logoColor=grey&colorA=0D1F3F&colorB=A23CD6)](https://podman.io/)
[![prek](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![MkDocs](https://img.shields.io/badge/MkDocs-Documentation-326CE5?logo=mkdocs&logoColor=white)](https://www.mkdocs.org/)
<!-- code-quality -->
[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![ty](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![pytest](https://img.shields.io/badge/tested%20with-pytest-46a2f1.svg?logo=pytest)](https://pytest.org/)
[![codecov](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
[![rumdl](https://img.shields.io/badge/markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
<!-- package-info -->
[![PyPI](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![Python](https://img.shields.io/badge/python-3.12|3.13|3.14-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)
<!-- ci/cd -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yml)
<!-- documentation -->
[![Documentation](https://img.shields.io/badge/Docs-GitHub%20Pages-black?style=for-the-badge&logo=github&logoColor=white)](https://Winipedia.github.io/pyrig)
<!-- rumdl-enable MD013 -->

---

> A Python toolkit to rig up your project that standardizes and automates project setup, configuration and development.

---

## Philosophy

pyrig provides **minimal best practices fully working defaults for everything a
project needs**. Every configuration, workflow, and tool is pre-configured and
working from day one. No templates, no boilerplate - just a complete, tested,
production-ready setup that lets you start coding immediately.

## Quick Start

```bash
# Create repository on GitHub, then clone it
git clone https://github.com/username/my-project.git
cd my-project

# Initialize with uv and pyrig
uv init
uv add pyrig
uv run pyrig init

# Push to GitHub
git push -u origin main
```

**New to pyrig?** See the [Getting Started Guide](more/getting-started.md) for
complete setup instructions including prerequisites, required tokens, and
detailed explanations.

---

## Documentation

### [CLI Documentation](cli/index.md)

Learn how pyrig's CLI system works, including command discovery, multi-package
support, and how to create your own commands.

### [Testing Documentation](tests/index.md)

Understand pyrig's testing framework, including mirrored test structure,
automatic fixture sharing, and autouse validation fixtures.

### [Builder Documentation](builders/index.md)

Create distributable artifacts with pyrig's builder system, including
PyInstaller executables and custom build processes.

### [Resources Documentation](resources/index.md)

Manage static files (images, configs, templates) that work seamlessly in both
development and PyInstaller executables.

### [Configuration Files Documentation](configs/index.md)

Understand pyrig's configuration file system, including automatic discovery,
validation, and creating custom config files. This is the main feature of pyrig
that generates a complete project structure for you, ready to use and start
developing your project.

### [Tool Wrappers Documentation](management/index.md)

pyrig wraps external tools (uv, git, ruff, pytest, etc.) in type-safe Python
classes. Learn how the Tool system works, what each wrapper does, and how to
customize tool behavior through subclassing.

### [Additional Information](more/index.md)

See more documentation about pyrig's drawbacks, how to get started, tooling
choices and a detailed example usage.

### [CodeWiki Documentation](https://codewiki.google/github.com/winipedia/pyrig)

AI-generated documentation for pyrig.
