# Getting Started with pyrig

This guide will walk you through creating your first pyrig project from scratch. By the end, you'll have a fully configured Python project with automated testing, linting, type checking, and CI/CD.

## Prerequisites

Before you begin, ensure you have the following installed and configured:

### Required Tools

- **Git** (any recent version)
  ```bash
  git --version  # Verify installation
  ```

- **uv** (Python package manager by Astral)
  ```bash
  # Install uv if you don't have it
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Verify installation
  uv --version
  ```

- **Podman** (for containerization)
  ```bash
  podman --version  # Verify installation
  ```
  Note: pyrig prefers Podman over Docker for its daemonless architecture and rootless design.

### GitHub Setup

pyrig is designed to work with GitHub. You'll need:

1. **A GitHub account** - [Sign up here](https://github.com/join) if you don't have one

2. **Git configured with your GitHub username**
   ```bash
   # Check your git username
   git config --get user.name
   
   # If it doesn't match your GitHub username, set it:
   git config --global user.name "YourGitHubUsername"
   git config --global user.email "your.email@example.com"
   ```
   
   **Important:** Your git username should match your GitHub username for pyrig to work garanteed correctly.

3. **A GitHub Personal Access Token (PAT)** with the following permissions:
   - `administration:read` and `administration:write` (for repository protection)
   - `contents:read` and `contents:write` (for pushing code in CI)
   
   [Create a PAT here](https://github.com/settings/tokens/new)

## Quick Start: Your First pyrig Project

### Step 1: Create a GitHub Repository

1. Go to [GitHub](https://github.com/new) and create a new repository
2. Choose a name for your project (e.g., `my-awesome-project`)
3. Make it public or private (your choice)
4. **Do not** initialize with README, .gitignore (pyrig will create these). LICENCE is fine if you do not want to use the MIT license, which pyrig uses by default.
5. Click "Create repository"

### Step 2: Configure GitHub Secrets

Your repository needs secrets for automation to work:

1. Go to your repository's **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add:

   - **`REPO_TOKEN`** (Required)
     - Value: Your Personal Access Token from prerequisites
     - Used for: Branch protection and repository management

   - **`PYPI_TOKEN`** (Optional, only if you want to publish to PyPI)
     - Value: Your PyPI API token
     - Used for: Automated package publishing
     - [Get a PyPI token here](https://pypi.org/manage/account/token/)
     - I recommend after the first publish to revoke the original token and make a scoped one for that package only.

   - **`CODECOV_TOKEN`** (public repos just need to connect Codecov account to the repository)
     - Value: Your Codecov token
     - Used for: Code coverage reporting
     - Public repos don't need this if you connect your Codecov account
     - [Get a Codecov token here](https://codecov.io/)

### Step 3: Clone and Initialize Locally

```bash
# Clone your empty repository
git clone https://github.com/YourUsername/my-awesome-project.git
cd my-awesome-project

# Initialize with uv
uv init

# Add pyrig as a dependency
uv add pyrig

# Run pyrig initialization (this is where the magic happens!)
uv run pyrig init
```

### Step 4: Understanding What Just Happened

The `pyrig init` command runs a few sequential steps:

1. **Adding dev dependencies** - Installs `pyrig-dev` package (includes things like: ruff, mypy, pytest, bandit, pre-commit, etc.)
2. **Syncing venv** - Installs all dependencies
3. **Creating priority config files** - Creates `pyproject.toml`, `.gitignore`, `LICENSE`, and other critical files
4. **Syncing venv** (again) - Ensures new configs are applied
5. **Creating project root** - Generates all config files and directory structure
6. **Creating test files** - Generates test skeletons for all code
7. **Running pre-commit hooks** - Formats and lints all code
8. **Running tests** - Validates everything works
9. **Committing initial changes** - Creates initial git commit

### Step 5: Push to GitHub

```bash
# Push your initialized project
git push -u origin main
```

The GitHub Actions workflows will automatically run, validate your code, and set up CI/CD for your project.
This will also setup main branch protection and other security settings for your repository.

## Understanding Your Project Structure

After initialization, your project will have this structure:

```
my-awesome-project/
├── .github/                     # GitHub Actions workflows
│   └── workflows/
│       ├── build.yaml           # Builds artifacts and container image
│       ├── health_check.yaml    # CI pipeline, runs tests etc
│       ├── publish.yaml         # Package publishing workflow (can be opted out of)
│       └── release.yaml         # Automated releases workflow, adds build files to release
├── docs/                        # Documentation
│   └── index.md                 # Documentation index
├── my_awesome_project/          # Main package (project name with underscores, not hyphens)
│   ├── dev/                     # Development tools (interaction with pyrig, not to be used in src code)
│   │   ├── builders/            # define subclasses of Builder to create artifacts, which can be invoked by `pyrig build` and are added to the release
│   │   │   └── __init__.py
│   │   ├── cli/                 # CLI commands
│   │   │   ├── __init__.py
│   │   │   ├── subcommands.py   # Project-specific CLI commands (only available in this project)
│   │   │   └── shared_subcommands.py  # Cross-package CLI commands (available in all dependent packages)
│   │   ├── configs/             # Configuration file managers, subclasses of ConfigFile to adjust behavior and settings of ConfigFiles
│   │   │   └── __init__.py
│   │   ├── tests/               # Test infrastructure
│   │   │   ├── fixtures/        # Pytest fixtures, all pytest.fixture functions in any file under fixtures/ are automatically registered as pytest fixtures
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── resources/               # define resources for your project, which can be accessed at runtime via get_resource_path
│   │   └── __init__.py
│   ├── src/                     # your project code
│   │   ├── __init__.py
│   │   └── ...                  # Your application code goes here
│   ├── __init__.py
│   ├── main.py                  # project entrypoint, the func main is also added as a CLI command, so you can run it via `uv run my_awesome_project main`
│   └── py.typed                 # PEP 561 marker for type checking
├── tests/                       # Test suite
│   ├── test_my_awesome_project/ # Tests mirror source structure
│   │   ├── test_dev/            # Tests for dev/ directory
│   │   │   ├── test_builders/
│   │   │   │   └── __init__.py
│   │   │   ├── test_cli/
│   │   │   │   ├── __init__.py
│   │   │   │   └── test_subcommands.py
│   │   │   ├── test_configs/
│   │   │   │   └── __init__.py
│   │   │   ├── test_tests/
│   │   │   │   ├── test_fixtures/
│   │   │   │   │   └── __init__.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── test_resources/      # Tests for resources/
│   │   │   └── __init__.py
│   │   ├── test_src/            # Tests for src/ (your code tests go here)
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── test_main.py         # Tests for main.py
│   ├── __init__.py
│   ├── conftest.py              # Pytest , adds pyrig.dev.tests.conftest as a pytest plugin
│   └── test_zero.py             # empty test to have tests run even when no tests are written, makes sure autouse fixtures are executed on initialization
├── .coverage                    # Coverage data file, produced by pytest-cov (git-ignored)
├── .env                         # Environment variables (git-ignored)
├── .gitignore                   # Git ignore patterns
├── .pre-commit-config.yaml      # Pre-commit hooks configuration (e.g. linting, formatting, type checking, security scanning)
├── .python-version              # Python version for the project
├── Containerfile                # Container definition (Podman)
├── LICENSE                      # MIT license or other license text that you put in there
├── pyproject.toml               # Project configuration
├── README.md                    # Project documentation, badges are automatically added by pyrig (matching git and github username required if remote is not set)
└── uv.lock                      # Dependency lock file
```

## Your First Code

Let's add some actual functionality to your project!

### Adding a Function

1. **Create a new module** in `<package>/src/`:

   ```bash
   # Create a new Python file
   touch my_awesome_project/src/calculator.py
   ```

2. **Write a simple function**:

   ```python
   # my_awesome_project/src/calculator.py
   """Simple calculator functions."""

   def add(a: int, b: int) -> int:
       """Add two numbers together.

       Args:
           a: First number
           b: Second number

       Returns:
           Sum of a and b
       """
       return a + b
   ```

3. **Generate test skeletons**:

   ```bash
   uv run pyrig mktests
   ```

   This creates `tests/test_my_awesome_project/test_src/test_calculator.py` with:

   ```python
   """Tests for my_awesome_project.src.calculator."""

   from my_awesome_project.src.calculator import add

   def test_add() -> None:
       """Test func."""
       raise NotImplementedError
   ```

4. **Implement the test**:

   ```python
   """Tests for my_awesome_project.src.calculator."""

   from my_awesome_project.src.calculator import add

   def test_add() -> None:
       """Test add."""
       assert add(2, 3) == 5
       assert add(-1, 1) == 0
       assert add(0, 0) == 0
   ```

5. **Run the tests**:

   ```bash
   uv run pytest
   ```

6. **Commit your changes**:

   ```bash
   git add .
   git commit -m "Add calculator module with tests"
   git push
   ```

   The pre-commit hooks will automatically:
   - Format your code with ruff
   - Check types with ty and mypy
   - Scan for security issues with bandit
   - Run all tests

### Adding a Class

1. **Create a class** in `<package>/src/`:

   ```python
   # my_awesome_project/src/counter.py
   """A simple counter class."""

   class Counter:
       """A counter that can increment and decrement."""

       def __init__(self, initial: int = 0) -> None:
           """Initialize the counter.

           Args:
               initial: Starting value for the counter
           """
           self.value = initial

       def increment(self) -> None:
           """Increment the counter by 1."""
           self.value += 1

       def decrement(self) -> None:
           """Decrement the counter by 1."""
           self.value -= 1

       def reset(self) -> None:
           """Reset the counter to 0."""
           self.value = 0
   ```

2. **Generate tests**:

   ```bash
   uv run pyrig mktests
   ```

   This creates a test class `TestCounter` with test methods for each method.

3. **Implement the tests**:

   ```python
   """Tests for my_awesome_project.src.counter."""

   from my_awesome_project.src.counter import Counter

   class TestCounter:
       """Tests for Counter."""

       def test_init(self) -> None:
           """Test __init__."""
           counter = Counter()
           assert counter.value == 0

           counter = Counter(initial=10)
           assert counter.value == 10

       def test_increment(self) -> None:
           """Test increment."""
           counter = Counter()
           counter.increment()
           assert counter.value == 1
           counter.increment()
           assert counter.value == 2

       def test_decrement(self) -> None:
           """Test decrement."""
           counter = Counter(initial=5)
           counter.decrement()
           assert counter.value == 4

       def test_reset(self) -> None:
           """Test reset."""
           counter = Counter(initial=10)
           counter.reset()
           assert counter.value == 0
   ```

4. **Run tests and commit**:

   ```bash
   uv run pytest
   git add .
   git commit -m "Add Counter class with tests"
   git push
   ```

## Common Issues

### Issue: "Config file X is not correct"

**What it means:** pyrig detected that a configuration file doesn't match the expected structure.

**Why it happens:**
- You manually edited a config file in a way that conflicts with pyrig's expectations
- A dependency update changed the expected configuration (pyrig version update)

**How to fix:**
```bash
# Regenerate all config files
uv run pyrig mkroot

# Review the changes
git diff

# If they look good, commit them
git add .
git commit -m "Update config files"
```

**Note:** pyrig uses "subset validation" - you can add to configs, but you can't remove required values.

### Issue: "Found missing tests"

**What it means:** You added code but haven't created tests for it yet.

**Why it happens:** pyrig enforces that every function and class has a corresponding test.

**How to fix:**
```bash
# Generate test skeletons for all untested code
uv run pyrig mktests

# Implement the generated tests (they'll have raise NotImplementedError)
# Then run tests
uv run pytest
```

### Issue: Pre-commit Hook Failures

**What it means:** Your code doesn't meet quality standards (formatting, types, security).

**Common failures:**

1. **Formatting issues (ruff format)**
   ```bash
   # Auto-fix formatting
   uv run ruff format .
   ```

2. **Linting issues (ruff check)**
   ```bash
   # Auto-fix many linting issues
   uv run ruff check --fix .

   # For issues that can't be auto-fixed, read the error and fix manually
   ```

3. **Type errors (ty or mypy)**
   ```bash
   # Check types
   uv run ty check
   uv run mypy .

   # Fix by adding type annotations or fixing type mismatches
   ```

4. **Security issues (bandit)**
   ```bash
   # Check security
   uv run bandit -c pyproject.toml -r .

   # Fix by addressing the security concerns
   # Or suppress false positives with # nosec comments
   ```

### Issue: "Coverage too low"

**What it means:** Your tests don't cover 90% of your code.

**How to fix:**
1. Check the coverage report in the terminal output of `uv run pytest`  (pyproject.toml defines already --cov-fail-under=90 and --cov-report=term-missing)

2. Check the coverage report in the logs to see what's not covered

3. Add tests for the uncovered code

4. Run tests again until you hit 90%+

### Issue: "ModuleNotFoundError" when importing

**What it means:** Python can't find your module.

**Common causes:**
1. **Missing `__init__.py` files**
   ```bash
   # Create all missing __init__.py files
   uv run pyrig mkinits
   ```

2. **Wrong import path**
   ```python
   # Wrong
   from calculator import add

   # Correct
   from my_awesome_project.src.calculator import add
   ```

3. **Not in the virtual environment**
   ```bash
   # Always use uv run
   uv run python -c "import my_awesome_project"
   ```

### Issue: GitHub Actions failing

**What it means:** CI pipeline is failing on GitHub.

**Common causes:**

1. **Missing secrets** - Add `REPO_TOKEN` to repository secrets

2. **Tests passing locally but failing in CI**
   - Check Python version matrix (CI tests 3.12, 3.13, 3.14)
   - Check for platform-specific code (Windows paths are a common issue)

3. **Branch protection preventing merge**
   - This is intentional! Fix the failing checks
   - Don't bypass branch protection
   - Especially if you are in a team, do not bypass branch protection
   - only the repo owner can bypass branch protection

**How to debug:**
1. Click on the failing workflow in GitHub Actions
2. Read the error logs
3. Fix the issue locally
4. Push again

## Essential Commands Reference

Here are the commands you'll use most often:

### Project Initialization
```bash
uv run pyrig init          # Initialize a new pyrig project (one-time)
uv run pyrig mkroot        # Regenerate all config files
```

### Development Workflow
```bash
uv run pyrig mktests       # Generate test skeletons for new code
uv run pyrig mkinits       # Create missing __init__.py files
uv run pytest              # Run all tests
uv run pytest -v           # Run tests with verbose output
uv run pytest tests/test_my_module.py  # Run specific test file
```

### Code Quality
```bash
uv run pre-commit run --all-files  # Run all pre-commit hooks
uv run ruff check .                # Lint code
uv run ruff format .               # Format code
uv run ty check                    # Type check with ty
uv run mypy .                      # Type check with mypy
uv run bandit -c pyproject.toml -r .  # Security scan
```

### Dependency Management
```bash
uv add package-name        # Add a new dependency
uv add --group dev package # Add a dev dependency
uv remove package-name     # Remove a dependency
uv sync                    # Install all dependencies
uv lock --upgrade          # Update all dependencies
```

### Building and Publishing
```bash
uv run pyrig build         # Build all artifacts (executables, etc.)
uv run pyrig protect-repo  # Set up GitHub branch protection
```

### Getting Help
```bash
uv run pyrig --help        # Show all available commands
uv run pyrig <command> --help  # Show help for a specific command
```

## Creating Custom CLI Commands

Pyrig provides two ways to add custom CLI commands to your project:

### Project-Specific Commands

Add commands to `{package}/dev/cli/subcommands.py` for commands that are **only available in this project**:

```python
# my_awesome_project/dev/cli/subcommands.py
"""Subcommands for the CLI.

They will be automatically imported and added to the CLI
IMPORTANT: All funcs in this file will be added as subcommands.
So best to define the logic elsewhere and just call it here in a wrapper.
"""


def migrate() -> None:
    """Run database migrations."""
    print("Running migrations...")
    # Your migration logic here


def seed_db() -> None:
    """Seed the database with test data."""
    print("Seeding database...")
    # Your seeding logic here
```

Now these commands are available:
```bash
uv run my-awesome-project migrate
# Running migrations...

uv run my-awesome-project seed-db
# Seeding database...
```

### Shared Commands (Multi-Package)

Add commands to `{package}/dev/cli/shared_subcommands.py` for commands that should be **available in all packages that depend on yours**:

```python
# company_base/dev/cli/shared_subcommands.py
"""Shared commands for the CLI.

This module provides shared CLI commands that can be used by multiple
packages in a multi-package architecture. These commands are automatically
discovered and added to the CLI by pyrig.
"""

import typer


def deploy() -> None:
    """Deploy the application to production."""
    from pyrig.dev.utils.cli import get_project_name_from_argv
    project_name = get_project_name_from_argv()
    typer.echo(f"Deploying {project_name} to production...")
    # Your deployment logic here
```

Now **every package** that depends on `company-base` gets the `deploy` command:

```bash
# In service-a (depends on company-base)
uv run service-a deploy
# Deploying service-a to production...

# In service-b (also depends on company-base)
uv run service-b deploy
# Deploying service-b to production...
```

**Built-in Example:** The `version` command is a shared subcommand from pyrig:

```bash
uv run my-awesome-project version
# my-awesome-project version 1.0.0
```

See [Multi-Package Architecture](multi-package-architecture.md) and [shared_subcommands.py documentation](config-files/shared-subcommands.md) for more details.

---

If you run into issues:
1. **Check existing documentation** - Browse the [docs/](.) directory

2. **Open an issue** - [GitHub Issues](https://github.com/Winipedia/pyrig/issues)

3. **Read the source code** - pyrig's code is well-documented and readable

## Tips for Success

1. **Trust the automation** - Let pyrig manage configs, don't fight it

2. **Run tests frequently** - `uv run pytest` should be muscle memory

3. **Commit often** - Pre-commit hooks catch issues early

4. **Read error messages** - pyrig provides detailed, actionable error messages

5. **Keep dependencies updated** - pyrig's CI  and autouse fixtures automatically update them

6. **Use type hints** - They catch bugs and improve code quality

7. **Write tests first** - Or at least write them immediately after code

8. **Don't bypass quality checks** - They're there to help you

## What Makes pyrig Different?

Unlike other project templates (cookiecutter, copier), pyrig is:

- **Living** - Configs stay synchronized automatically
- **Opinionated** - Best practices enforced, not suggested
- **Extensible** - Plugin architecture for custom functionality
- **Current** - Automatically updates to latest tools and standards
- **Comprehensive** - Handles everything from init to deployment

pyrig is designed for **serious, long-term projects** where code quality and maintainability matter more than quick setup.

---

**Ready to build something amazing?** Start coding in `<package>/src/` and let pyrig handle the rest!


