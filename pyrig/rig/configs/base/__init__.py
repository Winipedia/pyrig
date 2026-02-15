"""Base classes for configuration file management.

Provides foundational infrastructure for the ConfigFile system: abstract base class
and format-specific subclasses for managing project configuration files.

Architecture:
    Four layers:

    1. **Core**: ``ConfigFile`` (base.py) - Abstract base defining config lifecycle

    2. **Type-Specific**:
       - ``DictConfigFile``: dict-based configurations
       - ``ListConfigFile``: list-based configurations

    3. **Format-Specific**:
       - ``TomlConfigFile``: TOML files (pyproject.toml)
       - ``YamlConfigFile`` / ``YmlConfigFile``: YAML files
       - ``JsonConfigFile``: JSON files (package.json)
       - ``StringConfigFile``: Plain text with required content
       - ``PythonConfigFile``: Python source (.py)
       - ``MarkdownConfigFile``: Markdown (.md)
       - ``TypedConfigFile``: PEP 561 marker (py.typed)

    4. **Specialized**:
       - ``PythonPackageConfigFile``: Package files (__init__.py)
       - ``PythonTestsConfigFile``: Test files in tests/
       - ``CopyModuleConfigFile``: Replicate module content
       - ``CopyModuleOnlyDocstringConfigFile``: Copy only docstrings
       - ``InitConfigFile``: __init__.py with copied docstrings
       - ``BadgesMarkdownConfigFile``: Markdown with project badges
       - ``WorkflowConfigFile``: GitHub Actions workflow files

Format Features:
    - **TOML**: tomlkit for format-preserving parsing, multiline arrays, inline tables
    - **YAML**: PyYAML safe_load/dump, prevents code execution, preserves order
    - **JSON**: Built-in json module, 4-space indentation
    - **Text**: Content-based validation, appends user additions
    - **Python**: Extends StringConfigFile with .py extension
    - **Markdown**: Extends StringConfigFile with .md extension

Specialized Classes:
    - **PythonPackageConfigFile**: Ensures parent is valid package, creates __init__.py
    - **PythonTestsConfigFile**: Auto-places files in tests/
    - **CopyModuleConfigFile**: Replicates module structure, transforms paths
    - **CopyModuleOnlyDocstringConfigFile**: Extracts docstrings, creates stubs
    - **InitConfigFile**: Creates __init__.py with copied docstrings
    - **BadgesMarkdownConfigFile**: Generates Markdown with badges from pyproject.toml
    - **WorkflowConfigFileConfigFile**: Base class for GitHub Actions workflow configs

Example:
    Using format-specific base classes::

        from pathlib import Path
        from typing import Any
        from pyrig.rig.configs.base.toml import TomlConfigFile

        class MyConfigFile(TomlConfigFile):
            '''Manages myconfig.toml.'''


            def parent_path(self) -> Path:
                return Path()


            def _configs(self) -> dict[str, Any]:
                return {"setting": "value"}

    Using specialized base classes::

        from types import ModuleType
        from pyrig.rig.configs.base.copy_module import CopyModuleConfigFile
        import pyrig.src.string_

        class StringModuleCopy(CopyModuleConfigFile):
            '''Copy pyrig.src.string_ to the target project.'''


            def src_module(self) -> ModuleType:
                return pyrig.src.string_

See Also:
    pyrig.rig.configs: Package-level documentation
    pyrig.rig.configs.base.base: Core ConfigFile base class
"""
