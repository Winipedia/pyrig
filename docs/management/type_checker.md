# TypeChecker (ty)

Type-safe wrapper for [ty](https://github.com/astral-sh/ty), Astral's fast
Python type checker.

## Overview

`TypeChecker` wraps ty commands for:

- Type checking (`ty check`)

ty is a Rust-based type checker from the creators of Ruff and uv, designed for
speed and accuracy.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_check_args(*args)` | `ty check` | Run type checking |

## Usage

```python
from pyrig.dev.management.type_checker import TypeChecker

# Check entire project
TypeChecker.L.get_check_args().run()

# Check specific directory
TypeChecker.L.get_check_args("src/").run()

# Check specific file
TypeChecker.L.get_check_args("myapp/core.py").run()
```

## Subclassing Example

To add custom flags:

```python
# myapp/dev/management/type_checker.py
from pyrig.dev.management.type_checker import TypeChecker as BaseTC
from pyrig.src.processes import Args

class TypeChecker(BaseTC):
    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        # Add verbose output
        return super().get_check_args("--verbose", *args)
```

## Replacing ty with mypy

To use mypy instead of ty:

```python
# myapp/dev/management/type_checker.py
from pyrig.dev.management.type_checker import TypeChecker as BaseTC

class TypeChecker(BaseTC):
    @classmethod
    def name(cls) -> str:
        return "mypy"
```

**Note**: You'll also need to update pre-commit hooks and pyproject.toml
configuration. See [Replacing Tools](architecture.md#replacing-tools).

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - ty](../more/tooling.md#ty) - Why pyrig uses ty
- [pyproject.toml - ty](../configs/pyproject.md#ty-type-checker) - ty
  configuration
