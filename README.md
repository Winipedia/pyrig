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

### Project Scaffolding & Idempotent Init

pyrig's `init` command scaffolds a complete, production-ready Python project
(source layout, tests, CI/CD, docs, configs, working CLI) and is safe to re-run
due to its idempotency. See the [Getting Started Guide](https://winipedia.github.io/pyrig/more/getting-started/) for details and
[full generated project structure](https://winipedia.github.io/pyrig/more/getting-started/#what-you-get)
for the full layout.

### Config File System

pyrig generated files are modeled as Python classes in pyrig. They validate and
merge automatically. Extend or override configurations by subclassing. You can
create your own Config File classes as well and pyrig will handle them for you,
you just need to define behaviour. See the
[Config Architecture](https://winipedia.github.io/pyrig/configs/architecture/)
documentation for details.

### Dynamic Multi-Package CLI Discovery

pyrig `init` also sets up a CLI for your project, that works out of the box and
can be extended with custom commands very easily. Just define a function in
`<package>.rig.cli.subcommands` and it will be available as a CLI command
automatically. pyrig also supports multi-package CLI discovery via defining a
function in `<package>.rig.cli.shared_subcommands` which will be available in
all downstream packages in the dependency chain, just like the version command
provided by pyrig. See the [CLI docs](https://winipedia.github.io/pyrig/cli/)
for details.

### Pytest Enforcement, Autouse Fixtures && Test Skeleton Generation

pyrig comes with pytest configured as the test runner, and includes autouse
fixtures that enforce best practices, validate project invariants, and
auto-generate missing test skeletons. To generate test skeletons for missing
tests, just run `uv run pyrig mktests` and pyrig will create test skeletons for
any missing tests based on the source code structure. See the
[Test Structure docs](https://winipedia.github.io/pyrig/tests/structure/) for
more details. pyrig's autouse fixtures check some things like ensuring that all
source files have corresponding test files, that all packages have `__init__.py`
files, and that Config Files are correct. They also auto-upgrade your
dependencies via `uv lock --upgrade` to the latest allowed version defined in
your `pyproject.toml`. See the
[Autouse fixtures](https://winipedia.github.io/pyrig/tests/autouse/)
documentation for details on all the autouse fixtures provided by pyrig.

### Multi-Project Inheritance Model

pyrig allows you to override and customize almost any and all behavior in a
project via its `.I` inheritance system. Just define a class that inherits from
the pyrig provided class, override the behaviour you want to change, and pyrig
will use your implementation instead of the default one. This applies to all
Config Files, CLI commands, tools, builders, and more. You can even define your
own custom Config Files and pyrig will handle them for you as long as they
inherit from `ConfigFile`. This is a very powerful feature and a bit hard to
explain easily, so please check out the documentation for more details and
examples. In our opinion, the best thing this enables is that you can define
your very own personal pyrig package that defines your own standards and tools,
and then just add it as a dependency to all your projects to have those
standards and tools available everywhere automatically by just running
`uv add my-pyrig-package` and `uv run pyrig init` in each project, which is
pretty amazing. See the
[Tool Architecture docs](https://winipedia.github.io/pyrig/tools/architecture/#two-extension-mechanisms)
and the
[Config Architecture docs](https://winipedia.github.io/pyrig/configs/architecture/#automatic-discovery)
for details and examples.

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

### Logging & CLI Controls

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
