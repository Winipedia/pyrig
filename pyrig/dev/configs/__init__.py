"""Configuration file management system for pyrig projects.

This package provides the ConfigFile system, which is the core of pyrig's
automation. It automatically discovers, creates, validates, and updates all
configuration files needed for a complete Python project.

The configuration system supports:
- Automatic discovery of ConfigFile subclasses across all packages
- Subset validation (user configs can extend but not contradict base configs)
- Intelligent merging of missing configuration values
- Multiple file formats (YAML, TOML, JSON, Python, Markdown, plain text)
- Priority-based initialization order
- Idempotent operations (safe to run multiple times)

Key Components:
    - `base.base.ConfigFile`: Abstract base class for all config files
    - `pyproject.PyprojectConfigFile`: Manages pyproject.toml
    - `git.gitignore.GitIgnoreConfigFile`: Manages .gitignore
    - `git.pre_commit.PreCommitConfigFile`: Manages .pre-commit-config.yaml
    - `workflows.*`: GitHub Actions workflow configurations
    - `docs.mkdocs.MkDocsConfigFile`: Manages mkdocs.yml

How It Works:
    1. When you run `pyrig mkroot`, the ConfigFile system activates
    2. It discovers all ConfigFile subclasses across all packages depending on pyrig
    3. Each ConfigFile is initialized in priority order
    4. Files are created if missing, or updated if they don't match expected config
    5. User customizations are preserved - only missing values are added

Example:
    Create a custom config file::

        from pathlib import Path
        from typing import Any
        from pyrig.dev.configs.base.toml import TomlConfigFile

        class MyConfigFile(TomlConfigFile):
            @classmethod
            def get_parent_path(cls) -> Path:
                return Path()

            @classmethod
            def get_configs(cls) -> dict[str, Any]:
                return {
                    "tool": {
                        "myapp": {
                            "setting": "value"
                        }
                    }
                }

    Then run: `uv run myapp mkroot`

See Also:
    - `pyrig.dev.configs.base.base`: Base classes and core logic
    - `pyrig.dev.cli.commands.create_root`: Command that invokes the system
"""
