# SrcInitConfigFile

## Overview

**File Location:** `{package_name}/src/__init__.py`
**ConfigFile Class:** `SrcInitConfigFile`
**File Type:** Python
**Priority:** Standard

Creates the `src` package within your project, mirroring pyrig's internal `src` package structure. This package contains reusable utilities that your project can extend or customize.

## Purpose

The `{package_name}/src/__init__.py` file establishes the src package:

- **Package Marker** - Makes `src` a valid Python package
- **Utility Organization** - Provides a place for reusable utilities
- **Pyrig Mirroring** - Mirrors pyrig's `src` package structure
- **Extensibility** - Allows you to add custom utilities
- **Documentation** - Preserves pyrig's docstring for reference

### Why pyrig manages this file

pyrig creates `src/__init__.py` to:
1. **Consistent structure** - All pyrig projects have a `src` package
2. **Utility access** - Provides access to pyrig's utilities
3. **Customization point** - You can extend or override utilities
4. **Documentation** - Docstring explains the package's purpose
5. **Package discovery** - Ensures Python recognizes `src` as a package

The file is created during `pyrig init` with only the docstring from pyrig's `src` package.

## File Location

The file is placed in your package's `src` directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   └── src/
│       └── __init__.py  # <-- Here
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   └── src/
│       └── __init__.py  # <-- Mirrored from here
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `src/__init__.py`:

```python
"""src package."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.src.__init__`
- **Required:** Yes (minimal package marker)
- **Purpose:** Documents the package
- **Why pyrig sets it:** Provides context for the package

**Why only the docstring:**
- **Minimal** - Doesn't impose implementation
- **Flexible** - You can add your own code
- **Documentation** - Preserves pyrig's documentation
- **Package marker** - Makes directory a valid package

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/src/__init__.py`

**File contents:**
```python
"""src package."""
```

## The src Package Structure

While the `__init__.py` is minimal, you can add utilities to the `src` package:

```
my_awesome_project/
└── src/
    ├── __init__.py       # Minimal docstring
    ├── utils.py          # Your utilities
    ├── helpers.py        # Your helpers
    └── constants.py      # Your constants
```

### Pyrig's src Package

Pyrig's `src` package contains many utilities you can use:

```
pyrig/
└── src/
    ├── __init__.py
    ├── git/              # Git utilities
    ├── modules/          # Module introspection
    ├── os/               # OS utilities
    ├── project/          # Project management
    └── testing/          # Testing utilities
```

You can import these in your project:

```python
# In your code
from pyrig.src.modules.module import import_module_from_path
from pyrig.src.git.git import get_git_root
from pyrig.src.os.os import run_subprocess
```

## Customization

You can add your own utilities to the `src` package:

### Example: Add Utility Functions

```python
# my_awesome_project/src/__init__.py
"""src package."""

# Add your own utilities
def my_utility_function():
    """My custom utility."""
    return "useful"
```

### Example: Create Subpackages

```bash
# Create a utilities subpackage
mkdir my_awesome_project/src/utils
touch my_awesome_project/src/utils/__init__.py
```

```python
# my_awesome_project/src/utils/__init__.py
"""Utility functions for my-awesome-project."""

def format_data(data):
    """Format data for display."""
    return f"Formatted: {data}"
```

```python
# Use in your code
from my_awesome_project.src.utils import format_data

result = format_data("test")
```

### Example: Mirror Pyrig's Structure

```bash
# Create the same structure as pyrig
mkdir -p my_awesome_project/src/modules
mkdir -p my_awesome_project/src/git
mkdir -p my_awesome_project/src/os
```

```python
# my_awesome_project/src/modules/__init__.py
"""Module utilities specific to my-awesome-project."""

from pyrig.src.modules.module import import_module_from_path

# Add project-specific utilities
def import_project_module(name):
    """Import a module from this project."""
    return import_module_from_path(f"my_awesome_project.{name}")
```

## How It's Generated

### The InitConfigFile Base Class

`SrcInitConfigFile` extends `InitConfigFile`:

```python
class SrcInitConfigFile(InitConfigFile):
    """Configuration file manager for src/__init__.py."""

    @classmethod
    def get_src_module(cls) -> ModuleType:
        """Get the source module to mirror."""
        return src  # pyrig.src
```

### The Generation Process

1. **Get source module** - `pyrig.src`
2. **Extract docstring** - `"""src package."""`
3. **Determine target path** - `my_awesome_project/src/__init__.py`
4. **Write file** - Create with docstring only

### Why Only the Docstring

The `InitConfigFile` base class uses `CopyModuleOnlyDocstringConfigFile`:

```python
class CopyModuleOnlyDocstringConfigFile(CopyModuleConfigFile):
    """Config file that copies only the docstring from a module."""

    @classmethod
    def get_content_str(cls) -> str:
        """Extract only the docstring from the source module."""
        content = super().get_content_str()
        parts = content.split('"""', 2)
        return '"""' + parts[1] + '"""\n'
```

This ensures:
- **No code copied** - Only documentation
- **User freedom** - Add your own implementation
- **Package marker** - Valid Python package
- **Documentation** - Preserves context

## Related Files

- **`{package_name}/__init__.py`** - Main package init (created by pyrig)
- **`{package_name}/dev/__init__.py`** - Dev package init ([configs-init.md](configs-init.md))
- **`{package_name}/dev/configs/__init__.py`** - Configs package init ([configs-init.md](configs-init.md))
- **`{package_name}/dev/builders/__init__.py`** - Builders package init ([builders-init.md](builders-init.md))

## Common Issues

### Issue: Import error for src package

**Symptom:** `ModuleNotFoundError: No module named 'my_awesome_project.src'`

**Cause:** Package not installed or `__init__.py` missing

**Solution:**
```bash
# Ensure package is installed
uv sync

# Verify __init__.py exists
ls my_awesome_project/src/__init__.py

# If missing, run pyrig init
uv run pyrig init
```

### Issue: Want to add utilities to src

**Symptom:** Where should I put utility functions?

**Cause:** Not sure about project structure

**Solution:**
```python
# Option 1: Add to src/__init__.py
# my_awesome_project/src/__init__.py
"""src package."""

def my_utility():
    """My utility function."""
    pass

# Option 2: Create submodules
# my_awesome_project/src/utils.py
"""Utility functions."""

def my_utility():
    """My utility function."""
    pass
```

### Issue: Pyrig overwrites my changes

**Symptom:** Changes to `src/__init__.py` are lost

**Cause:** Pyrig regenerates the file

**Solution:**

Pyrig uses subset validation - it only checks that the docstring is present. You can add code after the docstring:

```python
"""src package."""

# Your code here is preserved
def my_utility():
    """My utility function."""
    pass
```

As long as the docstring `"""src package."""` is present, pyrig won't overwrite your changes.

### Issue: Want to use pyrig's utilities

**Symptom:** How do I access pyrig's src utilities?

**Cause:** Not familiar with pyrig's structure

**Solution:**
```python
# Import directly from pyrig
from pyrig.src.modules.module import import_module_from_path
from pyrig.src.git.git import get_git_root
from pyrig.src.os.os import run_subprocess
from pyrig.src.testing.assertions import assert_with_msg

# Use in your code
root = get_git_root()
result = run_subprocess(["echo", "hello"])
```

## Best Practices

### ✅ DO

- **Keep it minimal** - Only add what you need
- **Use submodules** - Create separate files for utilities
- **Preserve docstring** - Keep `"""src package."""` at the top
- **Import from pyrig** - Use pyrig's utilities when possible
- **Document additions** - Add docstrings to your utilities

### ❌ DON'T

- **Don't remove the docstring** - Pyrig expects it
- **Don't duplicate pyrig utilities** - Import them instead
- **Don't make it complex** - Keep utilities simple
- **Don't put business logic here** - Use main package for that
- **Don't create deep hierarchies** - Keep structure flat

## Advanced Usage

### Creating a Custom Utility Module

```python
# my_awesome_project/src/database.py
"""Database utilities for my-awesome-project."""

from typing import Any
import sqlite3


def connect_db(db_path: str) -> sqlite3.Connection:
    """Connect to the database."""
    return sqlite3.connect(db_path)


def execute_query(conn: sqlite3.Connection, query: str) -> list[Any]:
    """Execute a query and return results."""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()
```

```python
# Use in your code
from my_awesome_project.src.database import connect_db, execute_query

conn = connect_db("data.db")
results = execute_query(conn, "SELECT * FROM users")
```

### Extending Pyrig's Utilities

```python
# my_awesome_project/src/git.py
"""Git utilities extending pyrig's git module."""

from pyrig.src.git.git import get_git_root, run_git_command


def get_current_branch() -> str:
    """Get the current git branch."""
    result = run_git_command(["branch", "--show-current"])
    return result.stdout.decode().strip()


def is_clean_working_tree() -> bool:
    """Check if the working tree is clean."""
    result = run_git_command(["status", "--porcelain"])
    return len(result.stdout) == 0
```

### Creating a Shared Constants Module

```python
# my_awesome_project/src/constants.py
"""Shared constants for my-awesome-project."""

# API Configuration
API_BASE_URL = "https://api.example.com"
API_VERSION = "v1"
API_TIMEOUT = 30

# File Paths
DATA_DIR = "data"
CACHE_DIR = ".cache"
LOG_DIR = "logs"

# Feature Flags
ENABLE_CACHING = True
ENABLE_LOGGING = True
DEBUG_MODE = False
```

```python
# Use in your code
from my_awesome_project.src.constants import API_BASE_URL, API_TIMEOUT

response = requests.get(API_BASE_URL, timeout=API_TIMEOUT)
```

## See Also

- [Python Packages](https://docs.python.org/3/tutorial/modules.html#packages) - Official Python docs
- [__init__.py](https://docs.python.org/3/reference/import.html#regular-packages) - Package initialization
- [configs/__init__.py](configs-init.md) - Configs package init
- [builders/__init__.py](builders-init.md) - Builders package init
- [resources/__init__.py](resources-init.md) - Resources package init
- [Getting Started Guide](../getting-started.md) - Initial project setup


