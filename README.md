# pyrig

[![PyPI](https://img.shields.io/pypi/v/pyrig)](https://pypi.org/project/pyrig/)
[![Python](https://img.shields.io/pypi/pyversions/pyrig)](https://pypi.org/project/pyrig/)
[![License](https://img.shields.io/github/license/winipedia/pyrig)](https://github.com/winipedia/pyrig/blob/main/LICENSE)
[![CI](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml/badge.svg)](https://github.com/winipedia/pyrig/actions/workflows/health_check.yaml)

**pyrig** is a Python development toolkit that helps you **rig up** your Python projects by standardizing project configurations and automating testing workflows.

---

## Why pyrig?

**The problem:** Starting a new Python project means hours of setup — configuring linters, type checkers, CI/CD, pre-commit hooks, test infrastructure, and keeping it all in sync across projects.

**The solution:** pyrig handles it all automatically:

- **One command setup** — `uv run pyrig init` creates everything
- **Self-maintaining** — configs stay in sync, tests auto-generate, dependencies auto-update
- **Best practices enforced** — strict typing, all ruff rules, security scanning, branch protection

**Before pyrig:**
```
- Create pyproject.toml manually
- Configure ruff, mypy, pytest, bandit
- Write GitHub Actions workflows
- Set up pre-commit hooks
- Create test file structure
- Keep everything in sync... forever
```

**After pyrig:**
```bash
uv add pyrig && uv run pyrig init  # Done. Everything works.
```

---

## Quick Start

```bash
# 1. Create and clone a new GitHub repo
git clone https://github.com/your-username/my-project.git
cd my-project

# 2. Initialize with uv and add pyrig
uv init 
uv add pyrig

# 3. Run pyrig init (creates everything)
uv run pyrig init

# 4. Start coding - your project is ready
# - Write code in my_project/src/
# - Tests auto-generate when you run pytest
# - Pre-commit hooks auto-install
# - CI/CD workflows are ready

# 5. Commit and push
git add . && git commit -m "chore: init project" && git push
```

**That's it.** Your project now has linting, type checking, testing, CI/CD, and branch protection — all configured and working.

---

## Table of Contents

- [Why pyrig?](#why-pyrig)
- [Quick Start](#quick-start)
- [Requirements](#requirements)
- [Installation](#installation)
- [Architecture](#architecture)
- [Initialization](#initialization)
- [ConfigFile Machinery](#configfile-machinery)
- [CLI Commands](#cli-commands)
- [Repository Protection](#repository-protection)
- [Testing](#testing)
- [Building Artifacts](#building-artifacts)
- [Migrating Existing Projects](#migrating-existing-projects)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Alternatives Comparison](#alternatives-comparison)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Zero-Configuration Setup**: Opinionated, best-practice configurations for Python development tools
- **ConfigFile Machinery**: Automated system for discovering, creating, validating, and updating all configuration files
- **Automatic Test Generation**: Creates test skeletons that mirror your source code structure
- **Intelligent Fixture System**: Automatic discovery and loading of pytest fixtures across all packages
- **Strict Type Checking**: Enforces mypy strict mode with comprehensive type coverage
- **Code Quality Tools**: Pre-configured ruff (linting + formatting), mypy, bandit (security)
- **CI/CD Workflows**: GitHub Actions workflows for health checks, releases, and publishing
- **Repository Protection**: Automated GitHub branch protection and security settings
- **Dependency Management**: Automatic dependency updates with uv
- **Pre-commit Hooks**: Automated code quality checks before every commit with automatic installation
- **Artifact Building**: Extensible build system with PyInstaller support
- **Custom CLI**: Automatically generates CLI commands from your functions
- **Cross-Platform Testing**: Matrix testing across multiple OS and Python versions
- **Multi-Package Architecture**: Automatic discovery of configs, builders, fixtures, and resources across all packages depending on pyrig

---

## Requirements

- **Python**: 3.12 or higher
- **uv**: Package and dependency manager
- **Git**: Version control
- **GitHub**: For full CI/CD and repository protection features (optional but recommended)

---

## Installation

### From PyPI

```bash
pip install pyrig
# or
uv add pyrig
```

**Note**: pyrig should be added as a regular dependency, not a dev dependency, because the CLI and utility functions require runtime availability. While pyrig manages dev dependencies for tools like ruff, mypy, and pytest, it keeps itself as a regular dependency to ensure full functionality in all environments.

### From Source

```bash
git clone https://github.com/winipedia/pyrig.git
cd pyrig
uv sync
```

---

## Architecture

pyrig organizes your project into a clean, consistent structure:

```
my-project/
├── .github/workflows/          # CI/CD (health checks, releases, publishing)
├── my_project/                # Your package
│   ├── main.py                 # Entry point (CLI, PyInstaller)
│   ├── src/                    # Your source code goes here
│   │   ├── __init__.py
│   │   └── calculator.py       # Example: your modules
│   └── dev/                    # Development infrastructure and pyrig stuff
│       ├── cli/subcommands.py  # Custom CLI commands
│       ├── configs/            # Config file definitions
│       ├── artifacts/          # Build scripts & resources
│       └── tests/fixtures/     # Pytest fixtures
├── tests/                      # Test files (auto-generated)
│   ├── conftest.py
│   └── test_my_project/
│       └── test_src/
│           └── test_calculator.py
├── pyproject.toml              # Project config (managed by pyrig)
└── .pre-commit-config.yaml     # Pre-commit hooks (managed by pyrig)
```

**Key concepts:**
- **`src/`** — Your production code lives here
- **`dev/`** — Development and pyrig infrastructure
- **`tests/`** — Mirrors `src/` structure, auto-generated skeletons
- **ConfigFile Machinery** — Auto-discovers and manages all config files
- **Subclass overrides** — Customize any config by subclassing it

---

## Initialization

### Prerequisites

1. **Create a GitHub repository** for your project (e.g., `your-project`)

2. **Configure GitHub Secrets**
   - `REPO_TOKEN`: GitHub Fine-Grained Personal Access Token with permissions:
     - `contents:read and write` (needed to commit after release)
     - `administration:read and write` (needed to protect the repo)
   - `PYPI_TOKEN`: PyPI token for your project (only needed if publishing to PyPI)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-project.git
   cd your-project
   ```

2. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Initialize uv project**
   ```bash
   uv init 
   ```

4. **Add pyrig as a dependency**
   ```bash
   uv add pyrig
   ```

5. **Run pyrig initialization**
   ```bash
   uv run pyrig init
   ```

   **Note**: This will delete the root-level `main.py` created by `uv init` and replace it with a properly structured `your_project/main.py` inside the package.

6. **Commit and push changes**
   ```bash
   git add .
   git commit -m "chore: init project with pyrig"
   git push
   ```

---

## ConfigFile Machinery

The ConfigFile Machinery is pyrig's automated system for managing all configuration files. All configuration files are subclasses of `pyrig.dev.configs.base.base.ConfigFile` and are automatically discovered from `pkg/dev/configs/**` directories across all packages depending on pyrig.

**Key Features**:

- **Automatic Discovery**: Scans all `dev/configs/` directories across all packages depending on pyrig
- **Automatic Initialization**: Creates missing config files based on their class definitions
- **Automatic Validation**: Checks existing config files against their expected content
- **Automatic Updates**: Updates config files when their definitions change
- **Intelligent Subclass Discovery**: Only executes the most specific (leaf) implementations. If you subclass an existing config, only your custom subclass will be executed, preventing duplicates and ensuring your customizations take precedence.

**Note**: To prevent pyrig from managing a specific config file, make the file empty (the file must exist).

### Extending Configuration Files

The ConfigFile Machinery uses a **subset validation algorithm** that allows you to extend configuration files with custom settings while maintaining pyrig's required settings.

**Subset Validation Rules**:

- **Dictionaries**: All required keys must exist, but you can add additional keys
- **Lists**: All required items must exist (order doesn't matter), but you can add additional items
- **Values**: Required values must match exactly (unless they are nested structures)

**Example**:

If pyrig requires:
```toml
[tool.mypy]
strict = true
warn_redundant_casts = true
```

You can extend it with:
```toml
[tool.mypy]
strict = true
warn_redundant_casts = true
exclude = ["tests/fixtures/"]  # Your custom setting
plugins = ["pydantic.mypy"]     # Your custom setting
```

**Recommended Approach**: Subclass existing configs (e.g., `PyprojectConfigFile`) in your own `dev/configs/python/pyproject.py` file. When you subclass an existing config, only your subclass executes, ensuring your customizations take full control.

### ConfigFile Types

- **`ConfigFile`**: Base class for all config files
- **`CopyModuleConfigFile`**: Copies entire module content to a config file
- **`CopyModuleOnlyDocstringConfigFile`**: Copies only the docstring from a module
- **`PythonConfigFile`**: For Python source files
- **`YamlConfigFile`**: For YAML configuration files
- **`TomlConfigFile`**: For TOML configuration files

### Configuration Files Managed by the Machinery

The ConfigFile Machinery automatically manages the following configuration files:

#### `pyproject.toml`

Stores project metadata and dependencies. Automatically adds essential dev dependencies (ruff, mypy, pytest, pre-commit) with strict settings.

- **Automatic Version Stripping**: By default, pyrig strips version constraints from all dependencies (e.g., `requests>=2.0` becomes `requests`). This ensures you always get the latest compatible versions when running `uv lock --upgrade`.
- **When Updates Happen**: Dependencies are upgraded during `pyrig init` and via the `assert_dependencies_are_up_to_date` autouse session fixture (runs `uv sync`, then `uv lock --upgrade`).
- **Disabling Version Stripping**: To keep specific version constraints, subclass `PyprojectConfigFile` and override `should_remove_version_from_dep()` to return `False`:
  ```python
  # your_project/dev/configs/pyproject.py
  from pyrig.dev.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile

  class PyprojectConfigFile(BasePyprojectConfigFile):
      @classmethod
      def should_remove_version_from_dep(cls) -> bool:
          return False
  ```
- Enforces that GitHub repo name and cwd name are equal; hyphens in repo names are converted to underscores in package names

#### `pkg/py.typed`

Indicates that the package supports type checking.

#### `README.md`

Must start with `# <project_name>`. The rest of the content is up to you.

#### `LICENCE`

Empty file for you to add your own license.

#### `.experiment.py`

Empty file for experimentation. Git-ignored, not for production code.

#### `.python-version`

Set to the lowest supported Python version. Used by pyenv.

#### `.pre-commit-config.yaml`

Configured with the following hooks:

- `lint-code`: ruff check --fix
- `format-code`: ruff format
- `check-static-types`: mypy --exclude-gitignore
- `check-security`: bandit -c pyproject.toml -r .

Automatically installed during test session via autouse fixture.

**Note**: Heavy operations like `install-dependencies` and `create-root` run as autouse session fixtures during test execution, not as pre-commit hooks, to keep commits fast.

#### `.gitignore`

Pulls the latest [github/python.gitignore](https://github.com/github/gitignore/blob/main/Python.gitignore) and adds project-specific ignores.

#### `.env`

Empty file for environment variables. Git-ignored, used by python-dotenv.

#### `.github/workflows/health_check.yaml`

- **Triggers**: workflow_dispatch, pull_request, push to main, schedule (daily with staggered cron)
- **Purpose**: Matrix testing across different OS and Python versions
- **Staggered Cron Schedule**: To avoid test failures when multiple packages release on the same schedule, the cron time is staggered based on the package's position in the dependency chain. Packages with fewer dependencies on pyrig run earlier (starting at 1 AM UTC), with each additional dependency level adding 1 hour. This ensures that when dependencies release, dependent packages have time to pick up the new versions before their health checks run.

#### `.github/workflows/release.yaml`

- **Triggers**: workflow_dispatch, workflow_run (when health_check completes successfully on main)
- **Process**: Creates tag and changelog, creates GitHub release, builds and uploads artifacts, commits updates
- **Synchronization**: Keeps tags, package version, and PyPI in sync
- **Note**: Only runs after health check passes on main branch, so health check steps are not duplicated

#### `.github/workflows/publish.yaml`

- **Trigger**: Successful completion of release workflow
- **Purpose**: Publishes the package to PyPI
- **Note**: Empty the file to disable PyPI publishing

#### `pkg/main.py`

Main entry point for your application. Used by PyInstaller for building executables.

- **Usage**: `uv run your-pkg-name main` or `python -m your-pkg-name`

#### `pkg/src/`

Subfolder for organizing your source code, separating it from development infrastructure (`dev/`). Automatically created with an `__init__.py` file.

#### `pkg/dev/cli/subcommands.py`

Define custom CLI subcommands. Any function in this file is automatically added as a subcommand.

**Example**:
```python
def hello(name: str = "World") -> None:
    """Say hello to someone."""
    print(f"Hello, {name}!")

# Run with: uv run your-pkg-name hello --name Alice
```

#### `pkg/dev/configs/`

Define custom configuration files. Any subclass of `ConfigFile` is automatically discovered and initialized. Configs can be defined in any file in the `pkg/dev/configs` folder.

**Subclass Behavior**: If you subclass an existing `ConfigFile`, only your most specific subclass will be executed, preventing duplicates.

#### `pkg/dev/artifacts/builders/`

Define build scripts. Any subclass of `Builder` is automatically discovered and executed. Builders can be defined in any file in the `pkg/dev/artifacts/builders` folder.

**Subclass Behavior**: If you subclass an existing `Builder`, only your most specific subclass will be executed, preventing duplicate builds.

#### `pkg/dev/artifacts/resources/`

Directory for storing static resources (images, data files, etc.). Automatically included in PyInstaller builds.

- **Resource Access**: Use `get_resource_path()` to access resources at runtime
- **Automatic Discovery**: Resources from all packages depending on pyrig are automatically included

**Example**:
```python
from pyrig.src.resource import get_resource_path
import your_project.dev.artifacts.resources as resources

config_path = get_resource_path("config.json", resources)
data = config_path.read_text()
```

#### `pkg/dev/configs/python/resources_init.py`

Manages the `resources/__init__.py` file to ensure proper package initialization.

#### `pkg/dev/configs/testing/fixtures/`

Configuration files that manage the fixture system structure (scopes/session.py, scopes/package.py, scopes/module.py, scopes/class_.py, scopes/function.py).

#### `tests/conftest.py`

Automatically discovers and loads fixtures from all packages depending on pyrig. Fixtures are globally available across all tests without manual imports.

#### `tests/test_zero.py`

Empty test file to ensure pytest doesn't complain about missing tests during initial setup.

#### `tests/test_<pkg>/test_main.py`

Auto-generated test file that verifies the CLI entry point works correctly by running `uv run <pkg-name> --help`.

---


## CLI Commands

pyrig provides the following CLI commands:

```bash
pyrig --help

Usage: pyrig [OPTIONS] COMMAND [ARGS]...

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                            │
│ --show-completion             Show completion for the current shell, to copy it or customize the   │
│                               installation.                                                        │
│ --help                        Show this message and exit.                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────╮
│ main           Main entrypoint for the project.                                                    │
│ create-root    Creates the root of the project.                                                    │
│ create-tests   Create all test files for the project.                                              │
│ init           Set up the project.                                                                 │
│ build          Build all artifacts.                                                                │
│ protect-repo   Protect the repository.                                                             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

---

## Repository Protection

pyrig automatically configures comprehensive GitHub repository protection measures to enforce code quality, security, and collaboration best practices. The protection is applied via the `pyrig protect-repo` command, which is automatically run in CI/CD workflows.

### Repository Settings

The following repository-level settings are automatically configured:

| Setting | Configuration | Purpose |
|---------|--------------|---------|
| **Default Branch** | `main` | Standard default branch |
| **Delete Branch on Merge** | Enabled | Automatically deletes head branches after pull requests are merged |
| **Allow Update Branch** | Enabled | Allows updating pull request branches with the base branch |
| **Merge Commit** | Disabled | Prevents merge commits to maintain clean history |
| **Rebase Merge** | Enabled | Allows rebase and merge strategy |
| **Squash Merge** | Enabled | Allows squash and merge strategy |

### Branch Protection Rules

A comprehensive ruleset named "main protection" is applied to the default branch with the following protections:

#### Branch Modification Protections

- **Deletion Protection**: Prevents deletion of the protected branch
- **Non-Fast-Forward Protection**: Prevents force pushes and history rewrites
- **Creation Protection**: Controls branch creation patterns
- **Update Protection**: Restricts direct updates to the branch

#### Pull Request Requirements

- **Required Approving Reviews**: At least 1 approval required before merging
- **Dismiss Stale Reviews**: Automatically dismisses approvals when new commits are pushed
- **Code Owner Review**: Requires review from code owners (if CODEOWNERS file exists)
- **Last Push Approval**: Requires approval from someone other than the last person to push
- **Review Thread Resolution**: All review comments must be resolved before merging
- **Allowed Merge Methods**: Only squash and rebase merges are permitted

#### Code Quality Requirements

- **Required Linear History**: Enforces a linear commit history
- **Required Commit Signatures**: Requires commits to be signed (GPG/SSH signatures)
- **Required Status Checks**: All CI/CD checks must pass before merging
  - **Strict Status Checks**: Branch must be up-to-date with base branch before merging
  - **Required Workflow**: The `health_check.yaml` workflow must pass successfully

#### Bypass Actors

- Repository owner can bypass all protection rules when necessary

### Manual Application

The repository protection is automatically applied during CI/CD workflows, but you can also manually apply it:

```bash
# Set the REPO_TOKEN environment variable with a GitHub Personal Access Token
export REPO_TOKEN=your_github_token  # or add it to your .env file; pyrig picks it up automatically

# Run the protection command
uv run pyrig protect-repo
```

**Required Token Permissions**:
- `contents:read and write`
- `administration:read and write`

### CI/CD Integration

The `protect-repo` step is automatically included in both the `health_check.yaml` and `release.yaml` workflows, ensuring that protection rules are consistently applied and up-to-date with every CI/CD run.

---


## Testing

pyrig uses pytest as the test framework, which is automatically added as a dev dependency and configured in pyproject.toml.

### Test Structure

pyrig generates test skeletons that mirror your source code structure:

- **Module Level**: Each source module has a corresponding test module
- **Class Level**: Each source class has a corresponding test class
- **Function Level**: Each source function/method has a corresponding test function

### Automatic Test Generation

1. **Manual**: Run `uv run pyrig create-tests`
2. **Automatic**: An autouse session fixture creates missing tests when you run `pytest`

#### Fixture System

pyrig automatically discovers and loads fixtures from all packages depending on pyrig.
As long as they are defined in a file under `pkg/dev/tests/fixtures/`, they are automatically available to all tests.

**Built-in Fixtures**:
- `config_file_factory` - Factory for creating test config file classes
- `builder_factory` - Factory for creating test builder classes

**Creating Custom Fixtures**:

Add a `pkg/dev/tests/fixtures/` directory:

```
your_project/dev/tests/fixtures/
├── __init__.py
├── # Custom fixtures files
└── scopes/
    ├── __init__.py
    ├── session.py      # Session-level autouse fixtures
    └── ...
```

**Notes**:
- All fixtures are automatically discovered - no manual imports needed
- Autouse fixtures must be decorated with `@pytest.fixture(autouse=True)` or `@autouse_session_fixture`
- Fixtures from all packages are available to all tests

### Autouse Session Fixtures

Autouse session fixtures automatically enforce code quality and project conventions. These fixtures run once per test session before any tests execute.

#### `assert_root_is_correct`

Verifies and fixes all configuration files managed by the ConfigFile Machinery. If any config file is missing or incorrect, it automatically creates or corrects it. When running in GitHub Actions, it also ensures `.experiment.py` exists.

#### `assert_no_namespace_packages`

Ensures all packages have `__init__.py` files. If namespace packages are found (directories without `__init__.py`), they are automatically created. This prevents import issues and ensures proper package structure.

#### `assert_all_src_code_in_one_package`

Verifies that all source code is in a single package alongside the `tests` package. Also ensures the source package only contains the expected structure: `src/` and `dev/` subpackages, and a `main.py` module. This enforces a clean project structure.

#### `assert_src_package_correctly_named`

Checks that the source package name matches the project name defined in `pyproject.toml`. Hyphens in the project name are converted to underscores for the package name.

#### `assert_all_modules_tested`

Creates missing test modules, classes, and functions. For every module in the source package, it ensures a corresponding test module exists in the `tests` directory. Missing test skeletons are automatically generated.

#### `assert_no_unit_test_package_usage`

Prevents usage of the `unittest` package by scanning all Python files for `unittest` imports or usage. This enforces pytest as the sole testing framework for consistency.

#### `assert_dependencies_are_up_to_date`

Keeps dependencies current by running `uv self update` (when not in CI), `uv lock --upgrade`, and `uv sync`. This ensures you always have the latest compatible versions of all dependencies.

#### `assert_pre_commit_is_installed`

Ensures pre-commit hooks are installed by running `pre-commit install`. This guarantees that code quality checks run automatically before every commit.

#### `assert_src_runs_without_dev_deps`

Verifies that the source code runs correctly without dev dependencies installed. This fixture creates a temporary environment with only production dependencies, imports all source modules, and confirms they load successfully. This catches accidental imports of dev-only packages (like `pytest`) in production code.

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_your_project/test_calculator.py

# Run with coverage
uv run pytest --cov=your_project
```

### Disabling Tests

To disable tests for a specific module, empty the test file:
```bash
echo "" > tests/test_your_project/test_src/test_calculator.py
```

### Testing Utilities

pyrig provides several testing utilities in `pyrig.src.testing`:

**Assertions** (`pyrig.src.testing.assertions`):
- `assert_with_msg(expr, msg)` - Assert with a custom error message
- `assert_with_info(expr, expected, actual, msg)` - Assert with expected/actual values in the message
- `assert_isabstrct_method(method)` - Assert that a method is abstract

**Skip Decorators** (`pyrig.dev.tests.utils.decorators`):
- `@skip_fixture_test` - Skip tests for fixtures (cannot be called directly)
- `@skip_in_github_actions` - Skip tests that cannot run in GitHub Actions

**Fixture Scope Decorators** (`pyrig.dev.tests.utils.decorators`):
- `@function_fixture`, `@class_fixture`, `@module_fixture`, `@package_fixture`, `@session_fixture`
- `@autouse_function_fixture`, `@autouse_class_fixture`, `@autouse_module_fixture`, `@autouse_package_fixture`, `@autouse_session_fixture`

**Example**:
```python
from pyrig.src.testing.assertions import assert_with_msg
from pyrig.dev.tests.utils.decorators import autouse_session_fixture, skip_in_github_actions

@autouse_session_fixture
def my_fixture() -> str:
    return "test data"

@skip_in_github_actions
def test_local_only() -> None:
    assert_with_msg(True, "This should pass")
```

---

## Building Artifacts

pyrig provides an extensible build system. All builders are subclasses of `Builder`. When you run `pyrig build`, the system automatically discovers all `Builder` subclasses. If you subclass an existing builder, only your most specific subclass executes.

### Basic Builder

Create custom builders by subclassing `Builder` in `pkg/dev/artifacts/builders/`:

```python
from pathlib import Path
from pyrig.dev.artifacts.builders.base.base import Builder

class MyBuilder(Builder):
    """Custom builder for creating artifacts."""

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Build the project."""
        # Create your artifacts in temp_artifacts_dir
        artifact_path = temp_artifacts_dir / "my_artifact.txt"
        artifact_path.write_text("Hello, World!")
```

**Build artifacts**:
```bash
uv run pyrig build
```

Artifacts are placed in the `dist/` directory with platform-specific naming (e.g., `my_artifact-Linux.txt`, `my_artifact-Windows.txt`).

### PyInstaller Builder

pyrig includes a `PyInstallerBuilder` class for creating standalone executables.

1. **Implement your main function** in `your_project/main.py`
2. **Create an icon.png file** at `your_project/dev/artifacts/resources/icon.png` (256x256 recommended)
3. **Add resources** to `your_project/dev/artifacts/resources/` (optional)
4. **Subclass PyInstallerBuilder** in `your_project/dev/artifacts/builders/`:
   ```python
   from types import ModuleType
   from pyrig.dev.artifacts.builders.base.base import PyInstallerBuilder

   class MyAppBuilder(PyInstallerBuilder):
       """Build standalone executable with PyInstaller."""

       @classmethod
       def get_additional_resource_pkgs(cls) -> list[ModuleType]:
           """Return additional resource packages to include in the build."""
           return []  # Add your custom resource packages here
   ```

5. **Build**:
   ```bash
   uv run pyrig build
   ```

The builder automatically:
- Creates a single executable file
- Converts icon.png to platform-specific format
- Auto-discovers and includes resources from all packages depending on pyrig
- Names output with platform suffix (e.g., `your-project-Windows.exe`)

### Accessing Resources in Built Executables

Use `get_resource_path()` to access resources:

```python
from pyrig.src.resource import get_resource_path
import your_project.dev.artifacts.resources as resources

config_path = get_resource_path("config.json", resources)
data = json.loads(config_path.read_text())
```

### Multi-Package Architecture

pyrig supports multi-package architecture where multiple packages can depend on pyrig and automatically share configurations, builders, fixtures, and resources.

**Automatic Discovery**:

When you run pyrig commands or tests, it discovers components from all packages depending on pyrig:

1. **ConfigFile Machinery**: All `ConfigFile` subclasses from all `dev/configs/` directories
2. **Builders**: All `Builder` subclasses from all `dev/artifacts/builders/` directories
3. **Fixtures**: All pytest fixtures from all `dev/tests/fixtures/` directories
4. **Resources**: All files from all `dev/artifacts/resources/` directories

**Intelligent Subclass Discovery**:

- Only the most specific (leaf) subclasses are executed for configs and builders
- If you subclass a config or builder, only your subclass runs (not the parent)
- Fixtures use a different mechanism that loads all fixture modules without filtering

This enables:
- **Modular development**: Split your project into multiple packages with shared infrastructure
- **Reusable components**: Share configs, builders, fixtures, and resources across projects
- **Zero configuration**: Everything works automatically through dependency discovery



---

## Examples

### Example 1: Building a Calculator CLI

Let's build a real calculator CLI to see pyrig in action:

```bash
# Create project
git clone https://github.com/you/calc-cli.git && cd calc-cli
uv init  && uv add pyrig
uv run pyrig init
```

Now add your code:

```python
# calc_cli/src/calculator.py
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
```

```python
# calc_cli/dev/cli/subcommands.py
from calc_cli.src.calculator import add, multiply

def calc_add(a: float, b: float) -> None:
    """Add two numbers and print the result."""
    print(f"{a} + {b} = {add(a, b)}")

def calc_multiply(a: float, b: float) -> None:
    """Multiply two numbers and print the result."""
    print(f"{a} × {b} = {multiply(a, b)}")
```

Run tests (pyrig auto-generates test skeletons):

```bash
uv run pytest
# Creates tests/test_calc_cli/test_src/test_calculator.py with:
# - test_add()
# - test_multiply()
```

Use your CLI:

```bash
uv run calc-cli calc-add 2 3       # Output: 2 + 3 = 5.0
uv run calc-cli calc-multiply 4 5  # Output: 4 × 5 = 20.0
```

### Example 2: Adding a Custom Config File

Create a YAML config that pyrig manages automatically:

```python
# calc_cli/dev/configs/settings.py
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.base import YamlConfigFile

class SettingsConfigFile(YamlConfigFile):
    """Manages config/settings.yaml for the calculator."""

    @classmethod
    def get_filename(cls) -> str:
        return "settings"

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {
            "precision": 2,
            "default_operation": "add",
            "history_enabled": True,
        }
```

Run tests — pyrig creates `config/settings.yaml` automatically.

### Example 3: Building an Executable

```python
# calc_cli/dev/artifacts/builders/calculator_builder.py
from pyrig.dev.artifacts.builders.base.base import PyInstallerBuilder

class CalculatorBuilder(PyInstallerBuilder):
    """Build standalone calculator executable."""

    @classmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        return []  # Add any custom resource packages here
```

```bash
uv run pyrig build  # Creates dist/calculator executable
# or juts let the CI/CD do it for you by pushing to main
```

---

## Troubleshooting

### Common Issues

#### `pyrig some-cmd` command not found
```bash
# make sure you run in venv
uv run pyrig some-cmd
```

#### GitHub Actions permission errors
Ensure `REPO_TOKEN` secret has: `contents:read and write`, `administration:read and write`

---

## Contributing

1. **Report Issues**: [Open an issue](https://github.com/winipedia/pyrig/issues)
2. **Suggest Features**: [Start a discussion](https://github.com/winipedia/pyrig/discussions)
3. **Submit Pull Requests**: Fork, create feature branch, make changes, run tests, commit, push, open PR

### Development Setup

```bash
git clone https://github.com/winipedia/pyrig.git
cd pyrig
uv sync
uv run pytest
```

---

## License

pyrig is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

Copyright (c) 2025 Winipedia

---

## Links

- **Repository**: [github.com/winipedia/pyrig](https://github.com/winipedia/pyrig)
- **PyPI**: [pypi.org/project/pyrig](https://pypi.org/project/pyrig/)

---
