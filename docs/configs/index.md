# Configuration Files Documentation

pyrig's configuration system automatically creates and maintains project configuration files through a declarative class-based architecture.

## Documentation Pages

### [Architecture](architecture.md)
Learn how the ConfigFile system works, including automatic discovery, validation, and how to create custom configuration files.

## Quick Overview

The configuration system provides:
- **Automatic discovery** of config files across all packages depending on pyrig
- **Intelligent validation** ensuring configs are supersets of required values
- **Smart merging** of missing configuration without overwriting user changes
- **Multi-format support** for YAML, TOML, Python, Markdown, and plain text
- **Opt-out mechanism** via empty files

## Quick Start

### Using Existing Config Files

When you run `uv run myapp mkroot`, all ConfigFile subclasses are discovered and initialized:

```bash
uv run myapp mkroot
```

This creates:
- `pyproject.toml` - Project metadata and tool configurations
- `.gitignore` - Git ignore patterns
- `LICENSE` - Project license
- `README.md` - Project documentation
- `main.py` - CLI entry point
- And many more...

### Creating a Custom Config File

```python
from pathlib import Path
from typing import Any
from pyrig.dev.configs.base.base import YamlConfigFile

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

