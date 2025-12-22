# Configuration File Architecture

pyrig's ConfigFile system provides automatic creation, validation, and updating of project configuration files through a declarative class-based architecture.

## Core Concepts

### ConfigFile Base Class

The `ConfigFile` abstract base class is the foundation of the configuration system. All config files inherit from it or one of its format-specific subclasses.

```mermaid
graph TD
    A[ConfigFile] --> B[YamlConfigFile]
    A --> C[TomlConfigFile]
    A --> D[TextConfigFile]
    A --> E[TypedConfigFile]
    A --> F[JsonConfigFile]

    B --> B1[YmlConfigFile]
    B --> B2[Workflow]

    D --> D1[TxtConfigFile]
    D --> D2[MarkdownConfigFile]
    D --> D3[PythonConfigFile]

    D2 --> D2A[BadgesMarkdownConfigFile]

    D3 --> D3A[PythonPackageConfigFile]
    D3 --> D3B[PythonTestsConfigFile]

    D3A --> D3A1[CopyModuleConfigFile]
    D3A1 --> D3A1A[CopyModuleOnlyDocstringConfigFile]
    D3A1A --> D3A1A1[InitConfigFile]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style E fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style F fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style B2 fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

### Required Methods

Every ConfigFile subclass must implement:

| Method | Purpose | Returns |
|--------|---------|---------|
| `get_parent_path()` | Directory containing the file | `Path` |
| `get_file_extension()` | File extension without dot | `str` |
| `get_configs()` | Expected configuration structure | `dict` or `list` |
| `load()` | Parse file content | `dict` or `list` |
| `dump(config)` | Write configuration to file | `None` |

## Initialization Process

When a ConfigFile is instantiated, it follows this process:

```mermaid
graph TD
    A[ConfigFile instantiated] --> B[Create parent directories]
    B --> C{File exists?}
    C -->|No| D[Create file with default content]
    C -->|Yes| E{Is correct?}
    D --> E
    E -->|No| F[Add missing configs]
    E -->|Yes| H[Done]
    F --> G{Is correct now?}
    G -->|Yes| H
    G -->|No| I[Raise ValueError]
    
    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style E fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style F fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style G fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style H fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style I fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

### Validation Logic

A config file is considered correct if:
1. **Empty file** - User opted out of this configuration file
2. **Superset validation** - Actual config contains all expected keys/values

The validation uses `nested_structure_is_subset` to recursively check that the expected configuration is a subset of the actual configuration. Please only use lists and dicts to define your configuration.

### Smart Merging

When configs are missing, the system intelligently merges them:
- **Dict values** - Missing keys are added and key that have wrong values are corrected. So watch out! Pyrig does overwrite values.
- **List values** - Missing items are inserted at the correct index
- **User additions** - Preserved during merge as long as not incorrectly overwriting defaults that pyrig asserts and enforces via overwriting wrong values.

Note:
If you want to change default values, you will have to subclass the specific config file and overwrite the `get_configs` method or any other method you want behavior adjusted in. I highly recommend keeping the class name the same as the filename is derived from it unless you overwrite `get_filename`. Just import the class from pyrig via the as syntax: `from pyrig.dev.configs.some.config_file import MainConfigFile as BaseMainConfigFile` and subclass it.

## Automatic Discovery

ConfigFile subclasses are automatically discovered across all packages depending on pyrig:

```mermaid
graph LR
    A[pyrig.dev.configs] --> D[All discovered]
    B[pkg_a.dev.configs] --> D
    C[myapp.dev.configs] --> D
    D --> E[make_project_root called]
    E --> F[All configs initialized]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
    style E fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style F fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
```

Discovery uses `get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep` with `discard_parents=True`, meaning only leaf implementations are initialized.
This way you can subclass a config file and only your subclass will be initialized.
This makes it easy to adjust any config file to your liking.

Note: I highly recommend doing any changes to config files via a subclass and not directly in the file itself. This way you can regenerate the file at any time and it will not overwrite your changes. Also this way packages that will later depend on your package will automatically get your config file adjustments as well.

### Initialization Order

Config files are initialized in three phases during `pyrig init` or `pyrig mkroot`:

1. **Priority files** - Required by other configs (e.g. pyproject.toml, .gitignore, LICENSE, main.py), these must exist before other initialization can proceed.
2. **Ordered files** - Have dependencies on each other (e.g. fixtures/__init__.py, conftest.py)
3. **Remaining files** - All other discovered configs in a non-deterministic order.

#### Priority Initialization System

The priority initialization system is implemented in `pyrig/dev/cli/commands/create_root.py` with three key functions:

**`get_priority_config_files()`** - Returns config files that must be initialized first:
```python
def get_priority_config_files() -> list[type[ConfigFile]]:
    """Get config files that must be initialized first.

    These files are required by other config files or the build
    process and must exist before other initialization can proceed.
    """
    return [
        GitIgnoreConfigFile,      # Git ignore patterns
        PyprojectConfigFile,      # Project metadata and dependencies
        LicenceConfigFile,        # Project license
        MainConfigFile,           # CLI entry point
        ConfigsInitConfigFile,    # configs/__init__.py
        BuildersInitConfigFile,   # builders/__init__.py
        ZeroTestConfigFile,       # Initial test file
        FixturesInitConfigFile,   # fixtures/__init__.py
    ]
```

**`get_ordered_config_files()`** - Returns config files with specific ordering requirements:
```python
def get_ordered_config_files() -> list[type[ConfigFile]]:
    """Get config files that must be initialized in a specific order.

    These files have dependencies on each other and must be
    initialized after priority files but before general files.
    """
    return []  # Currently empty, but available for future use
```

**`get_unordered_config_files()`** - Returns all remaining config files:
```python
def get_unordered_config_files() -> list[type[ConfigFile]]:
    """Get all remaining config files.

    These files have no dependencies on each other and can be
    initialized in any order after priority and ordered files.
    """
    all_config_files = ConfigFile.get_all_subclasses()
    priority_and_ordered = get_priority_config_files() + get_ordered_config_files()
    return [cf for cf in all_config_files if cf not in priority_and_ordered]
```

You can create only priority config files using:
```bash
uv run pyrig mkroot --priority
```

This is useful during initial project setup when you need the essential files before installing dependencies.

## Format-Specific Subclasses
These subclasses implement already all the required methods for you that they can and simplfy creating ConfigFiles for the specific format.
Examples are the methods `load` and `dump` that are implemented for you or the file extension is set for you.

### JsonConfigFile

For JSON configuration files using Python's json module:

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.json import JsonConfigFile

class MyConfigFile(JsonConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {"key": "value"}
```

Creates `config/my_config.json`.

### YamlConfigFile

For YAML configuration files using PyYAML:

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.yaml import YamlConfigFile

class MyConfigFile(YamlConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {"key": "value"}
```

Creates `config/my_config.yaml`.

### TomlConfigFile

For TOML files using tomlkit (preserves formatting):

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.toml import TomlConfigFile

class MyConfigFile(TomlConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        return Path(".")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        return {"tool": {"myapp": {"setting": "value"}}}
```

Creates `my_config.toml` with pretty formatting.

### TextConfigFile

Note: this is not a txt file. The word text is used to indicate that it is a plain text file, this includes all files that can not be represented like a list or dict.
A .py, .txt or .md file are all text files. But file like .gitignore, .md, .yaml files fro exampe all can be represented as dicts or lists and should use the more specific subclasses.

For plain text files with required content:

```python
from pathlib import Path
from pyrig.dev.configs.base.text import TextConfigFile

class MyConfigFile(TextConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        return Path(".")

    @classmethod
    def get_content_str(cls) -> str:
        return "# Required header\n"

    @classmethod
    def get_file_extension(cls) -> str:
        return "someext"
```

Creates `my_config.someext`.
File is considered correct if it contains the required content. So you can add your own content after the required content or before it.

### PythonConfigFile

For Python source files:

```python
from pathlib import Path
from pyrig.dev.configs.base.python import PythonConfigFile

class MyConfigFile(PythonConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("myapp/src")

    @classmethod
    def get_content_str(cls) -> str:
        return '"""Module docstring."""\n\ndef main():\n    pass\n'
```

Creates `myapp/src/my_config.py`.

### Workflow

For GitHub Actions workflow files in `.github/workflows/`:

```python
from typing import Any
from pyrig.dev.configs.workflows.base.base import Workflow

class MyWorkflow(Workflow):
    @classmethod
    def get_workflow_triggers(cls) -> dict[str, Any]:
        """Define when the workflow runs."""
        triggers = super().get_workflow_triggers()
        triggers.update(cls.on_push())  # Trigger on push
        return triggers

    @classmethod
    def get_jobs(cls) -> dict[str, Any]:
        """Define the workflow jobs."""
        return {
            "my-job": {
                "runs-on": cls.UBUNTU_LATEST,
                "steps": [
                    cls.step_checkout(),
                    cls.step_setup_python(),
                    {"name": "Run tests", "run": "pytest"}
                ]
            }
        }
```

Creates `.github/workflows/my_workflow.yaml`. The Workflow class provides many helper methods for building jobs, steps, triggers, and matrix strategies. See the workflow documentation for details.

## Advanced Subclasses

### CopyModuleConfigFile

Copies entire module content from pyrig to your project:

```python
from types import ModuleType
from pyrig.dev.configs.base.py_package import CopyModuleConfigFile
from pyrig.dev.cli import subcommands

class SubcommandsConfigFile(CopyModuleConfigFile):
    @classmethod
    def get_src_module(cls) -> ModuleType:
        return subcommands
```

Creates `myapp/dev/cli/subcommands.py` with full content from `pyrig.dev.cli.subcommands`.

### CopyModuleOnlyDocstringConfigFile

Copies only the docstring, allowing custom implementation:

```python
from types import ModuleType
from pyrig.dev.configs.base.py_package import CopyModuleOnlyDocstringConfigFile
from pyrig.dev.cli import shared_subcommands

class SharedSubcommandsConfigFile(CopyModuleOnlyDocstringConfigFile):
    @classmethod
    def get_src_module(cls) -> ModuleType:
        return shared_subcommands
```

Creates `myapp/dev/cli/shared_subcommands.py` with only the docstring.

### InitConfigFile

Creates `__init__.py` files with docstrings:

```python
from types import ModuleType
from pyrig.dev.configs.base.init import InitConfigFile
from pyrig.dev import configs

class ConfigsInitConfigFile(InitConfigFile):
    @classmethod
    def get_src_module(cls) -> ModuleType:
        return configs
```

Creates `myapp/dev/configs/__init__.py` with the docstring from `pyrig.dev.configs`.

## Filename Derivation

Filenames are automatically derived from class names:

| Class Name | Filename |
|------------|----------|
| `MyConfigFile` | `my_config` |
| `PyprojectConfigFile` | `pyproject` |
| `DotEnvConfigFile` | `dot_env` |
| `GitIgnoreConfigFile` | `git_ignore` |

The system:
1. Removes abstract parent class suffixes (`ConfigFile`, `YamlConfigFile`, etc.)
2. Converts to snake_case
3. Adds the file extension

Override `get_filename()` for custom names:

```python
@classmethod
def get_filename(cls) -> str:
    return ""  # Creates ".env" instead of "dot_env.env"
```

## Opt-Out Mechanism

Users can opt out of any config file by emptying it. An empty file is considered "unwanted" and validation passes. There are few exceptions, e.g. README.md is considered always wanted. However you can override `is_unwanted` to change this behavior.

Note: Deleting a file will juts lead to it being recreated. Emptying it is the only way to opt out.

## Custom Validation

Override `is_correct()` for custom validation logic, pyrig does this in many of its own config files:

```python
@classmethod
def is_correct(cls) -> bool:
    """Check if config contains required structure."""
    content = cls.get_file_content()
    return super().is_correct() or (
        "required_string" in content
        and "another_required_string" in content
    )
```

## Best Practices

1. **Inherit from format-specific classes** - Use `YamlConfigFile`, `TomlConfigFile`, etc.
2. **Keep configs minimal** - Only specify required values
3. **Allow user customization** - Validation checks for supersets, not exact matches
4. **Use priority/ordered lists** - For configs with dependencies
5. **Override `is_correct()` carefully** - Ensure it allows user additions
6. **Document expected structure** - In docstrings and comments

## Example: Complete Custom Config

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.yaml import YamlConfigFile

class DatabaseConfigFile(YamlConfigFile):
    """Configuration for database connection settings."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Place in config/ directory."""
        return Path("config")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Required database configuration."""
        return {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp_db"
            }
        }

    @classmethod
    def is_correct(cls) -> bool:
        """Ensure required keys exist."""
        config = cls.load()
        required_keys = {"host", "port", "name"}
        actual_keys = set(config.get("database", {}).keys())
        return super().is_correct() or required_keys.issubset(actual_keys)
```

Place in `myapp/dev/configs/database.py` and it will create `config/database.yaml` with the required structure.

