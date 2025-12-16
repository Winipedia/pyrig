# PyTypedConfigFile

## Overview

**File Location:** `<package>/py.typed`
**ConfigFile Class:** `PyTypedConfigFile`
**File Type:** Marker file (empty)
**Priority:** Standard

An empty marker file required by PEP 561 to indicate your package includes type annotations. Type checkers like mypy use this file to determine whether to check types when your package is used as a dependency.

## Purpose

The `py.typed` file signals PEP 561 compliance:

- **Enables type checking** - Type checkers recognize your package as typed
- **Distributes type information** - Type annotations are available to downstream projects

### Why pyrig manages this file

pyrig uses mypy in strict mode, requiring all code to be typed. The `py.typed` marker ensures type information is distributed with your package so downstream projects benefit from type safety.

## File Contents

The file is always empty (contains only a newline). PEP 561 requires this - any content would be invalid.

**File location:** `my_awesome_project/py.typed`

**File contents:**
```
[empty file]
```

## How It Works

### Without `py.typed`

Type checkers treat your package as untyped:

```python
from my_awesome_project import some_function
result = some_function()  # mypy treats return type as 'Any'
```

### With `py.typed`

Type checkers use your package's type annotations:

```python
from my_awesome_project import some_function
result = some_function()  # mypy knows the exact return type
```

## Related Files

- **`pyproject.toml`** - Mypy configuration ([pyproject.md](pyproject.md))

## Common Issues

### Issue: Type checkers ignore package types

**Cause:** File is missing or in wrong location

**Solution:**
```bash
# Verify file exists in package directory
ls my_awesome_project/py.typed

# Regenerate if missing
uv run pyrig mkroot
```

### Issue: File has content

**Cause:** Someone added content (must be empty)

**Solution:**
```bash
# Reset the file
uv run pyrig mkroot
```

## See Also

- [PEP 561](https://peps.python.org/pep-0561/) - Distributing type information
- [Mypy - Installed Packages](https://mypy.readthedocs.io/en/stable/installed_packages.html)

