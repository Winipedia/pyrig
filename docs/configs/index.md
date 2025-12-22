# Configuration Files Documentation

pyrig's configuration system automatically creates and maintains project configuration files through a declarative class-based architecture.

## Documentation Pages

### [Architecture](architecture.md)
Learn how the ConfigFile system works, including automatic discovery, validation, and how to create custom configuration files.

## Configuration Files

### [branch-protection.json](branch_protection.md)
Branch protection ruleset configuration for GitHub repository protection.

### [builders/__init__.py](builders_init.md)
Package initialization file for the builders directory structure.

### [configs/__init__.py](configs_init.md)
Package initialization file for the configs directory structure.

### [conftest.py](conftest.md)
Pytest configuration file that imports pyrig's test fixtures and plugins.

### [Containerfile](container_file.md)
Container image configuration for building production-ready images with Podman or Docker.

### [.env](dot_env.md)
Environment variables file for local configuration, automatically excluded from version control.

### [.experiment.py](dot_experiment.md)
Scratch file for local experimentation, automatically excluded from version control.

### [.python-version](dot_python_version.md)
Python version specification file for pyenv and other version managers.

### [fixtures/__init__.py](fixtures_init.md)
Package initialization file for the test fixtures directory structure.

### [GitIgnore](gitignore.md)
Git ignore patterns for excluding files from version control.

### [Index.md](index_md.md)
Documentation homepage file for MkDocs sites with badges and project description.

### [LICENSE](license_md.md)
Project license file, defaults to MIT License with automatic year and owner.

### [main.py](main.md)
CLI entry point file that provides the command-line interface for your application.

### [MkDocs](mkdocs.md)
Documentation site configuration for generating websites with MkDocs.

### [Pre-Commit](pre_commit.md)
Pre-commit hooks configuration for automated code quality checks before commits.

### [py.typed](py_typed.md)
PEP 561 marker file indicating the package supports type checking.

### [pyproject.toml](pyproject.md)
Central project configuration file for Python packaging, dependencies, and tool settings.

### [README.md](readme_md.md)
Repository homepage file with badges and project description for GitHub.

### [resources/__init__.py](resources_init.md)
Package initialization file for the resources directory structure.

### [shared_subcommands.py](shared_subcommands.md)
CLI shared subcommands file for defining reusable commands across all pyrig projects.

### [src/__init__.py](src_init.md)
Package initialization file for the src directory structure.

### [subcommands.py](subcommands.md)
CLI subcommands file for defining project-specific custom commands.

### [test_main.py](test_main.md)
Test file for the CLI entry point (main.py).

### [test_zero.py](test_zero.md)
Placeholder test file that ensures pytest runs when no other tests exist.

### [Workflows](workflows/index.md)
GitHub Actions workflow configuration files for CI/CD automation.

## Quick Overview

The configuration system provides:
- **Automatic discovery** of config files across all packages depending on pyrig
- **Intelligent validation** ensuring configs are supersets of required values
- **Smart merging** of missing configuration without overwriting user changes
- **Multi-format support** for YAML, TOML, Python, Markdown, and plain text
- **Opt-out mechanism** via empty files

## Quick Start

### Using Existing Config Files

When you run `uv run pyrig mkroot`, all ConfigFile subclasses are discovered and initialized:

```bash
# Create all config files
uv run pyrig mkroot

# Create only priority config files (useful during initial setup)
uv run pyrig mkroot --priority
```

This creates:
- `pyproject.toml` - Project metadata and tool configurations
- `.gitignore` - Git ignore patterns
- `LICENSE` - Project license
- `README.md` - Project documentation
- `main.py` - CLI entry point
- And many more...

The `--priority` flag creates only essential config files needed before installing dependencies (pyproject.toml, .gitignore, LICENSE, main.py, and package __init__.py files).

### Creating a Custom Config File

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.yaml import YamlConfigFile

class MyConfigFile(YamlConfigFile):
    @classmethod
    def get_parent_path(cls) -> Path:
        """Directory containing the config file."""
        return Path(".")

    @classmethod
    def get_configs(cls) -> dict[str, Any]:
        """Expected configuration structure."""
        return {
            "app": {
                "name": "myapp",
                "version": "1.0.0"
            }
        }
```

Place this in `myapp/dev/configs/my_config.py` and it will be automatically discovered and initialized.

## Why Use ConfigFile?

The ConfigFile system solves several problems:
- **Consistency** across all pyrig projects
- **Automatic updates** when pyrig adds new required configurations
- **User customization** without breaking required structure
- **Multi-package inheritance** of configurations
- **Validation** ensuring configs remain correct

