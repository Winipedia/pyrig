# pyrig

<!-- project-status -->
[![CI](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/health_check.yml?label=CI&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/health_check.yml)
[![CD](https://img.shields.io/github/actions/workflow/status/Winipedia/pyrig/release.yml?label=CD&logo=github)](https://github.com/Winipedia/pyrig/actions/workflows/release.yml)
[![ProjectTester](https://codecov.io/gh/Winipedia/pyrig/branch/main/graph/badge.svg)](https://codecov.io/gh/Winipedia/pyrig)
<!-- code-quality -->
[![ByteOrderMarkerFormatter](https://img.shields.io/badge/BOM-fix--byte--order--marker-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![CaseConflictChecker](https://img.shields.io/badge/case--conflict-check--case--conflict-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![DependencyChecker](https://img.shields.io/badge/dependencies-deptry-blue)](https://github.com/osprey-oss/deptry)
[![EndOfFileFormatter](https://img.shields.io/badge/EOF-end--of--file--fixer-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![EndOfLineFormatter](https://img.shields.io/badge/EOL-mixed--line--ending-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![JSONFormatter](https://img.shields.io/badge/JSON-pretty--format--json-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![JSONLinter](https://img.shields.io/badge/JSON-check--json-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![LargeFileChecker](https://img.shields.io/badge/large--files-check--added--large--files-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![MarkdownLinter](https://img.shields.io/badge/Markdown-rumdl-darkgreen)](https://github.com/rvben/rumdl)
[![MergeConflictChecker](https://img.shields.io/badge/merge--conflict-check--merge--conflict-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![ModuleTestNamingChecker](https://img.shields.io/badge/test--naming-name--tests--test-blue)](https://github.com/pre-commit/pre-commit-hooks)
[![PythonLinter](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![SecretsChecker](https://img.shields.io/badge/secrets-detect--secrets-blue)](https://github.com/Yelp/detect-secrets)
[![SecurityChecker](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![ShellFormatter](https://img.shields.io/badge/shell-shfmt-orange)](https://github.com/mvdan/sh)
[![ShellLinter](https://img.shields.io/badge/shell-shellcheck-blue)](https://github.com/koalaman/shellcheck)
[![SpellChecker](https://img.shields.io/badge/spell--check-typos-blue)](https://github.com/crate-ci/typos)
[![TOMLLinter](https://img.shields.io/badge/TOML-tombi-blueviolet)](https://github.com/tombi-toml/tombi)
[![TrailingWhitespaceFormatter](https://img.shields.io/badge/whitespace-trailing--whitespace--fixer-orange)](https://github.com/pre-commit/pre-commit-hooks)
[![TypeChecker](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ty/main/assets/badge/v0.json)](https://github.com/astral-sh/ty)
[![YAMLLinter](https://img.shields.io/badge/YAML-ryl-red)](https://github.com/owenlamont/ryl)
<!-- tooling -->
[![PackageManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Pyrigger](https://img.shields.io/badge/built%20with-pyrig-3776AB?logo=buildkite&logoColor=black)](https://github.com/Winipedia/pyrig)
[![RemoteVersionController](https://img.shields.io/github/stars/Winipedia/pyrig?style=social)](https://github.com/Winipedia/pyrig)
[![VersionControlHookManager](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/j178/prek/master/docs/assets/badge-v0.json)](https://github.com/j178/prek)
[![VersionController](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)](https://git-scm.com)
<!-- project-info -->
[![DocsBuilder](https://img.shields.io/badge/Documentation-zensical-326CE5)](https://Winipedia.github.io/pyrig)
[![PackageIndex](https://img.shields.io/pypi/v/pyrig?logo=pypi&logoColor=white)](https://pypi.org/project/pyrig)
[![ProgrammingLanguage](https://img.shields.io/pypi/pyversions/pyrig)](https://www.python.org)
[![License](https://img.shields.io/github/license/Winipedia/pyrig)](https://github.com/Winipedia/pyrig/blob/main/LICENSE)

<!-- rumdl-disable MD013 -->
---

> A tool that standardizes and automates Python project setup, configuration, development, and maintenance.

---

<!-- rumdl-enable MD013 -->

## What is pyrig?

pyrig is a package and tool that **rigs up** Python projects with Convention-over-Configuration.
It scaffolds a complete, fully configured, installed and working Python project
with everything a modern Python project **should** have and makes the process of
developing and maintaining it more seamless and efficient by automating things
like configuration management, CLI generation, testing infrastructure, and more.

## Requirements

- Python 3.12+
- Git
- uv

## Quick Start

```bash
uv init my-project --python 3.12
cd my-project
uv add pyrig --dev
uv run pyrig init
```

See the [Getting Started Guide](https://Winipedia.github.io/pyrig/getting-started)
for detailed setup instructions to also fully integrate with GitHub and
CI/CD from the start.

## Features

### [Project Scaffolding & Initialization](https://Winipedia.github.io/pyrig/scaffolding)

The `pyrig init` command generates a complete project, this includes, but is not
limited to:

- Standardized directory structure
- Fully configured dev tools (linters, formatters, type checkers, test
frameworks, git hooks, etc.)
- End-to-end CI/CD pipeline with GitHub Actions and integrated repository protection
- Complete and working CLI
- And much more...

### [File & Configuration Management](https://Winipedia.github.io/pyrig/config-files)

pyrig manages and validates project files via classes, where every file is treated
as a data structure (dict or list), the content is loaded and validated against
the declared state in the class. This makes it possible to override and adjust
any and all behavior of pyrig via subclassing said classes. pyrig will automatically
discover and use your custom classes without any additional configuration.
Run `pyrig mk subcls` to generate a subclass for any pyrig class.
Run `pyrig sync` to create or update all config files at once.

### [Automatic CLI](https://Winipedia.github.io/pyrig/cli)

`pyrig init` sets up a CLI for your project that works immediately.
Generate and add new commands by running `pyrig mk cmd <name>`.
An automatic version command is included that shows the version of your project.
Run `my-project version` to see it in action.

### [Mirror Test Structure](https://Winipedia.github.io/pyrig/mirror-tests)

Generate test skeletons with `pyrig sync`.
This will generate test skeletons for all source modules
and update them automatically as your project evolves.

### [Plugin Architecture](https://Winipedia.github.io/pyrig/architecture)

Override and customize any and all behavior to suit your project's needs.
pyrig's classes are designed for inheritance and composition, allowing you to
create custom configurations, tools, and more by subclassing and simply
overriding methods. pyrig will automatically discover and use your custom classes
without any additional configuration.
Run `pyrig mk subcls` to generate a subclass for any pyrig class.
Create your own plugins this way to extend pyrig's functionality.

### [CI/CD & Repository Protection](https://Winipedia.github.io/pyrig/ci-cd)

Pyrig generates GitHub Actions workflows for CI/CD which automatically test
and release your code. They also configure and apply repository protection
settings and protection rulesets. Push your code to GitHub after initialization
and see it in action.

## [Commands](https://Winipedia.github.io/pyrig/cli/#pyrigs-own-commands)

Run `pyrig --help` to see a list of all available commands and their usage.
Run `pyrig <command> --help` for more information about a specific command and
its usage.
Run `my-project --help` to see the automatically generated CLI for your project.

## [Comparisons](https://Winipedia.github.io/pyrig/comparisons)

pyrig isn't the only tool in this field. See how it compares to other popular tools
like cookiecutter, copier or pyscaffold.

## Documentation

| | |
|---|---|
| **[Full Documentation](https://Winipedia.github.io/pyrig)** | The manually written documentation |
| **[CodeWiki](https://codewiki.google/github.com/winipedia/pyrig)** | AI-generated documentation |
| **[Tutorials](https://www.youtube.com/@Winipedia-py/playlists)** | YouTube tutorials for pyrig |
