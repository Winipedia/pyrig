"""Base classes for configuration file management.

This package provides the foundational infrastructure for the ConfigFile system,
including the abstract ``ConfigFile`` base class and format-specific subclasses
for managing project configuration files.

Architecture
------------

The base package is organized into three layers:

1. **Core Base Class** (``base.py``):
   - ``ConfigFile``: Abstract base class defining the configuration lifecycle

2. **Format-Specific Base Classes**:
   - ``TomlConfigFile``: TOML files (pyproject.toml, etc.)
   - ``YamlConfigFile`` / ``YmlConfigFile``: YAML files (.pre-commit-config.yaml, etc.)
   - ``JsonConfigFile``: JSON files (package.json, etc.)
   - ``TextConfigFile``: Plain text files with required content
   - ``PythonConfigFile``: Python source files (.py)
   - ``MarkdownConfigFile``: Markdown files (README.md, etc.)
   - ``TxtConfigFile``: Text files (.txt)
   - ``TypedConfigFile``: PEP 561 marker files (py.typed)

3. **Specialized Base Classes**:
   - ``PythonPackageConfigFile``: Python package files (__init__.py)
   - ``PythonTestsConfigFile``: Python test files in tests/
   - ``CopyModuleConfigFile``: Files that replicate module content
   - ``CopyModuleOnlyDocstringConfigFile``: Files that copy only docstrings
   - ``InitConfigFile``: __init__.py files with copied docstrings
   - ``BadgesMarkdownConfigFile``: Markdown files with project badges

Format-Specific Features
-------------------------

Each format-specific base class provides:

- **TOML** (``toml.py``):
  - Uses tomlkit for format-preserving parsing
  - Multiline arrays for readability
  - Inline tables for lists of dicts
  - Preserves comments and formatting

- **YAML** (``yaml.py``, ``yml.py``):
  - Uses PyYAML's safe_load/safe_dump
  - Prevents arbitrary code execution
  - Preserves key order

- **JSON** (``json.py``):
  - Uses Python's built-in json module
  - 4-space indentation for readability

- **Text** (``text.py``):
  - Content-based validation (substring matching)
  - Preserves user additions by appending
  - Suitable for files with required headers

- **Python** (``python.py``):
  - Extends TextConfigFile
  - .py extension

- **Markdown** (``markdown.py``):
  - Extends TextConfigFile
  - .md extension

Specialized Classes
-------------------

- **PythonPackageConfigFile** (``py_package.py``):
  - Ensures parent directory is a valid Python package
  - Creates __init__.py files in parent directories

- **PythonTestsConfigFile** (``py_tests.py``):
  - Automatically places files in tests/ directory
  - Simplifies test file creation

- **CopyModuleConfigFile** (``copy_module.py``):
  - Replicates pyrig's internal module structure
  - Transforms module paths (pyrig -> target project)
  - Enables customization through subclassing

- **CopyModuleOnlyDocstringConfigFile** (``copy_module_docstr.py``):
  - Extracts only the docstring from source module
  - Creates stub files with documentation
  - Allows users to provide custom implementations

- **InitConfigFile** (``init.py``):
  - Creates __init__.py files with copied docstrings
  - Derives parent path from source module name

- **BadgesMarkdownConfigFile** (``badges_md.py``):
  - Generates Markdown with project badges
  - Reads project metadata from pyproject.toml
  - Creates CI/CD, quality, and package badges

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
        def get_configs(cls) -> dict[str, Any]:
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
