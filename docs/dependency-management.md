# Dependency Management

pyrig uses [uv](https://github.com/astral-sh/uv) as its package management tool. This document covers how pyrig integrates with uv for dependency resolution, locking, version management, and CI/CD automation.

## Overview

pyrig's dependency management is built around:

- **uv** — Fast Python package manager for installing, syncing, and publishing
- **pyproject.toml** — Central configuration for project metadata and dependencies
- **uv.lock** — Lock file ensuring reproducible builds across environments
- **Automatic version bumping** — CI/CD patches versions on every successful build/release

Key characteristics:

- **Version-free dependencies** — pyrig strips version specifiers from dependencies in pyproject.toml
- **Lock file tracking** — Exact versions are tracked in uv.lock for reproducibility
- **Automated updates** — CI runs `uv lock --upgrade` to keep dependencies current
- **Separation of concerns** — Runtime vs. development dependencies are clearly separated

Stripping versions to have everything always up to date and autoupdated is very useful but also very controversial. You can disable this behavior by overriding `PyprojectConfigFile.should_remove_version_from_dep` in your `pyproject.py` config file and make it return `False`.

## uv Commands

pyrig uses these uv commands throughout its workflows:

| Command | Purpose | When Used |
|---------|---------|-----------|
| `uv init` | Initialize a new Python project | Initial project setup |
| `uv add <package>` | Add a dependency | Adding new packages |
| `uv sync` | Install dependencies from lock file | After cloning, after lock changes |
| `uv lock --upgrade` | Update all dependencies to latest | CI health check, dependency updates |
| `uv version --bump patch` | Increment patch version | CI release preparation |
| `uv build` | Build wheel and source distribution | Release workflow |
| `uv publish` | Publish to PyPI | Publish workflow |
| `uv run <command>` | Run command in project environment | All CLI commands |

## pyproject.toml Structure

pyrig generates and maintains a specific pyproject.toml structure:

```toml
[project]
name = "your-project"
version = "1.0.0"
description = "Your project description"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pyrig",
    "requests",
    # Note: No version specifiers
]

# pyrig's own runtime dependencies include:
# - dotenv: Environment variable management
# - packaging: Version parsing and comparison
# - pathspec: .gitignore pattern matching
# - pillow: Image processing for icons
# - pygithub: GitHub API integration
# - pyyaml: YAML file handling
# - setuptools: Package building utilities
# - tenacity: Retry and exponential backoff for network resilience
# - tomlkit: TOML file handling with formatting preservation
# - typer: CLI framework

[project.scripts]
your-project = "your_project.dev.cli.cli:main"

[dependency-groups]
dev = [
    "bandit",
    "mypy",
    "pre-commit",
    "pytest",
    "pytest-mock",
    "ruff",
    "ty",
    # Type stubs and other dev tools
]

[build-system]
requires = ["uv_build"]
build-backend = "uv_build"

[tool.uv.build-backend]
module-name = "your_project"
module-root = ""
```

### Key Sections

| Section | Purpose |
|---------|---------|
| `[project]` | Package metadata and runtime dependencies |
| `[project.scripts]` | CLI entry points |
| `[dependency-groups]` | Development-only dependencies |
| `[build-system]` | Build backend configuration (uv) |
| `[tool.uv.build-backend]` | Package module configuration |

## Version-Free Dependencies

pyrig deliberately strips version specifiers from dependencies:

```python
# In PyprojectConfigFile
@classmethod
def should_remove_version_from_dep(cls) -> bool:
    """Determine whether to strip version specifiers from dependencies."""
    return True

@classmethod
def remove_version_from_dep(cls, dep: str) -> str:
    """Strip version specifier from a dependency string."""
    return re.split(r"[^a-zA-Z0-9_.-]", dep)[0]
```

**Why?**

1. **Simplicity** — No version conflicts to manage manually
2. **Always current** — CI updates to latest compatible versions
3. **Lock file authority** — uv.lock contains exact versions for reproducibility

**Example transformation:**
```
# Input
requests>=2.28.0,<3.0.0

# Output in pyproject.toml
requests

# Exact version tracked in uv.lock
requests==2.31.0
```

## Lock File (uv.lock)

The `uv.lock` file contains:

- Exact versions of all dependencies (direct and transitive)
- Package hashes for integrity verification
- Platform-specific markers
- Source URLs

```yaml
# Example excerpt from uv.lock
[[package]]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
    { name = "certifi" },
    { name = "charset-normalizer" },
    { name = "idna" },
    { name = "urllib3" },
]

[package.metadata]
requires-dist = [
    { name = "certifi", specifier = ">=2017.4.17" },
    # ...
]
```

### Lock File Commands

```bash
# Install from lock file (fast, reproducible)
uv sync

# Update lock file to latest versions
uv lock --upgrade

# Update specific package
uv lock --upgrade-package requests
```

## Development Dependencies

pyrig automatically includes standard development dependencies:

```python
@classmethod
def get_standard_dev_dependencies(cls) -> list[str]:
    return sorted([
        "bandit",       # Security scanning
        "mypy",         # Type checking (strict mode)
        "pre-commit",   # Git hooks
        "pytest",       # Testing
        "pytest-cov",   # Test coverage
        "pytest-mock",  # Test mocking
        "ruff",         # Linting and formatting
        "ty",           # Type checking (modern, fast)
        "pyinstaller",  # Executable building
        # Type stubs
        "types-defusedxml",
        "types-pyinstaller",
        "types-pyyaml",
        "types-setuptools",
        "types-tqdm",
    ])
```

These are placed in `[dependency-groups].dev` and installed with `uv sync`.

### Type Checking Tools

pyrig includes two type checkers:

- **ty** — A modern, fast type checker that provides quick feedback during development
- **mypy** — The established standard for Python type checking, configured in strict mode

Both run as part of pre-commit hooks and CI. This dual approach ensures comprehensive type coverage while `ty` continues to mature.

> **Note:** In the future, pyrig plans to transition to using only `ty` once it reaches a more mature state. For now, both type checkers are maintained to provide maximum type safety.

## Version Bumping

pyrig automates version management in CI/CD:

### Automatic Patch Bumping

During the health check workflow, the version is bumped:

```yaml
- name: Patch Version
  run: uv version --bump patch && git add pyproject.toml
```

This command:
1. Increments the patch version (e.g., 1.0.0 → 1.0.1)
2. Stages the modified pyproject.toml

### Version Extraction

The release workflow extracts the version for tagging:

```yaml
- name: Extract Version
  run: echo "version=v$(uv version --short)" >> $GITHUB_OUTPUT

- name: Create And Push Tag
  run: git tag v$(uv version --short) && git push origin v$(uv version --short)
```

### Version Commands

```bash
# Show current version
uv version

# Show version number only
uv version --short

# Bump patch (1.0.0 → 1.0.1)
uv version --bump patch

# Bump minor (1.0.0 → 1.1.0)
uv version --bump minor

# Bump major (1.0.0 → 2.0.0)
uv version --bump major

# Set specific version
uv version 2.0.0
```

## Dependency Installation

### PyprojectConfigFile Methods

pyrig provides programmatic access to dependency management:

```python
from pyrig.dev.configs.pyproject import PyprojectConfigFile

# Install all dependencies (runtime + dev)
PyprojectConfigFile.install_dependencies()  # runs: uv sync

# Update to latest versions
PyprojectConfigFile.update_dependencies()   # runs: uv lock --upgrade
```

### PROJECT_MGT Constant

The project management tool is defined as a constant for consistency:

```python
from pyrig.src.project.mgt import PROJECT_MGT, PROJECT_MGT_RUN_ARGS

PROJECT_MGT = "uv"
PROJECT_MGT_RUN_ARGS = ["uv", "run"]
```

This allows pyrig to consistently build commands:

```python
# Run a CLI command
args = ["uv", "run", "pyrig", "build"]

# Run a Python module
args = ["uv", "run", "python", "-m", "your_module"]
```

## CI/CD Integration

### Health Check Workflow Steps

The health check workflow handles dependencies:

```yaml
steps:
  - name: Install Python Dependencies
    run: uv sync

  - name: Patch Version
    run: uv version --bump patch && git add pyproject.toml

  - name: Update Dependencies
    run: uv lock --upgrade && uv sync

  - name: Add Dependency Updates To Git
    run: git add pyproject.toml uv.lock
```

### Build Workflow Steps

The build workflow builds artifacts after health check passes on main:

```yaml
steps:
  - name: Build Wheel
    run: uv build

  - name: Upload Artifacts
    uses: actions/upload-artifact@main
```

### Release Workflow Steps

The release workflow creates releases after build passes:

```yaml
steps:
  - name: Download Artifacts
    uses: actions/download-artifact@main

  - name: Create And Push Tag
    run: git tag v$(uv version --short) && git push origin v$(uv version --short)
```

### Publish Workflow Steps

The publish workflow deploys to PyPI:

```yaml
steps:
  - name: Build Wheel
    run: uv build

  - name: Publish To PyPI
    run: uv publish --token ${{ secrets.PYPI_TOKEN }}
```

## Python Version Management

pyrig queries and manages Python version constraints:

### Querying Versions

```python
from pyrig.dev.configs.pyproject import PyprojectConfigFile

# Get minimum supported version
min_version = PyprojectConfigFile.get_first_supported_python_version()
# Returns: Version("3.12")

# Get all supported versions
versions = PyprojectConfigFile.get_supported_python_versions()
# Returns: [Version("3.12"), Version("3.13"), Version("3.14")]

# Get latest possible version
latest = PyprojectConfigFile.get_latest_possible_python_version()
# Returns: Version("3.14")
```

### Version Constraints

The `VersionConstraint` class parses PEP 440 specifiers:

```python
from pyrig.src.project.versions import VersionConstraint

constraint = VersionConstraint(">=3.12,<4.0")
lower = constraint.get_lower_inclusive()  # Version("3.12")
upper = constraint.get_upper_exclusive()  # Version("4.0")
versions = constraint.get_version_range(level="minor")
# Returns: [Version("3.12"), Version("3.13"), Version("3.14")]
```

### Fetching Latest Python Version

pyrig can fetch the latest stable Python version from the endoflife.date API:

```python
@classmethod
@return_resource_content_on_fetch_error(resource_name="LATEST_PYTHON_VERSION")
@cache
def fetch_latest_python_version(cls) -> str:
    """Fetch the latest stable Python version from endoflife.date.

    Falls back to local resource file if fetch fails.
    """
    url = "https://endoflife.date/api/python.json"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data[0]["latest"]

@classmethod
def get_latest_python_version(
    cls, level: Literal["major", "minor", "micro"] = "minor"
) -> Version:
    """Get the latest stable Python version as a Version object."""
    latest_version = Version(cls.fetch_latest_python_version())
    return adjust_version_to_level(latest_version, level)
```

The `@return_resource_content_on_fetch_error` decorator ensures that if the API is unavailable, pyrig falls back to a cached version stored in `pyrig/resources/LATEST_PYTHON_VERSION`. This provides offline capability and resilience to network failures.

## Project Initialization

The `init()` function orchestrates dependency setup:

```python
SETUP_STEPS = [
    ConfigFile.init_priority_config_files,      # Write pyproject.toml
    PyprojectConfigFile.install_dependencies,   # uv sync (install dev deps)
    PyprojectConfigFile.update_dependencies,    # uv lock --upgrade
    run_mkroot,                                 # Create project structure
    run_mktests,                                # Generate test files
    PreCommitConfigConfigFile.run_hooks,        # Format code
    ConftestConfigFile.run_tests,               # Verify setup
    PyprojectConfigFile.install_dependencies,   # Activate CLI entry points
    commit_initial_changes,                     # Git commit all changes
]
```

## Common Workflows

### Adding a New Dependency

```bash
# Add runtime dependency
uv add requests

# Add development dependency
uv add --dev pytest-cov

# Rebuild to update configs
uv run pyrig build
```

### Updating All Dependencies

```bash
# Update lock file
uv lock --upgrade

# Install updated versions
uv sync
```

### Checking Installed Versions

```bash
# Show all installed packages
uv pip list

# Show specific package
uv pip show requests
```

## Troubleshooting

### "No module named X"

**Cause**: Dependencies not installed or outdated.

**Solution**:
```bash
uv sync
```

### "Version conflict"

**Cause**: Incompatible version requirements between packages.

**Solution**:
```bash
# Update all to resolve
uv lock --upgrade
uv sync

# If specific package causes issues, try pinning it
uv add "package>=1.0,<2.0"
```

### "Lock file out of date"

**Cause**: pyproject.toml changed but lock file not updated.

**Solution**:
```bash
uv lock
uv sync
```

### "Build backend not found"

**Cause**: uv_build not installed.

**Solution**:
```bash
uv sync  # This installs uv_build from pyproject.toml
```

### CI fails with dependency errors

**Cause**: Lock file not committed or out of sync.

**Solution**:
1. Run `uv lock` locally
2. Commit `uv.lock`
3. Push changes

## Summary

| Component | Purpose |
|-----------|---------|
| **uv** | Fast Python package manager |
| **pyproject.toml** | Project configuration and metadata |
| **uv.lock** | Reproducible dependency versions |
| **Version bumping** | Automated via `uv version --bump patch` |
| **CI integration** | `uv sync`, `uv lock --upgrade`, `uv build`, `uv publish` |
| **Version-free deps** | Simplifies management, lock file tracks exact versions |

