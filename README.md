# pyrig

**pyrig** is a Python development toolkit that helps you **rig up** your Python projects by standardizing project configurations and automating testing workflows. It eliminates boilerplate setup work by providing opinionated, best-practice configurations for linting, type checking, testing, and CI/CD—allowing you to focus on writing code instead of configuring tools.

Built for Python 3.12+ projects using Poetry and GitHub, pyrig automatically generates project structure, creates test skeletons that mirror your source code, and maintains configuration files for tools like ruff, mypy, pytest, and pre-commit hooks.

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
- **Automatic Test Generation**: Creates test skeletons that mirror your source code structure
- **Strict Type Checking**: Enforces mypy strict mode with comprehensive type coverage
- **Code Quality Tools**: Pre-configured ruff (linting + formatting), mypy, bandit (security)
- **CI/CD Workflows**: GitHub Actions workflows for health checks, releases, and publishing
- **Repository Protection**: Automated GitHub branch protection and security settings
- **Dependency Management**: Automatic dependency updates with Poetry
- **Pre-commit Hooks**: Automated code quality checks before every commit
- **Artifact Building**: Extensible build system with PyInstaller support
- **Custom CLI**: Automatically generates CLI commands from your functions
- **Cross-Platform Testing**: Matrix testing across multiple OS and Python versions

---

## Requirements

- **Python**: 3.12 or higher
- **Poetry**: Package and dependency manager
- **Git**: Version control
- **GitHub**: For full CI/CD and repository protection features (optional but recommended)

---

## Installation

### From PyPI

```bash
pip install pyrig
# or
poetry add pyrig
```

**Note**: pyrig should be added as a regular dependency, not a dev dependency. 
Some might argue it should be a dev dependency. I hav ethought about it, but
decided against it for several reasons. 
The CLI functionality requires pyrig availability at runtime. Also pyrig has a small but often useful utility functionality that is available at runtime if you should need it. Also in the future functionality of pyrig might be extended around other things every project needs and these could include things that require runtime availability. 
Also pyrig decides itself what should be a dev dependency and what not. 
You will see in the generated pyproject.toml file that pyrig adds many dev dependencies. 
These are things that are only needed for development and testing and are not needed at runtime. 
pyrig does not add itself to the dev dependencies because it is needed at runtime for some of the functionality. 
You can add it as a dev dependency if you want, but all the functionality that requires pyrig at runtime will not be working then outside of the dev environment.

### From Source

```bash
git clone https://github.com/winipedia/pyrig.git
cd pyrig
poetry install
```

---

## Quick Start

```bash
# Create a new GitHub repository
# Clone it locally
git clone https://github.com/your-username/your-project.git
cd your-project

# Initialize Poetry project
poetry init

# Add pyrig
poetry add pyrig

# Initialize pyrig (creates all config files, tests, and runs setup)
poetry run pyrig init

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

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Initialize Poetry project**
   ```bash
   poetry init  # or poetry new
   ```

4. **Add pyrig as a dependency**
   ```bash
   poetry add pyrig
   ```

5. **Run pyrig initialization**
   ```bash
   poetry run pyrig init
   ```

   This command performs the following steps:
   - Creates the project root structure (source and test packages)
   - Initializes all configuration files
   - Generates test skeletons for all source code
   - Updates all dependencies to latest versions
   - Runs all pre-commit hooks
   - Executes the test suite

6. **Commit and push changes**
   ```bash
   git add .
   git commit -m "chore: init project with pyrig"
   git push
   ```

---

## Configuration Files

All configuration files are subclasses of `pyrig.dev.configs.base.base.ConfigFile` and are automatically created and managed by pyrig. You can add custom configs by subclassing `ConfigFile` and adding it to `pkg/dev/configs/**`. All subclasses in this folder are automatically discovered and initialized (created if not exists, updated if not correct).

**Note**: If you do not wish to have a specific config file managed by pyrig, you can make the file empty and pyrig will not overwrite it, however the file must exist.

### Managed Configuration Files

#### `pyproject.toml`

Stores project metadata and dependencies. pyrig automatically adds essential dev dependencies (ruff, mypy, pytest, pre-commit) and configures them with the strictest possible settings to enforce best practices.

- **Dependency Management**: All dependencies use `*` as the version to stay up-to-date
- **Version Constraints**: Use dictionary syntax for specific constraints: `{"version": "*", "python": "<3.15"}`
- **Dependency Locations**:
  - Dependencies: `tool.poetry.dependencies`
  - Dev dependencies: `tool.poetry.group.dev.dependencies`
- **Naming Convention**: Enforces that GitHub repo name and cwd name are equal; hyphens in repo names are converted to underscores in package names

#### `pkg/py.typed`

Automatically created to indicate that the package supports type checking, as pyrig uses mypy and enforces typing.

#### `README.md`

Automatically created with the requirement that it starts with `# <project_name>`. The rest of the content is up to you. Future versions may include skeleton functionality based on project structure.

#### `LICENCE`

Automatically created as an empty file for you to add your own license (e.g., MIT).

#### `experiment.py`

Automatically created as an empty file for experimentation. It is ignored by git and intended for trying out new things, not for production code.

#### `.python-version`

Automatically created and set to the lowest supported Python version. Used by pyenv to set the Python version for the project.

#### `.pre-commit-config.yaml`

Automatically created and configured with the following pre-commit hooks:

- `update-package-manager`: poetry self update
- `check-package-manager-config`: poetry check --strict
- `install-dependencies`: poetry install --with dev (keeps dependencies up-to-date automatically)
- `create-root`: pyrig create-root
- `lint-code`: ruff check --fix
- `format-code`: ruff format
- `check-static-types`: mypy --exclude-gitignore
- `check-security`: bandit -c pyproject.toml -r .

The `install-dependencies` hook ensures that your local environment stays synchronized with the latest dependencies defined in `pyproject.toml` before each commit.

#### `.gitignore`

Automatically created by pulling the latest version of [github/python.gitignore](https://github.com/github/gitignore/blob/main/Python.gitignore) and adding project-specific ignores (e.g., experiment.py).

#### `.env`

Automatically created as an empty file for environment variables. It is ignored by git and used by python-dotenv to load environment variables.

#### `.github/workflows/health_check.yaml`

Automatically created to run the health check workflow via GitHub Actions.

- **Triggers**: workflow_dispatch, pull_request, schedule (daily)
- **Purpose**: Runs a matrix of tests on different operating systems and supported Python versions to ensure cross-platform compatibility

#### `.github/workflows/release.yaml`

Automatically created to run the release workflow via GitHub Actions.

- **Triggers**: workflow_dispatch, commit to main, schedule (weekly)
- **Process**:
  1. Runs the health check workflow
  2. Creates a tag for the release and builds a changelog
  3. Creates a release on GitHub
  4. Builds artifacts (if a builder class is implemented) and uploads them to the release
  5. Commits the tag and possible dependency updates to `pyproject.toml` and `poetry.lock`
- **Synchronization**: Keeps tags, poetry version, and PyPI (if PYPI_TOKEN is configured) in sync

#### `.github/workflows/publish.yaml`

Automatically created to run the publish workflow via GitHub Actions.

- **Trigger**: Successful completion of the release workflow
- **Purpose**: Publishes the package to PyPI with poetry
- **Note**: If you do not want to publish to PyPI, empty the file and pyrig will not overwrite it, but will add a simple workflow that does nothing

#### `pkg/main.py`

Automatically created as the main entry point for your application. This file is used by PyInstaller to build standalone executables and can also be run directly.

- **Purpose**: Provides a clear entry point for your application
- **Usage**: Implement your application logic in the `main()` function
- **CLI Integration**: Can be called with `poetry run your-pkg-name main` or `python -m your-pkg-name`
- **PyInstaller**: Automatically used as the entry point for building executables

**Example**:
```python
# In pkg/main.py
def main() -> None:
    """Main entrypoint for the project."""
    print("Hello from your application!")
    # Add your application logic here

if __name__ == "__main__":
    main()
```

#### `pkg/src/`

Automatically created as a subfolder within your package to organize your source code. This separates your application code from development infrastructure (`dev/`) and configuration files.

- **Purpose**: Clear separation between source code and development tooling
- **Structure**: Place your modules, classes, and functions here
- **Organization**: Helps maintain a clean project structure

**Example Structure**:
```
your_project/
├── main.py              # Entry point
├── src/                 # Your source code goes here
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── utils.py
└── dev/                 # Development infrastructure
    ├── cli/
    ├── configs/
    └── artifacts/
```

#### `pkg/dev/subcommands.py`

Automatically created for defining custom CLI subcommands. Any function in this file is automatically added as a subcommand to your project's CLI.

- **Example**: A function named `run` can be executed with `poetry run your-pkg-name run`
- **Implementation**: pyrig automatically detects your package name, imports your subcommands.py file, and adds all functions as subcommands using typer
- **Entry Point**: Configured in `tool.poetry.scripts` in pyproject.toml

**Try it**: Add a print statement to a function in subcommands.py and run it with `poetry run your-pkg-name <func_name>`.

**Example Usage**:
```python
# In pkg/dev/subcommands.py
def hello(name: str = "World") -> None:
    """Say hello to someone."""
    print(f"Hello, {name}!")

# Run with:
# poetry run your-pkg-name hello --name Alice
```

#### `pkg/dev/configs/configs.py`

Define custom configuration files here. Any subclass of `pyrig.dev.configs.base.base.ConfigFile` is automatically discovered and initialized (created if not exists, updated if not correct). Configs can be defined in any file in the `pkg/dev/configs` folder.

**Note**: The configs.py file must exist. Deleting config files is pointless as they will be recreated by the create-root hook or by pytest session fixture.

#### `pkg/dev/artifacts/builder/builder.py`

Automatically created for defining build scripts. Any subclass of `pyrig.dev.artifacts.builder.base.base.Builder` is automatically discovered and executed. Builders can be defined in any file in the `pkg/dev/artifacts/builder` folder.

**Note**: The builder.py file must exist. Deleting builder classes is pointless as they will be recreated by the create-root hook or by pytest session fixture.

#### `tests/conftest.py`

Automatically created and configured to run pytest plugins. It automatically discovers and loads:
- All fixtures from `tests/base/fixtures/` in your project
- All fixtures from pyrig's testing module
- Makes all fixtures available to all tests in the project

This allows you to define reusable fixtures in `tests/base/fixtures/fixture.py` that are automatically available across all your tests.

#### `tests/base/`

Automatically created base test structure containing:
- **`tests/base/fixtures/`** - Directory for reusable pytest fixtures
  - `fixture.py` - Define custom fixtures here (e.g., `builder_factory`, `config_file_factory`)
  - `scopes/` - Fixture scope configurations
- **`tests/base/utils/`** - Directory for test utility functions
  - `utils.py` - Helper functions for tests

This base structure is copied from pyrig's internal testing framework and provides a foundation for organizing shared test utilities and fixtures.

#### `tests/test_zero.py`

An empty test file to ensure pytest does not complain about missing tests during initial setup.

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
poetry run pyrig protect-repo
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

pyrig enforces comprehensive testing by generating test skeletons for all functions and classes in the source code. It follows a mirror structure of the source package in the tests package:

- **Module Level**: For every module in your package, there is a corresponding module in `tests`
- **Class Level**: For every class in a module, there is a corresponding class in the test module
- **Function Level**: For every function in a class, there is a corresponding test function in the test class

**Example Structure**:
```
your_project/
├── your_project/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   └── src/
│       ├── __init__.py
│       ├── calculator.py    # Source module
│       └── utils.py         # Source module
└── tests/
    ├── __init__.py
    ├── test_your_project/
    │   ├── test_main.py         # Test for main.py
    │   └── test_src/
    │       ├── test_calculator.py   # Mirror test module
    │       └── test_utils.py        # Mirror test module
    └── conftest.py
```

### Automatic Test Generation

pyrig automatically generates test skeletons in two ways:

1. **Manual Generation**: Run `poetry run pyrig create-tests` to generate all missing tests
2. **Automatic Generation**: When you run `pytest`, an autouse session fixture automatically creates missing test modules, classes, and functions

#### Test Base Structure Creation

When you run `pyrig create-tests` (or `pyrig init`), pyrig first creates a **base test structure** by copying a template from pyrig's internal testing framework. This creates:

- **`tests/base/fixtures/`** - Reusable pytest fixtures that are automatically available to all tests
  - `fixture.py` - Define custom fixtures here (automatically loaded by conftest.py)
  - `scopes/` - Fixture scope configurations
- **`tests/base/utils/`** - Test utility functions
  - `utils.py` - Helper functions for your tests
- **`tests/conftest.py`** - Pytest configuration that auto-discovers and loads all fixtures

This base structure provides a foundation for organizing shared test utilities and fixtures across your entire test suite. Any fixtures defined in `tests/base/fixtures/fixture.py` are automatically available to all your tests without needing to import them.

**Generated Test Example**:
```python
# If you have this in your_project/src/calculator.py:
class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

# pyrig generates this in tests/test_your_project/test_src/test_calculator.py:
class TestCalculator:
    def test_add(self) -> None:
        """Test func for add."""
        raise NotImplementedError
```

### Automatic Test Enforcement with Autouse Session Fixtures

pyrig automatically enforces code quality and project conventions through a suite of autouse session fixtures that run once per test session. These fixtures are automatically plugged in via `tests/conftest.py` and ensure your project maintains best practices.

#### Session-Level Fixtures

The following autouse session fixtures are automatically applied to every test run:

**Project Structure Enforcement**:
- `assert_no_namespace_packages`: Ensures all packages have `__init__.py` files (no namespace packages)
- `assert_all_src_code_in_one_package`: Verifies that all source code is in a single package (besides the tests package)
- `assert_src_package_correctly_named`: Checks that the source package name matches the project name in `pyproject.toml`

**Test Coverage Enforcement**:
- `assert_all_modules_tested`: Automatically creates missing test modules, classes, and functions for any untested code. If tests are missing, they are generated and the fixture fails to alert you.

**Code Quality Enforcement**:
- `assert_no_unit_test_package_usage`: Prevents usage of the `unittest` package (enforces pytest)
- `assert_no_dev_usage_in_non_dev_files`: Ensures development utilities from the `dev/` folder are not imported in production code

**Configuration Enforcement**:
- `assert_config_files_are_correct`: Verifies all configuration files are correct and automatically fixes them if needed
- `assert_dev_dependencies_config_is_correct`: Validates dev dependencies configuration (pyrig internal)

**Dependency Management**:
- `assert_dependencies_are_up_to_date`: Runs `poetry update --with dev` to ensure dependencies are current

These fixtures run automatically before your tests execute, ensuring that:
1. Your project structure follows best practices
2. All code has corresponding test skeletons
3. Configuration files are up-to-date
4. Dependencies are synchronized
5. Code quality standards are maintained

**Note**: These fixtures are designed to fail fast and provide clear error messages when conventions are violated, helping you maintain a clean and well-structured codebase.

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_your_project/test_calculator.py

# Run with coverage
poetry run pytest --cov=your_project
```

### Disabling Tests

If you do not want tests for a specific module, you must manually empty the test file. This way pytest never loads it and the autouse module fixture does not trigger. This is purposely made difficult to enforce best practices and comprehensive test coverage.

**To disable tests for a module**:
```bash
# Empty the test file (but keep the file)
echo "" > tests/test_your_project/test_src/test_calculator.py
```

---

## Building Artifacts

pyrig provides an extensible build system for creating distributable artifacts. All builders are subclasses of `pyrig.dev.artifacts.builder.base.base.Builder`.

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
poetry run pyrig build
```

Artifacts are placed in the `artifacts/` directory with platform-specific naming (e.g., `my_artifact-Linux.txt`, `my_artifact-Windows.txt`).

### PyInstaller Builder

pyrig includes a `PyInstallerBuilder` class for creating standalone executables. The `main.py` file is automatically created in your source package during initialization.

1. **Implement your main function** in `your_project/main.py` (automatically created):
   ```python
   # your_project/main.py
   def main() -> None:
       print("Hello from your app!")
       # Add your application logic here

   if __name__ == "__main__":
       main()
   ```

2. **Create an icon.png file** at `your_project/dev/artifacts/icon.png` (256x256 recommended)

3. **Subclass PyInstallerBuilder** in `your_project/dev/artifacts/builder/builder.py`:
   ```python
   from pathlib import Path
   from pyrig.dev.artifacts.builder.base.base import PyInstallerBuilder

   class MyAppBuilder(PyInstallerBuilder):
       """Build standalone executable with PyInstaller."""

       @classmethod
       def get_add_datas(cls) -> list[tuple[Path, Path]]:
           """Specify additional data files to include."""
           return [
               (Path("your_project/data"), Path("data")),
               # Add more data files as needed
           ]
   ```

4. **Build the executable**:
   ```bash
   poetry run pyrig build
   ```

The builder automatically:
- Creates a single executable file
- Converts icon.png to platform-specific format (ico for Windows, icns for macOS)
- Includes specified data files
- Names the output with platform suffix (e.g., `your-project-Windows.exe`, `your-project-Linux`)

**PyInstaller Options**:
- `--onefile`: Single executable (default)
- `--noconsole`: No console window (default)
- Platform-specific icons handled automatically

---

## Examples

### Example 1: Complete Project Structure

After running `pyrig init`, your project will look like this:

```
your-project/
├── .env                          # Environment variables (git-ignored)
├── .gitignore                    # Git ignore rules
├── .pre-commit-config.yaml       # Pre-commit hooks configuration
├── .python-version               # Python version for pyenv
├── experiment.py                 # Experimentation file (git-ignored)
├── LICENSE                       # License file
├── poetry.lock                   # Poetry lock file
├── pyproject.toml                # Project configuration
├── README.md                     # Project documentation
├── .github/
│   └── workflows/
│       ├── health_check.yaml     # CI testing workflow
│       ├── publish.yaml          # PyPI publishing workflow
│       └── release.yaml          # Release workflow
├── your_project/                 # Source package
│   ├── __init__.py
│   ├── main.py                   # Main entry point (auto-created)
│   ├── py.typed                  # Type checking marker
│   ├── src/                      # Source code folder
│   │   └── __init__.py
│   └── dev/                      # Development infrastructure
│       ├── __init__.py
│       ├── artifacts/
│       │   └── builder/
│       │       └── builder.py    # Build scripts
│       ├── cli/
│       │   └── subcommands.py    # CLI commands
│       └── configs/
│           └── configs.py        # Custom config files
└── tests/                        # Test package
    ├── __init__.py
    ├── conftest.py               # Pytest configuration
    ├── test_zero.py              # Empty test placeholder
    ├── base/                     # Base test structure
    │   ├── __init__.py
    │   ├── fixtures/             # Reusable pytest fixtures
    │   │   ├── __init__.py
    │   │   ├── fixture.py        # Custom fixtures
    │   │   └── scopes/           # Fixture scopes
    │   └── utils/                # Test utilities
    │       ├── __init__.py
    │       └── utils.py          # Helper functions
    └── test_your_project/        # Mirror of source structure
        ├── __init__.py
        └── test_dev
            ├── ...               # will have the tests for the dev package
                
        
```

### Example 2: Adding a Custom Config File

```python
# In your_project/dev/configs/configs.py
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.base import YamlConfigFile

class MyConfigFile(YamlConfigFile):
    """Custom YAML configuration file."""

    @classmethod
    def get_filename(cls) -> str:
        return "myconfig"

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")  # Creates config/myconfig.yaml

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {
            "setting1": "value1",
            "setting2": "value2",
        }
```

### Example 3: Custom CLI Command

```python
# In your_project/dev/cli/subcommands.py
import typer

def deploy(environment: str = typer.Option("staging", help="Deployment environment")) -> None:
    """Deploy the application to specified environment."""
    print(f"Deploying to {environment}...")
    # Your deployment logic here

# Run with:
# poetry run your-project deploy --environment production
```

---

## Troubleshooting

### Common Issues

#### Issue: `poetry run pyrig` command not found

**Solution**: Make sure you've installed dependencies:
```bash
poetry install
```

#### Issue: Pre-commit hooks failing

**Solution**: Install pre-commit hooks:
```bash
poetry run pre-commit install
# Or run hooks manually
poetry run pre-commit run --all-files
```

#### Issue: Tests not being generated automatically

**Solution**: Make sure your test files are not empty. If a test file is empty, pytest won't load it and the autouse fixture won't trigger. Run:
```bash
poetry run pyrig create-tests
```

#### Issue: GitHub Actions failing with permission errors

**Solution**: Ensure your `REPO_TOKEN` secret has the correct permissions:
- `contents:read and write`
- `administration:read and write`

#### Issue: MyPy errors after initialization

**Solution**: pyrig enforces strict type checking. Add type hints to your code:
```python
# Before
def add(a, b):
    return a + b

# After
def add(a: int, b: int) -> int:
    return a + b
```

#### Issue: Dependency conflicts

**Solution**: Update dependencies:
```bash
poetry update --with dev
```

#### Issue: PyInstaller build fails

**Solution**:
1. Ensure `main.py` exists in your source package (automatically created by `pyrig init`)
2. Ensure you've implemented the `main()` function in `main.py`
3. Ensure `icon.png` exists at `your_project/dev/artifacts/icon.png`
4. Check that all data files in `get_add_datas()` exist

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues**: Found a bug? [Open an issue](https://github.com/winipedia/pyrig/issues)
2. **Suggest Features**: Have an idea? [Start a discussion](https://github.com/winipedia/pyrig/discussions)
3. **Submit Pull Requests**:
   - Fork the repository
   - Create a feature branch (`git checkout -b feature/amazing-feature`)
   - Make your changes
   - Run tests (`poetry run pytest`)
   - Run pre-commit hooks (`poetry run pre-commit run --all-files`)
   - Commit your changes (`git commit -m 'feat: add amazing feature'`)
   - Push to the branch (`git push origin feature/amazing-feature`)
   - Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/winipedia/pyrig.git
cd pyrig

# Install dependencies
poetry install --with dev

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest

# Run type checking
poetry run mypy .

# Run linting
poetry run ruff check .
```

---

## License

pyrig is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

Copyright (c) 2025 Winipedia

---

## Links and Resources

- **Repository**: [https://github.com/winipedia/pyrig](https://github.com/winipedia/pyrig)
- **Issues**: [https://github.com/winipedia/pyrig/issues](https://github.com/winipedia/pyrig/issues)
- **Discussions**: [https://github.com/winipedia/pyrig/discussions](https://github.com/winipedia/pyrig/discussions)
- **PyPI**: [https://pypi.org/project/pyrig/](https://pypi.org/project/pyrig/)

### Built With

- [Poetry](https://python-poetry.org/) - Dependency management
- [Ruff](https://github.com/astral-sh/ruff) - Linting and formatting
- [mypy](https://mypy-lang.org/) - Static type checking
- [pytest](https://pytest.org/) - Testing framework
- [pre-commit](https://pre-commit.com/) - Git hook management
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [PyInstaller](https://pyinstaller.org/) - Executable builder
- [Bandit](https://bandit.readthedocs.io/) - Security linting

---
