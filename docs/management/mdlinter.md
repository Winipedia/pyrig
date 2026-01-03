# MDLinter (rumdl)

Type-safe wrapper for [rumdl](https://github.com/pluveto/rumdl), the fast
Markdown linter.

## Overview

`MDLinter` wraps rumdl commands for:

- Checking Markdown files (`rumdl check`)
- Auto-fixing issues (`rumdl check --fix`)

rumdl is a Rust-based Markdown linter that enforces consistent formatting and
catches common issues.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_check_args(*args)` | `rumdl check` | Check Markdown files |
| `get_check_fix_args(*args)` | `rumdl check --fix` | Check and auto-fix |

## Usage

```python
from pyrig.dev.management.mdlinter import MDLinter

# Check all Markdown files
MDLinter.L.get_check_args().run()

# Check and auto-fix
MDLinter.L.get_check_fix_args().run()

# Check specific file
MDLinter.L.get_check_args("README.md").run()

# Check specific directory
MDLinter.L.get_check_args("docs/").run()
```

## Subclassing Example

To add custom flags:

```python
# myapp/dev/management/mdlinter.py
from pyrig.dev.management.mdlinter import MDLinter as BaseMDL
from pyrig.src.processes import Args

class MDLinter(BaseMDL):
    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        # Add verbose output
        return super().get_check_args("--verbose", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
