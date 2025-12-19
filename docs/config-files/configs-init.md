# ConfigsInitConfigFile

## Overview

**File Location:** `{package_name}/dev/configs/__init__.py`
**ConfigFile Class:** `ConfigsInitConfigFile`
**File Type:** Python
**Priority:** Standard

Creates the `configs` package within your project's `dev` directory. This package is where you define custom ConfigFile classes to manage your project's configuration files.

## Purpose

The `{package_name}/dev/configs/__init__.py` file establishes the configs package:

- **Package Marker** - Makes `configs` a valid Python package
- **ConfigFile Organization** - Provides a place for custom ConfigFile classes
- **Pyrig Mirroring** - Mirrors pyrig's `dev.configs` package structure
- **Automatic Discovery** - ConfigFiles in this package are automatically discovered
- **Extensibility** - Allows you to create project-specific config management

### Why pyrig manages this file

pyrig creates `dev/configs/__init__.py` to:
1. **Consistent structure** - All pyrig projects have a `configs` package
2. **ConfigFile discovery** - Pyrig automatically finds ConfigFile subclasses here
3. **Customization point** - You can add custom config file managers
4. **Documentation** - Docstring explains the package's purpose
5. **Package discovery** - Ensures Python recognizes `configs` as a package

The file is created during `pyrig init` with only the docstring from pyrig's `dev.configs` package.

## File Location

The file is placed in your package's `dev/configs` directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── configs/
│           └── __init__.py  # <-- Here
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── configs/
│           └── __init__.py  # <-- Mirrored from here
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `dev.configs.__init__`:

```python
"""__init__ module."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.dev.configs.__init__`
- **Required:** Yes (minimal package marker)
- **Purpose:** Documents the package
- **Why pyrig sets it:** Provides context for the package

**Why only the docstring:**
- **Minimal** - Doesn't impose implementation
- **Flexible** - You can add your own config files
- **Documentation** - Preserves pyrig's documentation
- **Package marker** - Makes directory a valid package

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/dev/configs/__init__.py`

**File contents:**
```python
"""__init__ module."""
```

## What Are ConfigFiles?

ConfigFiles are classes that manage configuration files. They extend the `ConfigFile` base class and are automatically discovered by pyrig.

### ConfigFile Base Class

```python
from pyrig.dev.configs.base.base import YamlConfigFile
from pathlib import Path

class MyConfigFile(YamlConfigFile):
    """My custom config file."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the directory for the config file."""
        return Path(".")

    @classmethod
    def get_configs(cls) -> dict:
        """Get the expected configuration."""
        return {"key": "value"}
```

### Automatic Discovery

Pyrig automatically discovers all ConfigFile subclasses in:
- `{package_name}/dev/configs/`
- Any package that depends on pyrig

This means you can create config files and they'll be automatically managed.

## Creating Custom ConfigFiles

### Example: Application Config

```python
# my_awesome_project/dev/configs/app_config.py
"""Application configuration file."""

from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile


class AppConfigFile(YamlConfigFile):
    """Manages app.yaml configuration."""

    @classmethod
    def get_parent_path(cls) -> Path:
        """Get the config directory."""
        return Path("config")

    @classmethod
    def get_filename(cls) -> str:
        """Get the filename."""
        return "app"

    @classmethod
    def get_configs(cls) -> dict:
        """Get the default configuration."""
        return {
            "app_name": "my-awesome-project",
            "version": "1.0.0",
            "debug": False,
            "database": {
                "host": "localhost",
                "port": 5432,
            },
        }
```

This creates `config/app.yaml`:

```yaml
app_name: my-awesome-project
version: 1.0.0
debug: false
database:
  host: localhost
  port: 5432
```

### Example: Custom pyproject.toml Extension

```python
# my_awesome_project/dev/configs/custom_pyproject.py
"""Custom pyproject.toml configuration."""

from pyrig.dev.configs.pyproject import PyprojectConfigFile


class CustomPyprojectConfigFile(PyprojectConfigFile):
    """Extends pyproject.toml with custom settings."""

    @classmethod
    def get_configs(cls) -> dict:
        """Get configuration with custom additions."""
        config = super().get_configs()

        # Add custom tool configuration
        config["tool"]["myapp"] = {
            "setting1": "value1",
            "setting2": "value2",
        }

        return config
```

### Example: Environment-Specific Config

```python
# my_awesome_project/dev/configs/environments.py
"""Environment-specific configuration files."""

from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile


class DevelopmentConfigFile(YamlConfigFile):
    """Development environment configuration."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config/environments")

    @classmethod
    def get_filename(cls) -> str:
        return "development"

    @classmethod
    def get_configs(cls) -> dict:
        return {
            "environment": "development",
            "debug": True,
            "log_level": "DEBUG",
        }


class ProductionConfigFile(YamlConfigFile):
    """Production environment configuration."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config/environments")

    @classmethod
    def get_filename(cls) -> str:
        return "production"

    @classmethod
    def get_configs(cls) -> dict:
        return {
            "environment": "production",
            "debug": False,
            "log_level": "WARNING",
        }
```

## Subclassing Pyrig's ConfigFiles

You can extend pyrig's existing ConfigFile classes:

### Example: Custom Pre-commit Hooks

```python
# my_awesome_project/dev/configs/custom_precommit.py
"""Custom pre-commit configuration."""

from pyrig.dev.configs.git.pre_commit_config import PreCommitConfigFile


class CustomPreCommitConfigFile(PreCommitConfigFile):
    """Extends pre-commit with additional hooks."""

    @classmethod
    def get_configs(cls) -> dict:
        """Get configuration with custom hooks."""
        config = super().get_configs()

        # Add custom hook
        config["repos"].append({
            "repo": "https://github.com/pre-commit/mirrors-eslint",
            "rev": "v8.0.0",
            "hooks": [{
                "id": "eslint",
                "files": r"\.(js|jsx|ts|tsx)$",
            }],
        })

        return config
```

## Running ConfigFile Management

### Using pyrig CLI

```bash
# Initialize all config files
uv run pyrig init

# Recreate root config files
uv run pyrig mkroot
```

### Programmatically

```python
from my_awesome_project.dev.configs.app_config import AppConfigFile

# Initialize the config file
AppConfigFile().init()

# Check if it's correct
if not AppConfigFile.is_correct():
    print("Config file needs updating")
```

## Customization

You can add imports or utilities to the `__init__.py`:

### Example: Export ConfigFiles

```python
# my_awesome_project/dev/configs/__init__.py
"""__init__ module."""

from my_awesome_project.dev.configs.app_config import AppConfigFile
from my_awesome_project.dev.configs.custom_pyproject import CustomPyprojectConfigFile

__all__ = ["AppConfigFile", "CustomPyprojectConfigFile"]
```

### Example: Shared Utilities

```python
# my_awesome_project/dev/configs/__init__.py
"""__init__ module."""

from pathlib import Path


def get_config_dir() -> Path:
    """Get the configuration directory."""
    return Path("config")


def ensure_config_dir() -> None:
    """Ensure the configuration directory exists."""
    get_config_dir().mkdir(parents=True, exist_ok=True)
```

## Related Files

- **`{package_name}/dev/__init__.py`** - Dev package init (created by pyrig)
- **`{package_name}/dev/builders/__init__.py`** - Builders package init ([builders-init.md](builders-init.md))
- **`{package_name}/dev/resources/__init__.py`** - Resources package init ([resources-init.md](resources-init.md))
- **`pyproject.toml`** - Main configuration file ([pyproject.md](pyproject.md))

## Common Issues

### Issue: ConfigFile not discovered

**Symptom:** Custom config file not managed by pyrig

**Cause:** ConfigFile not in the configs package or not a ConfigFile subclass

**Solution:**
```python
# Ensure your config file:
# 1. Is in my_awesome_project/dev/configs/
# 2. Extends a ConfigFile base class
# 3. Implements required methods

from pyrig.dev.configs.base.base import YamlConfigFile
from pathlib import Path

class MyConfigFile(YamlConfigFile):
    """My config file."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path(".")

    @classmethod
    def get_configs(cls) -> dict:
        return {"key": "value"}
```

### Issue: Config file not created

**Symptom:** Running `pyrig init` doesn't create my config file

**Cause:** ConfigFile class not properly defined or discovered

**Solution:**
```bash
# Check that the file exists
ls my_awesome_project/dev/configs/my_config.py

# Check that it's a valid ConfigFile subclass
uv run python -c "from my_awesome_project.dev.configs.my_config import MyConfigFile; print(MyConfigFile)"

# Run init again
uv run pyrig init
```

### Issue: Want to organize configs in subpackages

**Symptom:** Too many config files in one directory

**Cause:** Flat structure doesn't scale

**Solution:**
```bash
# Create subpackages
mkdir my_awesome_project/dev/configs/app
mkdir my_awesome_project/dev/configs/database
mkdir my_awesome_project/dev/configs/api

# Add __init__.py to each
touch my_awesome_project/dev/configs/app/__init__.py
touch my_awesome_project/dev/configs/database/__init__.py
touch my_awesome_project/dev/configs/api/__init__.py
```

## Best Practices

### ✅ DO

- **Use appropriate base classes** - YamlConfigFile, TomlConfigFile, etc.
- **Implement required methods** - get_parent_path(), get_configs()
- **Use subset validation** - Allow user customization
- **Document config options** - Add docstrings explaining settings
- **Test config files** - Ensure they generate correctly

### ❌ DON'T

- **Don't remove the docstring** - Pyrig expects it
- **Don't hardcode values** - Use configuration
- **Don't make configs stateful** - Keep them simple
- **Don't create circular dependencies** - Keep configs independent
- **Don't override user changes** - Use subset validation

## Advanced Usage

### ConfigFile with Validation

```python
# my_awesome_project/dev/configs/validated_config.py
"""Config file with validation."""

from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile


class ValidatedConfigFile(YamlConfigFile):
    """Config file with custom validation."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_filename(cls) -> str:
        return "validated"

    @classmethod
    def get_configs(cls) -> dict:
        return {
            "port": 8080,
            "host": "localhost",
        }

    @classmethod
    def is_correct(cls) -> bool:
        """Validate configuration."""
        if not super().is_correct():
            return False

        # Custom validation
        config = cls.load()
        port = config.get("port", 0)
        return 1024 <= port <= 65535
```

### ConfigFile with Dynamic Content

```python
# my_awesome_project/dev/configs/dynamic_config.py
"""Config file with dynamic content."""

from pathlib import Path
from datetime import datetime
from pyrig.dev.configs.base.base import YamlConfigFile


class DynamicConfigFile(YamlConfigFile):
    """Config file with dynamic content."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_filename(cls) -> str:
        return "dynamic"

    @classmethod
    def get_configs(cls) -> dict:
        """Get configuration with dynamic values."""
        return {
            "generated_at": datetime.now().isoformat(),
            "version": cls._get_version(),
        }

    @classmethod
    def _get_version(cls) -> str:
        """Get version from pyproject.toml."""
        from pyrig.dev.configs.pyproject import PyprojectConfigFile
        return PyprojectConfigFile.get_version()
```

### ConfigFile with Environment Variables

```python
# my_awesome_project/dev/configs/env_config.py
"""Config file using environment variables."""

import os
from pathlib import Path
from pyrig.dev.configs.base.base import YamlConfigFile


class EnvConfigFile(YamlConfigFile):
    """Config file that uses environment variables."""

    @classmethod
    def get_parent_path(cls) -> Path:
        return Path("config")

    @classmethod
    def get_filename(cls) -> str:
        return "env"

    @classmethod
    def get_configs(cls) -> dict:
        """Get configuration from environment."""
        return {
            "database_url": os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"),
            "secret_key": os.getenv("SECRET_KEY", "dev-secret-key"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
        }
```

## See Also

- [ConfigFile System](../configfile-system.md) - ConfigFile system documentation
- [pyproject.toml](pyproject.md) - Main configuration file
- [builders/__init__.py](builders-init.md) - Builders package init
- [resources/__init__.py](resources-init.md) - Resources package init
- [Getting Started Guide](../getting-started.md) - Initial project setup


