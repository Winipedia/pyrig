# pyrig

**pyrig** is a Python development toolkit that helps you **rig up** your Python projects by standardizing project configurations and automating testing workflows. It eliminates boilerplate setup work by providing opinionated, best-practice configurations for linting, type checking, testing, and CI/CD—allowing you to focus on writing code instead of configuring tools.

Built for Python 3.12+ projects using uv and GitHub, pyrig automatically generates project structure, creates test skeletons that mirror your source code, and maintains configuration files for tools like ruff, mypy, pytest, and pre-commit hooks.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Initialization](#initialization)
- [Configuration Files](#configuration-files)
- [CLI Commands](#cli-commands)
- [Repository Protection](#repository-protection)
- [Testing](#testing)
- [Building Artifacts](#building-artifacts)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
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

## Quick Start

```bash
# Create a new GitHub repository
# add REPO_TOKEN and PYPI_TOKEN to secrets as needed (more info below)
# Clone it locally
git clone https://github.com/your-username/your-project.git
cd your-project

# Initialize uv project
uv init --python 3.12 # 3.12 is the minimum supported version

# Add pyrig
uv add pyrig

# Initialize pyrig (creates all config files, tests, and runs setup)
uv run pyrig init

# Commit and push
git add .
git commit -m "chore: init project with pyrig"
git push
```

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
   uv init --python 3.12
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

#### `experiment.py`

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

#### `pkg/dev/configs/configs.py`

Define custom configuration files. Any subclass of `ConfigFile` is automatically discovered and initialized. Configs can be defined in any file in the `pkg/dev/configs` folder.

**Subclass Behavior**: If you subclass an existing `ConfigFile`, only your most specific subclass will be executed, preventing duplicates.

#### `pkg/dev/artifacts/builder/builder.py`

Define build scripts. Any subclass of `Builder` is automatically discovered and executed. Builders can be defined in any file in the `pkg/dev/artifacts/builder` folder.

**Subclass Behavior**: If you subclass an existing `Builder`, only your most specific subclass will be executed, preventing duplicate builds.

#### `pkg/dev/artifacts/resources/`

Directory for storing static resources (images, data files, etc.). Automatically included in PyInstaller builds.

- **Resource Access**: Use `get_resource_path()` to access resources at runtime
- **Automatic Discovery**: Resources from all packages depending on pyrig are automatically included

**Example**:
```python
from pyrig.dev.artifacts.resources.resource import get_resource_path
import your_project.dev.artifacts.resources as resources

config_path = get_resource_path("config.json", resources)
data = config_path.read_text()
```

#### `pkg/dev/configs/python/resources_init.py`

Manages the `resources/__init__.py` file to ensure proper package initialization.

#### `pkg/dev/configs/testing/fixtures/`

Configuration files that manage the fixture system structure (fixture.py, scopes/session.py, scopes/package.py, scopes/module.py, scopes/class_.py, scopes/function.py).

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

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                             │
│ --show-completion             Show completion for the current shell, to copy it or customize the    │
│                               installation.                                                         │
│ --help                        Show this message and exit.                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────╮
│ create-root    Creates the root of the project.                                                     │
│ create-tests   Create all test files for the project.                                               │
│ init           Set up the project.                                                                  │
│ build          Build all artifacts.                                                                 │
│ protect-repo   Protect the repository.                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────╯
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

**Built-in Fixtures**:
- `config_file_factory` - Factory for creating test config file classes
- `builder_factory` - Factory for creating test builder classes

**Creating Custom Fixtures**:

Add a `pkg/dev/tests/fixtures/` directory:

```
your_project/dev/tests/fixtures/
├── __init__.py
├── fixture.py          # Custom fixtures
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

Verifies and fixes all configuration files managed by the ConfigFile Machinery. If any config file is missing or incorrect, it automatically creates or corrects it. When running in GitHub Actions, it also ensures `experiment.py` exists.

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

Create custom builders by subclassing `Builder` in `pkg/dev/artifacts/builder/builder.py`:

```python
from pathlib import Path
from pyrig.dev.artifacts.builder.base.base import Builder

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
4. **Subclass PyInstallerBuilder** in `your_project/dev/artifacts/builder/builder.py`:
   ```python
   from types import ModuleType
   from pyrig.dev.artifacts.builder.base.base import PyInstallerBuilder

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
from pyrig.dev.artifacts.resources.resource import get_resource_path
import your_project.dev.artifacts.resources as resources

config_path = get_resource_path("config.json", resources)
data = json.loads(config_path.read_text())
```

### Multi-Package Architecture

pyrig supports multi-package architecture where multiple packages can depend on pyrig and automatically share configurations, builders, fixtures, and resources.

**Automatic Discovery**:

When you run pyrig commands or tests, it discovers components from all packages depending on pyrig:

1. **ConfigFile Machinery**: All `ConfigFile` subclasses from all `dev/configs/` directories
2. **Builders**: All `Builder` subclasses from all `dev/artifacts/builder/` directories
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

### Example 1: Complete Project Structure

After running `pyrig init`:

```
your-project/
├── .env, .gitignore, .pre-commit-config.yaml, .python-version
├── experiment.py, LICENSE, uv.lock, pyproject.toml, README.md
├── .github/workflows/
│   ├── health_check.yaml, publish.yaml, release.yaml
├── your_project/
│   ├── __init__.py, main.py, py.typed
│   ├── src/
│   └── dev/
│       ├── artifacts/builder/, artifacts/resources/
│       ├── cli/subcommands.py
│       ├── configs/configs.py
│       └── tests/fixtures/
└── tests/
    ├── conftest.py, test_zero.py
    └── test_your_project/
```

### Example 2: Adding a Custom Config File

```python
from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile

class MyConfigFile(YamlConfigFile):
    @classmethod
    def get_filename(cls) -> str:
        return "myconfig"

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {"setting1": "value1", "setting2": "value2"}
```

### Example 3: Custom CLI Command

```python
def deploy(environment: str = "staging") -> None:
    """Deploy the application."""
    print(f"Deploying to {environment}...")

# Run with: uv run your-project deploy --environment production
```

---

## Troubleshooting

### Common Issues

#### `uv run pyrig` command not found
```bash
uv sync
```

#### Pre-commit hooks failing
```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

#### Tests not being generated automatically
```bash
uv run pyrig create-tests
```

#### GitHub Actions permission errors
Ensure `REPO_TOKEN` secret has: `contents:read and write`, `administration:read and write`

#### MyPy errors
Add type hints:
```python
def add(a: int, b: int) -> int:
    return a + b
```

#### Dependency conflicts
```bash
uv lock --upgrade && uv sync
```

#### PyInstaller build fails
1. Ensure `main.py` exists and has `main()` function implemented
2. Ensure `icon.png` exists at `your_project/dev/artifacts/resources/icon.png`

#### Resources not found in built executable
Use `get_resource_path()`:
```python
from pyrig.dev.artifacts.resources.resource import get_resource_path
import your_project.dev.artifacts.resources as resources
path = get_resource_path("config.json", resources)
```

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
