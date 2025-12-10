# Multi-Package Support

This document describes pyrig's multi-package architecture, which enables dependent packages to extend pyrig's functionality by adding their own ConfigFile classes, Builder classes, fixtures, and CLI commands.

## Overview

pyrig is designed to act as a base package that other packages can depend on. When you add pyrig as a dependency, your package can:

- Define custom ConfigFile subclasses → pyrig discovers and initializes them
- Define custom Builder subclasses → pyrig discovers and runs them
- Define custom fixtures → pytest discovers and uses them
- Define custom CLI commands → available via your project's CLI

This architecture enables:
- Company-wide base packages that extend pyrig with internal standards
- Shared configurations across multiple projects
- Plugin-style extensibility

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Dependency Graph Discovery                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   your_project                                                       │
│        │                                                             │
│        └──depends on──► company_base                                 │
│                              │                                       │
│                              └──depends on──► pyrig                  │
│                                                                      │
├─────────────────────────────────────────────────────────────────────┤
│                      Discovery Direction                             │
│                                                                      │
│   pyrig ◄── discovers ── company_base ◄── discovers ── your_project │
│                                                                      │
│   - First: pyrig's ConfigFile/Builder classes                       │
│   - Then: company_base's extensions                                  │
│   - Finally: your_project's extensions                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## How Discovery Works

### The DependencyGraph Class

pyrig uses a `DependencyGraph` class to build a graph of all installed Python packages and their dependencies:

```python
from pyrig.src.modules.package import DependencyGraph

graph = DependencyGraph()
dependents = graph.get_all_depending_on("pyrig")
# Returns: [your_project_module, company_base_module]
```

The graph is built from `importlib.metadata.distributions()` which scans all installed packages.

### Module Path Replacement

The key insight is that dependent packages mirror pyrig's directory structure. pyrig uses this to find equivalent modules:

```
pyrig/dev/configs/          →  your_project/dev/configs/
pyrig/dev/builders/         →  your_project/dev/builders/
pyrig/dev/tests/fixtures/   →  your_project/dev/tests/fixtures/
```

The `get_same_modules_from_deps_depen_on_dep()` function performs this discovery:

```python
from pyrig.src.modules.module import get_same_modules_from_deps_depen_on_dep
from pyrig.dev import configs
import pyrig

# Find all equivalent config modules across the dependency tree
modules = get_same_modules_from_deps_depen_on_dep(configs, pyrig)
# Returns: [pyrig.dev.configs, company_base.dev.configs, your_project.dev.configs]
```

### Discovery Order

Packages are sorted by dependency count (more dependencies = loaded later):

1. **pyrig** (base, fewest dependencies)
2. **company_base** (depends on pyrig)
3. **your_project** (depends on company_base and pyrig)

This ensures base classes are defined before subclasses that extend them.

## Extension Points

### 1. ConfigFile Extensions

Custom configuration files are discovered in `your_project/dev/configs/`:

```
your_project/
└── dev/
    └── configs/
        ├── __init__.py
        └── custom_config.py   ← Your ConfigFile classes go here
```

**Example: Custom ConfigFile**

```python
# your_project/dev/configs/custom_config.py
from pyrig.dev.configs.base.base import TomlConfigFile

class MyCustomConfigFile(TomlConfigFile):
    """Custom TOML configuration file."""
    
    @classmethod
    def get_path_relative_to_root(cls) -> Path:
        return Path("my-config.toml")
    
    @classmethod
    def get_expected_config(cls) -> dict[str, Any]:
        return {
            "setting1": "value1",
            "setting2": True,
        }
```

When `pyrig mkroot` runs, it discovers and initializes all ConfigFile subclasses.

### 2. Builder Extensions

Custom builders are discovered in `your_project/dev/builders/`:

```
your_project/
└── dev/
    └── builders/
        ├── __init__.py
        └── custom_builder.py   ← Your Builder classes go here
```

**Example: Custom Builder**

```python
# your_project/dev/builders/custom_builder.py
from pyrig.dev.builders.base.base import Builder
from pathlib import Path

class MyCustomBuilder(Builder):
    """Builds custom artifacts for my project."""

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Create artifacts in the temporary directory."""
        artifact_path = temp_artifacts_dir / "my_artifact.txt"
        artifact_path.write_text("Generated content")
```

When `pyrig build` runs, it discovers and invokes all Builder subclasses.

### 3. Fixture Extensions

Custom fixtures are discovered in `your_project/dev/tests/fixtures/`:

```
your_project/
└── dev/
    └── tests/
        └── fixtures/
            ├── __init__.py
            └── custom_fixtures.py   ← Your fixtures go here
```

**Example: Custom Fixtures**

```python
# your_project/dev/tests/fixtures/custom_fixtures.py
import pytest

@pytest.fixture
def my_custom_fixture():
    """Provide a custom test fixture."""
    return {"test_data": "value"}

@pytest.fixture(scope="session", autouse=True)
def my_session_setup():
    """Run once per test session."""
    print("Setting up custom session...")
    yield
    print("Tearing down custom session...")
```

These fixtures are automatically discovered and available in all tests.

### 4. CLI Extensions

Custom CLI commands are defined in `your_project/dev/cli/subcommands.py`:

```
your_project/
└── dev/
    └── cli/
        ├── __init__.py
        ├── cli.py           ← Entry point (copied from pyrig)
        └── subcommands.py   ← Your custom commands go here
```

**Example: Custom CLI Commands**

```python
# your_project/dev/cli/subcommands.py
def deploy() -> None:
    """Deploy the application to production."""
    from your_project.src.deployment import run_deploy
    run_deploy()

def generate_docs() -> None:
    """Generate project documentation."""
    from your_project.src.docs import build_docs
    build_docs()
```

These become available as `your-project deploy` and `your-project generate-docs`.

**Note:** CLI commands are separate from pyrig's commands. You use `pyrig init` for pyrig operations, and `your-project deploy` for your project's operations.

---

## How Each Extension is Discovered

### ConfigFile Discovery

The `ConfigFile.get_all_subclasses()` method:

```python
@classmethod
def get_all_subclasses(cls) -> list[type["ConfigFile"]]:
    return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
        cls,
        pyrig,
        configs,  # pyrig.dev.configs
        discard_parents=True,
    )
```

This:
1. Finds all packages that depend on pyrig
2. Looks for `{package}.dev.configs` in each
3. Discovers all ConfigFile subclasses in those modules
4. Discards parent classes, keeping only leaf implementations

### Builder Discovery

The `Builder.get_non_abstract_subclasses()` method:

```python
@classmethod
def get_non_abstract_subclasses(cls) -> list[type["Builder"]]:
    return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
        cls,
        pyrig,
        builders,  # pyrig.dev.builders
        discard_parents=True,
    )
```

### Fixture Discovery

The `conftest.py` discovers fixtures:

```python
# pyrig/dev/tests/conftest.py
from pyrig.dev.tests import fixtures
from pyrig.src.modules.module import get_same_modules_from_deps_depen_on_dep
import pyrig

fixtures_pkgs = get_same_modules_from_deps_depen_on_dep(fixtures, pyrig)

pytest_plugin_paths: list[Path] = []
for pkg in fixtures_pkgs:
    for path in Path(pkg.__path__[0]).rglob("*.py"):
        pytest_plugin_paths.append(path)

pytest_plugins = [to_module_name(path) for path in pytest_plugin_paths]
```

All `.py` files in `dev/tests/fixtures/` across all dependent packages become pytest plugins.

---

## Use Cases

### 1. Company-Wide Base Package

Create a company package that extends pyrig with internal standards:

```
acme_pyrig/
├── pyproject.toml          # depends on pyrig
└── acme_pyrig/
    └── dev/
        ├── configs/
        │   ├── internal_lint.py    # Company linting config
        │   └── security.py         # Security scanning config
        ├── artifacts/
        │   └── builders/
        │       └── compliance.py   # Compliance artifact builder
        └── tests/
            └── fixtures/
                └── company.py      # Company-wide test fixtures
```

All company projects then depend on `acme_pyrig` instead of `pyrig` directly.

### 2. Multiple Projects Sharing Configurations

```
                    pyrig
                      ▲
                      │
              acme_pyrig (company base)
                      ▲
          ┌───────────┼───────────┐
          │           │           │
     project_a   project_b   project_c
```

All three projects get:
- pyrig's base functionality
- acme_pyrig's company standards
- Their own project-specific extensions

### 3. Plugin Architecture

Create optional plugins that add functionality:

```python
# pyproject.toml for a project using plugins
[project]
dependencies = [
    "pyrig",
    "pyrig-docker-plugin",      # Adds Docker-related configs
    "pyrig-aws-plugin",         # Adds AWS-related configs
]
```

Each plugin adds its own ConfigFile and Builder classes that pyrig discovers automatically.

---

## Required Directory Structure

For extensions to be discovered, your package must mirror pyrig's structure:

```
your_project/
├── pyproject.toml
├── your_project/
│   ├── __init__.py
│   ├── main.py                        # → "your-project main"
│   ├── src/                           # Your source code
│   └── dev/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── cli.py                 # Entry point
│       │   └── subcommands.py         # Custom CLI commands
│       ├── configs/
│       │   ├── __init__.py
│       │   └── *.py                   # Custom ConfigFile classes
│       ├── artifacts/
│       │   └── builders/
│       │       ├── __init__.py
│       │       └── *.py               # Custom Builder classes
│       └── tests/
│           ├── __init__.py
│           ├── conftest.py
│           └── fixtures/
│               ├── __init__.py
│               └── *.py               # Custom fixtures
└── tests/
    └── ...                            # Test files
```

**Tip:** Run `pyrig init` to scaffold this structure automatically.

---

## Debugging Discovery Issues

### Check Which Packages Are Found

```python
from pyrig.src.modules.package import DependencyGraph

graph = DependencyGraph()
dependents = graph.get_all_depending_on("pyrig")
print([m.__name__ for m in dependents])
```

### Check Which ConfigFiles Are Discovered

```python
from pyrig.dev.configs.base.base import ConfigFile

subclasses = ConfigFile.get_all_subclasses()
for cls in subclasses:
    print(f"{cls.__module__}.{cls.__name__}")
```

### Check Which Builders Are Discovered

```python
from pyrig.dev.builders.base.base import Builder

subclasses = Builder.get_non_abstract_subclasses()
for cls in subclasses:
    print(f"{cls.__module__}.{cls.__name__}")
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Extension not discovered | Package not installed | Run `uv sync` |
| Extension not discovered | Missing `__init__.py` | Add `__init__.py` to all directories |
| Extension not discovered | Wrong directory path | Check structure matches pyrig's |
| "Package not found in dependency graph" | Package not yet installed | Install with `uv add` first |
| Subclass not found | Class is abstract | Remove `ABC` base or implement abstract methods |

---

## The Discovery Functions

### `DependencyGraph.get_all_depending_on()`

Finds all packages that depend on a given package:

```python
def get_all_depending_on(
    self, package: ModuleType | str, *, include_self: bool = False
) -> list[ModuleType]:
    """Find all packages that depend on the given package.

    Results are sorted by dependency count (fewer dependencies first).
    This ensures base packages are processed before their dependents.
    """
```

### `get_same_modules_from_deps_depen_on_dep()`

Finds equivalent modules across all dependent packages:

```python
def get_same_modules_from_deps_depen_on_dep(
    module: ModuleType, dep: ModuleType
) -> list[ModuleType]:
    """Find equivalent modules across all packages depending on a dependency.

    Given pyrig.dev.configs, finds:
    - pyrig.dev.configs
    - company_base.dev.configs
    - your_project.dev.configs
    """
```

### `get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep()`

Finds all non-abstract subclasses across dependent packages:

```python
def get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
    cls: type,
    dep: ModuleType,
    load_package_before: ModuleType,
    *,
    discard_parents: bool = False,
) -> list[type]:
    """Find non-abstract subclasses across all packages depending on a dependency.

    This is the core discovery function for ConfigFile and Builder classes.
    """
```

---

## Summary

| Extension Point | Location | Discovery Method |
|----------------|----------|------------------|
| ConfigFile | `dev/configs/*.py` | `ConfigFile.get_all_subclasses()` |
| Builder | `dev/builders/*.py` | `Builder.get_non_abstract_subclasses()` |
| Fixtures | `dev/tests/fixtures/*.py` | `conftest.py` pytest_plugins |
| CLI Commands | `dev/cli/subcommands.py` | `get_all_functions_from_module()` |

pyrig's multi-package architecture enables a powerful plugin-style extensibility model where:
1. pyrig provides the base framework
2. Company packages add organization standards
3. Individual projects add project-specific customizations

All extensions are automatically discovered and integrated through the dependency graph.
