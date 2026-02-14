# Configuration Files Documentation

pyrig's configuration system automatically creates and maintains project
configuration files through a declarative class-based architecture.

## Documentation Pages

### [Architecture](architecture.md)

Learn how the ConfigFile system works, including automatic discovery,
validation, and creating custom configuration files.

## Configuration Files

### [branch-protection.json](branch_protection.md)

Branch protection ruleset configuration for GitHub repository protection.

### [builders/\_\_init\_\_.py](builders_init.md)

Package initialization file for the builders directory structure.

### [configs/\_\_init\_\_.py](configs_init.md)

Package initialization file for the configs directory structure.

### [CODE_OF_CONDUCT.md](code_of_conduct.md)

Community standards file using the Contributor Covenant for welcoming
collaboration.

### [CONTRIBUTING.md](contributing.md)

Contribution guidelines file with best practices for issues and pull requests.

### [pull_request_template.md](pull_request_template.md)

Pull request template for GitHub with Summary and Test Plan sections.

### [conftest.py](conftest.md)

Pytest configuration file that imports pyrig's test fixtures and plugins.

### [Containerfile](container_file.md)

Container image configuration for building production-ready images with Podman
or Docker.

### [.env](dot_env.md)

Environment variables file for local configuration, automatically excluded from
version control.

### [.scratch.py](dot_scratch.md)

Scratch file for local experimentation, automatically excluded from version
control.

### [.python-version](dot_python_version.md)

Python version specification file for pyenv and other version managers.

### [api.md](api_md.md)

API reference documentation page generated from Python docstrings using
mkdocstrings.

### [fixtures/\_\_init\_\_.py](fixtures_init.md)

Package initialization file for the test fixtures directory structure.

### [GitIgnore](gitignore.md)

Git ignore patterns for excluding files from version control.

### [Issue Templates](issue_templates/index.md)

GitHub issue templates for bug reports and feature requests in
`.github/ISSUE_TEMPLATE/`.

### [Index.md](index_md.md)

Documentation homepage file for MkDocs sites with badges and project
description.

### [LICENSE](license_md.md)

Project license file, defaults to MIT License with automatic year and owner.

### [main.py](main.md)

CLI entry point file that provides the command-line interface for your
application.

### [MkDocs](mkdocs.md)

Documentation site configuration for generating websites with MkDocs.

### [Prek](pre_commit.md)

Prek hooks configuration for automated code quality checks before commits.

### [py.typed](py_typed.md)

PEP 561 marker file indicating the package supports type checking.

### [pyproject.toml](pyproject.md)

Central project configuration file for Python packaging, dependencies, and tool
settings.

### [README.md](readme_md.md)

Repository homepage file with badges and project description for GitHub.

### [resources/\_\_init\_\_.py](resources_init.md)

Package initialization file for the resources directory structure.

### [SECURITY.md](security.md)

Security policy file with vulnerability reporting guidelines.

### [shared_subcommands.py](shared_subcommands.md)

CLI shared subcommands file for defining reusable commands across all pyrig
projects.

### [src/\_\_init\_\_.py](src_init.md)

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
- **Multi-format support** for YAML, TOML, Python, Markdown, JSON, and plain
  text
- **Priority-based validation** for dependency ordering
- **Parallel validation** for performance
- **Opt-out mechanism** via empty files

See [Architecture](architecture.md) for complete technical details on how the
system works.

## Quick Start

### Using Existing Config Files

```bash
# Create all config files
uv run pyrig mkroot

# Create only priority config files (useful during initial setup)
uv run pyrig mkroot --priority
```

The `--priority` flag creates only essential files needed before installing
dependencies (LICENSE, pyproject.toml, `__init__.py` files).

### Creating a Custom Config File

```python
from pathlib import Path
from typing import Any
from pyrig.rig.configs.base.yaml import YamlConfigFile

class MyConfigFile(YamlConfigFile):
    @classmethod
    def parent_path(cls) -> Path:
        """Directory containing the config file."""
        return Path("config")

    @classmethod
    def _configs(cls) -> dict[str, Any]:
        """Expected configuration structure."""
        return {
            "app": {
                "name": "myapp",
                "version": "1.0.0"
            }
        }
```

Place this in `myapp/rig/configs/my_config.py` and it will be automatically
discovered and create `config/my_config.yaml`.

See [Architecture](architecture.md) for:

- Setting priority for validation order
- Format-specific subclasses (YAML, TOML, JSON, etc.)
- Custom validation logic
- Filename derivation rules
- Best practices
