# PyprojectConfigFile

## Overview

**File Location:** `pyproject.toml`
**ConfigFile Class:** `PyprojectConfigFile`
**File Type:** TOML
**Priority:** Priority (created early in init process)

The central configuration file for your Python project, containing project metadata, dependencies, build system configuration, and tool settings for all quality assurance tools. Unlike other Config Files this file is already expected to exist in the project via `uv init` and have essential fields populated like `name`, `version`, `description`, `requires-python`, `dependencies` in the `[project]` section. 

## Purpose

`pyproject.toml` is the heart of your pyrig project. It serves multiple critical functions:

- **Project Metadata** - Defines your project's name, version, description, and authors
- **Dependency Management** - Lists runtime and development dependencies (without version pins)
- **Build Configuration** - Configures uv as the build backend
- **Tool Configuration** - Centralizes settings for ruff, mypy, pytest, and bandit
- **CLI Entry Points** - Defines command-line scripts for your package

### Why pyrig manages this file

pyrig enforces opinionated defaults that ensure:
1. **Consistent code quality** across all pyrig projects
2. **Maximum strictness** in linting and type checking
3. **High test coverage** (90% minimum)
4. **Security scanning** on all code
5. **Reproducible builds** via uv

The file is created during `pyrig init` and updated by `pyrig mkroot` to keep configurations synchronized with pyrig's latest standards.

## Configuration Sections

### `[project]` - Project Metadata

Core metadata about your Python package following PEP 621 standards.

#### `name`

- **Type:** string
- **Default:** Derived from current directory name (e.g., `my-awesome-project`)
- **Required:** Yes
- **Purpose:** The distribution name for PyPI (uses hyphens)
- **Why pyrig sets it:** Automatically inferred from your repository/directory name

#### `version`

- **Type:** string
- **Default:** Preserved from existing file, or empty string for new projects
- **Required:** Yes (for publishing)
- **Purpose:** Semantic version of your package
- **Why pyrig sets it:** Allows you to manage versioning; pyrig autoincrements on release via `uv version --bump patch` in the `release.yaml` workflow in the GitHub Actions CI pipeline

#### `description`

- **Type:** string
- **Default:** Preserved from existing file, or empty string for new projects
- **Required:** No (but recommended)
- **Purpose:** One-line summary of your project
- **Why pyrig sets it:** You should customize this to describe your project. The value will automatically be added to the README.md file and also synchronized to the GitHub repository description. If you chnage it the your Readme will be updated on the next `pyrig mkroot` or via pytest autouse fixtures.

#### `readme`

- **Type:** string
- **Default:** `"README.md"`
- **Required:** No
- **Purpose:** Path to your README file for PyPI long description
- **Why pyrig sets it:** Standard convention; pyrig generates README.md
Pyrig addes some badges and your description to the README.md file. See more about the badges in the [README.md](readme-file.md) documentation.

#### `authors`

- **Type:** array of objects
- **Default:** `[{name = "YourGitHubUsername"}]`
- **Required:** No
- **Purpose:** List of project authors
- **Why pyrig sets it:** Automatically extracted from your git configuration or the username of the remote url in gits upstream. Remote takes precedence.

#### `license-files`

- **Type:** array of strings
- **Default:** `["LICENSE"]`
- **Required:** No
- **Purpose:** Paths to license files to include in distributions
- **Why pyrig sets it:** Points to the MIT LICENSE file pyrig generates
Pyrig auto generates a LICENSE file with the MIT license. You can change this to any other license you want. Pyrig does not enforce any specific license.

#### `requires-python`

- **Type:** string (version specifier)
- **Default:** `">=3.12"`
- **Required:** No (but strongly recommended)
- **Purpose:** Minimum Python version required
- **Why pyrig sets it:** Enforces modern Python (3.12+) for latest features and performance

#### `classifiers`

- **Type:** array of strings
- **Default:** Auto-generated based on `requires-python`
- **Example:** `["Programming Language :: Python :: 3.12", "Programming Language :: Python :: 3.13", ...]`
- **Required:** No
- **Purpose:** PyPI classifiers for package discovery
- **Why pyrig sets it:** Automatically includes all supported Python versions

#### `scripts`

- **Type:** object (mapping of command names to entry points)
- **Default:** `{<project-name> = "<package>.dev.cli.cli:main"}`
- **Example:** `{myproject = "myproject.dev.cli.cli:main"}`
- **Required:** No
- **Purpose:** Defines CLI commands installed with your package
- **Why pyrig sets it:** Creates a CLI command matching your project name

#### `dependencies`

- **Type:** array of strings
- **Default:** `[]` (empty for new projects)
- **Required:** No
- **Purpose:** Runtime dependencies (no version specifiers)
- **Why pyrig sets it:** Dependencies without versions; actual versions managed in `uv.lock`

**Important:** pyrig automatically strips version specifiers from dependencies.
Can be disabled by subclassing `PyprojectConfigFile` and overriding `should_remove_version_from_dep` to return `False` because this is a controversial convenience feature to automatically keep dependencies up to date.

### `[dependency-groups]` - Development Dependencies

Modern dependency groups following PEP 735.

#### `dev`

- **Type:** array of strings
- **Default:** `["pyrig-dev"]`
- **Required:** Yes (for pyrig projects)
- **Purpose:** Development-only dependencies (testing, linting, etc.)
- **Why pyrig sets it:** Includes `pyrig-dev` which provides all development tools, like `pytest`, `ruff`, `mypy`, `bandit`, etc.

**Important:** Like runtime dependencies, dev dependencies have their versions stripped.

### `[build-system]` - Build Configuration

Defines how your package is built following PEP 517/518.

#### `requires`

- **Type:** array of strings
- **Default:** `["uv_build"]`
- **Required:** Yes
- **Purpose:** Build dependencies
- **Why pyrig sets it:** Uses uv's fast build backend

#### `build-backend`

- **Type:** string
- **Default:** `"uv_build"`
- **Required:** Yes
- **Purpose:** The build backend to use
- **Why pyrig sets it:** uv provides the fastest, most modern build experience

### `[tool.uv.build-backend]` - uv Build Configuration

Configuration specific to uv's build backend.

#### `module-name`

- **Type:** string
- **Default:** Package name derived from project name (e.g., `my_awesome_project`)
- **Required:** Yes
- **Purpose:** The Python package name (uses underscores)
- **Why pyrig sets it:** Automatically converts project name to valid Python identifier

#### `module-root`

- **Type:** string
- **Default:** `""`
- **Required:** Yes
- **Purpose:** Root directory for the module (empty means project root)
- **Why pyrig sets it:** Standard layout with package at project root

### `[tool.ruff]` - Ruff Linter and Formatter

Configuration for ruff, the extremely fast Python linter and formatter.

#### `exclude`

- **Type:** array of strings
- **Default:** `[".*", "**/migrations/*.py"]`
- **Required:** No
- **Purpose:** Patterns for files/directories to exclude from linting
- **Why pyrig sets it:** Excludes hidden files and database migrations (common pattern)

### `[tool.ruff.lint]` - Ruff Linting Rules

#### `select`

- **Type:** array of strings
- **Default:** `["ALL"]`
- **Required:** No
- **Purpose:** Which linting rules to enable
- **Why pyrig sets it:** Enables ALL ruff rules for maximum code quality

This is pyrig's most opinionated choice - enabling every single ruff rule ensures:
- Consistent code style
- Best practices enforcement
- Security issue detection
- Performance optimizations
- Documentation completeness

#### `ignore`

- **Type:** array of strings
- **Default:** `["D203", "D213", "COM812", "ANN401"]`
- **Required:** No
- **Purpose:** Specific rules to disable
- **Why pyrig sets it:**
  - `D203` - Conflicts with D211 (blank line before class)
  - `D213` - Conflicts with D212 (multi-line summary position)
  - `COM812` - Can conflict with formatter
  - `ANN401` - Allows `Any` type (sometimes necessary)

#### `fixable`

- **Type:** array of strings
- **Default:** `["ALL"]`
- **Required:** No
- **Purpose:** Which rules can be auto-fixed
- **Why pyrig sets it:** Allows ruff to automatically fix all fixable issues

#### `per-file-ignores`

- **Type:** object (mapping of file patterns to ignored rules)
- **Default:** `{"**/tests/**/*.py" = ["S101"]}`
- **Required:** No
- **Purpose:** Ignore specific rules for specific files
- **Why pyrig sets it:** Allows `assert` statements in tests (S101 = use of assert)

#### `pydocstyle.convention`

- **Type:** string
- **Default:** `"google"`
- **Required:** No
- **Purpose:** Docstring style convention
- **Why pyrig sets it:** Google style is clean, readable, and widely adopted

### `[tool.mypy]` - Mypy Type Checker

Configuration for mypy static type checker.

#### `strict`

- **Type:** boolean
- **Default:** `true`
- **Required:** No
- **Purpose:** Enable all strict type checking options
- **Why pyrig sets it:** Maximum type safety catches bugs before runtime

#### `warn_unreachable`

- **Type:** boolean
- **Default:** `true`
- **Required:** No
- **Purpose:** Warn about unreachable code
- **Why pyrig sets it:** Catches dead code and logic errors

#### `show_error_codes`

- **Type:** boolean
- **Default:** `true`
- **Required:** No
- **Purpose:** Show error codes in messages
- **Why pyrig sets it:** Makes it easier to selectively ignore specific errors

#### `files`

- **Type:** string
- **Default:** `"."`
- **Required:** No
- **Purpose:** Which files/directories to type check
- **Why pyrig sets it:** Check everything in the project

### `[tool.pytest.ini_options]` - Pytest Configuration

Configuration for pytest test runner.

#### `testpaths`

- **Type:** array of strings
- **Default:** `["tests"]`
- **Required:** No
- **Purpose:** Directories to search for tests
- **Why pyrig sets it:** Standard location for test files

#### `addopts`

- **Type:** string
- **Default:** `"--cov=<package> --cov-report=term-missing --cov-fail-under=90"`
- **Required:** No
- **Purpose:** Additional command-line options for pytest
- **Why pyrig sets it:** Enforces 90% code coverage requirement

Options breakdown:
- `--cov=<package>` - Measure coverage for your package
- `--cov-report=term-missing` - Show which lines aren't covered
- `--cov-fail-under=90` - Fail if coverage drops below 90%

### `[tool.bandit]` - Bandit Security Scanner

Configuration for bandit security linter.

#### `exclude_dirs`

- **Type:** array of strings
- **Default:** `[".*"]`
- **Required:** No
- **Purpose:** Directories to exclude from security scanning
- **Why pyrig sets it:** Skip hidden directories (like `.git`, `.venv`)

### `[tool.bandit.assert_used]` - Assert Usage Check

#### `skips`

- **Type:** array of strings
- **Default:** `["*/tests/*.py"]`
- **Required:** No
- **Purpose:** Files where assert statements are allowed
- **Why pyrig sets it:** Asserts are normal in tests, but discouraged in production code

## Default Configuration

Here's a complete example of what pyrig generates for a project named `my-awesome-project`:

```toml
[project]
name = "my-awesome-project"
version = "0.1.0"
description = "My awesome Python project"
readme = "README.md"
authors = [
    {name = "YourGitHubUsername"},
]
license-files = ["LICENSE"]
requires-python = ">=3.12"
classifiers = [
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
dependencies = [
    "pyrig",
]

[project.scripts]
my-awesome-project = "pyrig.dev.cli.cli:main"

[dependency-groups]
dev = [
    "pyrig-dev",  # Includes all dev tools
]

[build-system]
requires = ["uv_build"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "my_awesome_project"
module-root = ""

[tool.ruff]
exclude = [".*", "**/migrations/*.py"]

[tool.ruff.lint]
select = ["ALL"]  # All rules enabled
ignore = ["D203", "D213", "COM812", "ANN401"]
fixable = ["ALL"]

[tool.ruff.lint.per-file-ignores]
"**/tests/**/*.py" = ["S101"]  # Allow asserts in tests

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.mypy]
strict = true
warn_unreachable = true
show_error_codes = true
files = "."

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=my_awesome_project --cov-report=term-missing --cov-fail-under=90"

[tool.bandit]
exclude_dirs = [".*"]

[tool.bandit.assert_used]
skips = ["*/tests/*.py"]
```

## Customization
As long as you do not chnage a setting that is defaulkt by pyrig, you can customize this file as you see fit. Pyrig will not overwrite your changes.

However I recommend overwriting config files via subclassing the relevant config file class rather than editing the file directly. This allows you to keep your customizations in sync with pyrig's latest standards and also allow pyrig to manage them.

For exmaple if you want to change the version stripping behavior, you can subclass `PyprojectConfigFile` and override the `should_remove_version_from_dep` method.

```python
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class CustomPyprojectConfigFile(PyprojectConfigFile):
    @classmethod
    def should_remove_version_from_dep(cls) -> bool:
        return False
```

Or if you want to add a new dev dependency, you can subclass `PyprojectConfigFile` and override the `get_standard_dev_dependencies` method.

```python
from pyrig.dev.configs.pyproject import PyprojectConfigFile


class CustomPyprojectConfigFile(PyprojectConfigFile):
    @classmethod
    def get_standard_dev_dependencies(cls) -> list[str]:
        return super().get_standard_dev_dependencies() + ["black"]
```
