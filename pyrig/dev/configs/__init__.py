"""Configuration file management system for pyrig projects.

This package provides the ConfigFile system, which is the core of pyrig's
project automation. It automatically discovers, creates, validates, and updates
all configuration files needed for a complete Python project.

The ConfigFile system is declarative and extensible: you define what config
files should exist and what they should contain, and the system ensures they
match that specification. User customizations are preserved through subset
validation - the system only adds missing values, never removes or modifies
existing ones unless you manually change a value whose default is defined differently.
If you want to do that, you will have to subclass the ConfigFile and override the
`get_configs()` method to change the default value.

Architecture:
    The system uses automatic subclass discovery to find all ConfigFile
    implementations across all packages that depend on pyrig. When initialized,
    ConfigFiles are processed in priority order (higher priority first), with
    files at the same priority level initialized in parallel for performance.

    Each ConfigFile subclass:
    - Defines its location via `get_parent_path()` and `get_file_extension()`
    - Specifies expected content via `get_configs()`
    - Implements format-specific loading/dumping via `load()` and `dump()`
    - Optionally sets initialization priority via `get_priority()`

Features:
    - **Automatic Discovery**: Finds all ConfigFile subclasses across packages
    - **Subset Validation**: User configs can extend but not contradict base
    - **Intelligent Merging**: Only missing values are added, existing preserved
    - **Multiple Formats**: YAML, TOML, JSON, Python, Markdown, plain text
    - **Priority-Based Init**: Control initialization order when dependencies exist
    - **Parallel Execution**: Same-priority files initialized concurrently
    - **Idempotent**: Safe to run multiple times, no duplicate additions
    - **Opt-Out Support**: Empty files signal user doesn't want that config

Key Components:
    Base Classes:
        - `base.base.ConfigFile`: Abstract base for all config files
        - `base.toml.TomlConfigFile`: Base for TOML files
        - `base.yaml.YamlConfigFile`: Base for YAML files
        - `base.python.PythonConfigFile`: Base for Python files
        - `base.markdown.MarkdownConfigFile`: Base for Markdown files

    Core Config Files:
        - `pyproject.PyprojectConfigFile`: Manages pyproject.toml
        - `git.gitignore.GitIgnoreConfigFile`: Manages .gitignore
        - `git.pre_commit.PreCommitConfigFile`: Manages .pre-commit-config.yaml
        - `docs.mkdocs.MkDocsConfigFile`: Manages mkdocs.yml
        - `workflows.*`: GitHub Actions workflow configurations

How It Works:
    1. User runs `pyrig mkroot` (or `ConfigFile.init_all_subclasses()`)
    2. System discovers all ConfigFile subclasses via `get_all_subclasses()`
    3. Subclasses are grouped by priority and sorted (highest first)
    4. Each priority group is initialized in parallel via ThreadPoolExecutor
    5. For each ConfigFile:
       a. Parent directories are created if needed
       b. File is created with default content if it doesn't exist
       c. Existing content is validated via `is_correct()`
       d. Missing values are added via `add_missing_configs()`
       e. Final validation ensures file is correct or raises ValueError

Subset Validation:
    The system uses `nested_structure_is_subset()` to validate that expected
    configuration is present in actual configuration. This allows users to:
    - Add extra configuration keys
    - Extend lists with additional items
    - Override values (as long as required structure exists)

    A file is considered "correct" if:
    - It's empty (user opted out), OR
    - Expected config is a subset of actual config

Example:
    Create a custom config file::

        from pathlib import Path
        from typing import Any
        from pyrig.dev.configs.base.toml import TomlConfigFile

        class MyConfigFile(TomlConfigFile):
            '''Custom TOML configuration for myapp.'''

            @classmethod
            def get_parent_path(cls) -> Path:
                '''Place file in project root.'''
                return Path()

            @classmethod
            def get_configs(cls) -> dict[str, Any]:
                '''Define expected configuration structure.'''
                return {
                    "tool": {
                        "myapp": {
                            "setting": "default_value",
                            "enabled": True
                        }
                    }
                }

            @classmethod
            def get_priority(cls) -> float:
                '''Initialize after pyproject.toml (priority 100).'''
                return 50

    Then run::

        uv run myapp mkroot

    The system will:
    - Create myconfig.toml if it doesn't exist
    - Add missing keys if file exists but incomplete
    - Preserve any extra keys user added
    - Validate final result matches expected structure

See Also:
    pyrig.dev.configs.base.base.ConfigFile: Base class and core logic
    pyrig.dev.cli.commands.create_root.make_project_root: CLI command
    pyrig.src.iterate.nested_structure_is_subset: Subset validation logic
    pyrig.src.modules.class_.get_all_nonabstract_subclasses: Discovery mechanism
"""
