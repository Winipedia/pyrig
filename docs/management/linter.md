# Linter (ruff)

Type-safe wrapper for [Ruff](https://github.com/astral-sh/ruff), the fast Python
linter and formatter.

## Overview

`Linter` wraps ruff commands for:

- Linting code (`ruff check`)
- Auto-fixing issues (`ruff check --fix`)
- Formatting code (`ruff format`)

Ruff is a Rust-based linter that replaces flake8, isort, pyupgrade, and black
with 10-100x faster performance.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_check_args(*args)` | `ruff check` | Check code for issues |
| `get_check_fix_args(*args)` | `ruff check --fix` | Check and auto-fix |
| `get_format_args(*args)` | `ruff format` | Format code |

## Usage

```python
from pyrig.dev.management.linter import Linter

# Check for issues
Linter.L.get_check_args().run()

# Check and auto-fix
Linter.L.get_check_fix_args().run()

# Format code
Linter.L.get_format_args().run()

# Check specific directory
Linter.L.get_check_args("src/").run()
```

## Subclassing Example

To add custom flags to checks:

```python
# myapp/dev/management/linter.py
from pyrig.dev.management.linter import Linter as BaseLinter
from pyrig.src.processes import Args

class Linter(BaseLinter):
    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        # Always show source code in errors
        return super().get_check_args("--show-source", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - Ruff](../more/tooling.md#ruff) - Why pyrig uses Ruff
- [pyproject.toml - Ruff](../configs/pyproject.md#ruff-linter--formatter) - Ruff
  configuration
