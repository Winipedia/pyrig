"""Base classes for configuration file management.

Provides foundational infrastructure for the ConfigFile system: abstract base class
and format-specific subclasses for managing project configuration files.

Architecture
------------

Three layers:

1. **Core**: ``ConfigFile`` (base.py) - Abstract base defining config lifecycle

2. **Format-Specific**:
   - ``TomlConfigFile``: TOML files (pyproject.toml)
   - ``YamlConfigFile`` / ``YmlConfigFile``: YAML files (.pre-commit-config.yaml)
   - ``JsonConfigFile``: JSON files (package.json)
   - ``StringConfigFile``: Plain text with required content
   - ``PythonConfigFile``: Python source (.py)
   - ``MarkdownConfigFile``: Markdown (.md)
   - ``TxtConfigFile``: Text files (.txt)
   - ``TypedConfigFile``: PEP 561 marker (py.typed)

3. **Specialized**:
   - ``PythonPackageConfigFile``: Package files (__init__.py)
   - ``PythonTestsConfigFile``: Test files in tests/
   - ``CopyModuleConfigFile``: Replicate module content
   - ``CopyModuleOnlyDocstringConfigFile``: Copy only docstrings
   - ``InitConfigFile``: __init__.py with copied docstrings
   - ``BadgesMarkdownConfigFile``: Markdown with project badges
   - ``MirrorTestConfigFile``: Test files mirroring source module structure

Format Features
---------------

- **TOML**: tomlkit for format-preserving parsing, multiline arrays, inline tables
- **YAML**: PyYAML safe_load/dump, prevents code execution, preserves order
- **JSON**: Built-in json module, 4-space indentation
- **Text**: Content-based validation, appends user additions
- **Python**: Extends TextConfigFile with .py extension
- **Markdown**: Extends TextConfigFile with .md extension

Specialized Classes
-------------------

- **PythonPackageConfigFile**: Ensures parent is valid package, creates __init__.py
- **PythonTestsConfigFile**: Auto-places files in tests/
- **CopyModuleConfigFile**: Replicates module structure, transforms paths
- **CopyModuleOnlyDocstringConfigFile**: Extracts docstrings, creates stubs
- **InitConfigFile**: Creates __init__.py with copied docstrings
- **BadgesMarkdownConfigFile**: Generates Markdown with badges from pyproject.toml
- **MirrorTestConfigFile**: Creates test files mirroring source module structure

Usage Examples
--------------

Using format-specific base classes::

    from pathlib import Path
    from typing import Any
    from pyrig.dev.configs.base.toml import TomlConfigFile

    class MyConfigFile(TomlConfigFile):
        '''Manages myconfig.toml.'''

        @classmethod
        def get_parent_path(cls) -> Path:
            return Path()

        @classmethod
        def _get_configs(cls) -> dict[str, Any]:
            return {"setting": "value"}

Using specialized base classes::

    from types import ModuleType
    from pyrig.dev.configs.base.copy_module import CopyModuleConfigFile
    import my_module

    class MyModuleCopy(CopyModuleConfigFile):
        '''Copies my_module to the target project.'''

        @classmethod
        def get_src_module(cls) -> ModuleType:
            return my_module

See Also:
--------
pyrig.dev.configs: Package-level documentation
pyrig.dev.configs.base.base: Core ConfigFile base class
"""
