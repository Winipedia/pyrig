# Architecture: File Generation System

This document describes pyrig's ConfigFile system — the core mechanism that automatically generates and manages project configuration files.

## Overview

When you run `pyrig init` or `pyrig mkroot`, pyrig discovers all `ConfigFile` subclasses and initializes them, creating a complete project structure. The system supports multiple file formats (YAML, TOML, Python, plain text) and ensures configurations stay consistent while respecting user customizations.

## Generated Project Structure

Running `pyrig init` on a new project generates the following structure:

```
your-project/
├── .env                           # Environment variables (gitignored)
├── .experiment.py                 # Local experimentation file (gitignored)
├── .gitignore                     # Git ignore patterns
├── .pre-commit-config.yaml        # Pre-commit hooks configuration
├── .python-version                # Python version for pyenv
├── docs/
│   └── index.md                   # Documentation index
├── LICENSE                        # License file (user fills in)
├── README.md                      # Project readme with header
├── pyproject.toml                 # Central project configuration
│
├── .github/
│   └── workflows/
│       ├── health_check.yaml      # CI: tests, linting, type checking
│       ├── build.yaml             # Build artifacts after health check on main
│       ├── publish.yaml           # Publish to PyPI after release
│       └── release.yaml           # Create GitHub releases after build
│
├── your_project/                  # Source package (matches project name)
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── py.typed                   # PEP 561 type marker
│   │
│   ├── dev/
│   │   ├── __init__.py
│   │   ├── builders/
│   │   │   └── __init__.py        # Custom builders go here
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── subcommands.py     # Custom CLI commands
│   │   ├── configs/
│   │   │   └── __init__.py        # Custom ConfigFile classes
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── fixtures/
│   │           └── __init__.py    # Custom fixtures (auto-discovered)
│   ├── resources/
│   │   └── __init__.py            # Build resources (icons, etc.) go here
│   └── src/
│       └── __init__.py            # Core utilities go here
│
└── tests/
    ├── __init__.py
    ├── conftest.py                # Pytest configuration
    ├── test_zero.py               # Placeholder test
    └── test_your_project/         # Auto-generated test structure
        └── ...                    # Mirrors source structure
```

## ConfigFile Class Hierarchy

The ConfigFile system uses an abstract base class pattern with format-specific subclasses:

```
ConfigFile (ABC)
├── YamlConfigFile
│   ├── PreCommitConfigConfigFile     → .pre-commit-config.yaml
│   └── Workflow (ABC)
│       ├── HealthCheckWorkflow       → health_check.yaml
│       ├── BuildWorkflow             → build.yaml
│       ├── PublishWorkflow           → publish.yaml
│       └── ReleaseWorkflow           → release.yaml
│
├── TomlConfigFile
│   └── PyprojectConfigFile           → pyproject.toml
│
├── TextConfigFile
│   ├── LicenceConfigFile             → LICENSE
│   ├── MarkdownConfigFile
│   │   ├── ReadmeConfigFile          → README.md
│   │   └── IndexConfigFile           → docs/index.md
│   └── PythonConfigFile
│       ├── DotExperimentConfigFile   → .experiment.py
│       ├── PythonTestsConfigFile
│       │   ├── ZeroTestConfigFile    → test_zero.py
│       │   └── ConftestConfigFile    → conftest.py
│       └── PythonPackageConfigFile
│           ├── MainTestConfigFile    → test_main.py
│           ├── CopyModuleConfigFile
│           │   └── MainConfigFile    → main.py
│           └── CopyModuleOnlyDocstringConfigFile
│               ├── SubcommandsConfigFile → subcommands.py
│               └── InitConfigFile (various) → __init__.py files
│
├── TypedConfigFile
│   └── PyTypedConfigFile             → py.typed
│
├── GitIgnoreConfigFile               → .gitignore
├── DotEnvConfigFile                  → .env
└── DotPythonVersionConfigFile        → .python-version
```

## Initialization Order

Config files are initialized in a specific order to handle dependencies:

### Priority Files (First)

These files must exist before other config files can be created:

1. **GitIgnoreConfigFile** — Creates `.gitignore` so other files know what to exclude
2. **PyprojectConfigFile** — Creates `pyproject.toml` with project metadata needed by other configs
3. **MainConfigFile** — Creates `main.py` entry point
4. **ConfigsInitConfigFile** — Creates `dev/configs/__init__.py` for custom configs
5. **BuildersInitConfigFile** — Creates `dev/builders/__init__.py` for custom builders
6. **ZeroTestConfigFile** — Creates `test_zero.py` so pytest has at least one test

### Ordered Files (Second)

These files depend on other ordered files:

1. **FixturesInitConfigFile** — Creates fixtures directory structure
2. **ConftestConfigFile** — Creates `conftest.py` (depends on fixtures)

### Remaining Files (Last)

All other ConfigFile subclasses are initialized in no particular order.

## How ConfigFile Works

### Lifecycle

When a ConfigFile subclass is instantiated, it follows this lifecycle:

```python
def __init__(self):
    # 1. Create parent directories if needed
    self.get_path().parent.mkdir(parents=True, exist_ok=True)

    # 2. Create file with defaults if it doesn't exist
    if not self.get_path().exists():
        self.get_path().touch()
        self.dump(self.get_configs())

    # 3. Validate and merge missing configs
    if not self.is_correct():
        config = self.add_missing_configs()
        self.dump(config)

    # 4. Final validation
    if not self.is_correct():
        raise ValueError(f"Config file {self.get_path()} is not correct.")
```

### Subset Validation

The system uses **subset validation**: a config file is considered "correct" if the expected configuration is a **subset** of what exists in the file. This means:

- Users can **add** keys/values without breaking validation
- Users can **extend** arrays with additional items
- Users **cannot remove** required keys/values
- Users **cannot change** the values of existing required keys

Example: If pyrig expects `{"tool": {"ruff": {"lint": {"select": ["ALL"]}}}}`, a user's config with additional ruff settings will still pass validation as long as `select: ["ALL"]` is present.

### Merging Missing Configs

When validation fails, pyrig attempts to **merge** missing configurations:

```python
@classmethod
def add_missing_configs(cls):
    current_config = cls.load()        # What's in the file now
    expected_config = cls.get_configs() # What pyrig expects

    # Recursively add missing keys/values
    nested_structure_is_subset(
        expected_config,
        current_config,
        cls.add_missing_dict_val,      # Handler for missing dict keys
        cls.insert_missing_list_val,   # Handler for missing list items
    )
    return current_config
```

### User Opt-Out Mechanism

If a config file exists but is **empty**, pyrig treats it as "user opted out":

```python
@classmethod
def is_unwanted(cls) -> bool:
    return (
        cls.get_path().exists() and
        cls.get_path().read_text(encoding="utf-8") == ""
    )
```

This allows users to prevent pyrig from managing a specific file by emptying it.
For example if your project doesn't use pre-commit, you can empty `.pre-commit-config.yaml` to prevent pyrig from managing it. Or if you do not want to publish to PyPI, you can empty `publish.yaml`.

## Multi-Package Discovery

ConfigFile subclasses are automatically discovered across all packages that depend on pyrig:

```python
@classmethod
def get_all_subclasses(cls) -> list[type["ConfigFile"]]:
    return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
        cls,
        pyrig,
        configs,
        discard_parents=True,
    )
```

This enables:
- **Ecosystem-wide configuration**: Shared ConfigFile classes across related packages
- **Override behavior**: Child packages can subclass parent ConfigFile classes to customize behavior
- **Automatic integration**: New ConfigFile subclasses are automatically discovered and initialized

Lets say you make a package for PySide6 and you have to add additional system installation for CI/CD in GitHub Actions. You can create a subclass of `HealthCheckWorkflow` and add the additional steps you need. Pyrig will automatically discover it and use it instead of the base class.
Now every package that uses your package will automatically get the additional steps.
Also pyrig just inits the most recent leave of a class tree. So pyrigs own `HealthCheckWorkflow` will not be inited but only the subclass from your package.

## Generated Files Reference

### Root Configuration Files

| File | Class | Purpose |
|------|-------|---------|
| `.gitignore` | `GitIgnoreConfigFile` | Git ignore patterns for Python projects, virtual environments, build artifacts |
| `.pre-commit-config.yaml` | `PreCommitConfigConfigFile` | Pre-commit hooks for ruff, mypy, and bandit |
| `.python-version` | `DotPythonVersionConfigFile` | Python version for pyenv and uv |
| `.env` | `DotEnvConfigFile` | Environment variables (gitignored) |
| `.experiment.py` | `DotExperimentConfigFile` | Local experimentation file (gitignored) |
| `pyproject.toml` | `PyprojectConfigFile` | Central project configuration (dependencies, tools, metadata) |
| `LICENSE` | `LicenceConfigFile` | License file with placeholder for user to fill |
| `README.md` | `ReadmeConfigFile` | Project readme with header |
| `docs/index.md` | `IndexConfigFile` | Documentation index |

### GitHub Workflows

| File | Class | Purpose |
|------|-------|---------|
| `.github/workflows/health_check.yaml` | `HealthCheckWorkflow` | CI pipeline: tests, linting, type checking across OS/Python matrix. Will also run on every Pull Request as a required check |
| `.github/workflows/build.yaml` | `BuildWorkflow` | Builds artifacts after health check passes on main, uploads for downstream workflows |
| `.github/workflows/release.yaml` | `ReleaseWorkflow` | Creates GitHub releases after build passes, downloads artifacts from build workflow |
| `.github/workflows/publish.yaml` | `PublishWorkflow` | Publishes to PyPI after successful release |

### Source Package Files

| File | Class | Purpose |
|------|-------|---------|
| `{pkg}/main.py` | `MainConfigFile` | CLI entry point with `main()` and `__name__ == "__main__"` guard |
| `{pkg}/py.typed` | `PyTypedConfigFile` | PEP 561 marker for typed packages |
| `{pkg}/dev/cli/subcommands.py` | `SubcommandsConfigFile` | Custom CLI subcommands |
| `{pkg}/dev/configs/__init__.py` | `ConfigsInitConfigFile` | Custom ConfigFile classes |
| `{pkg}/dev/builders/__init__.py` | `BuildersInitConfigFile` | Custom artifact builders |
| `{pkg}/resources/__init__.py` | `ResourcesInitConfigFile` | Build resources |
| `{pkg}/src/__init__.py` | `SrcInitConfigFile` | Core utilities |

### Test Files

| File | Class | Purpose |
|------|-------|---------|
| `tests/conftest.py` | `ConftestConfigFile` | Pytest configuration and shared fixtures |
| `tests/test_zero.py` | `ZeroTestConfigFile` | Placeholder test to ensure pytest runs |
| `tests/test_{pkg}/test_main.py` | `MainTestConfigFile` | Tests for main.py |

### Fixture Scope Files

| File | Class | Purpose |
|------|-------|---------|
| `{pkg}/dev/tests/fixtures/__init__.py` | `FixturesInitConfigFile` | Fixtures package |

Any fixture defined in any file under `dev/tests/fixtures/` is automatically discovered and added as a pytest plugin. This means fixtures are shared across all packages that depend on pyrig. For example, pyrig's `config_file_factory` fixture is automatically available in all dependent packages. E.g. If you define an autouse session fixture in your package, it will run before every test in every dependent package. 

## Creating Custom ConfigFile Classes

To add custom configuration files to your project, create a subclass in `{pkg}/dev/configs/`:

```python
# your_project/dev/configs/my_config.py
from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile

class MyCustomConfigFile(YamlConfigFile):
    """Custom configuration file for my tool."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path()  # Project root

    @classmethod
    def get_filename(cls) -> str:
        return "my-tool-config"  # Creates my-tool-config.yaml

    @classmethod
    def get_configs(cls) -> dict:
        return {
            "version": 1,
            "settings": {
                "enabled": True,
            }
        }
```

The next time `pyrig init` or `pyrig mkroot` runs, your custom config file will be automatically discovered and created.

## Key Design Decisions

### Why Subset Validation?

Subset validation allows users to extend configurations without breaking pyrig's expectations. This is crucial because:

1. **User customization is preserved**: Adding extra linting rules, test configurations, or tool settings won't be overwritten
2. **Required settings are enforced**: Core configurations that pyrig depends on are always present
3. **Merge conflicts are minimized**: pyrig only adds what's missing, never removes what exists
