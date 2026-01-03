# Pyrigger (pyrig)

Type-safe wrapper for pyrig CLI commands.

## Overview

`Pyrigger` provides programmatic access to pyrig commands:

- Converting function objects to command names
- Constructing pyrig command arguments

This is used internally by pyrig for executing its own commands
programmatically.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_cmd_args(cmd, *args)` | `pyrig <cmd_name>` | Construct pyrig command from callable |

## Usage

```python
from pyrig.dev.management.pyrigger import Pyrigger
from pyrig.dev.cli.subcommands import build, test

# Run pyrig build
Pyrigger.L.get_cmd_args(build).run()

# Run pyrig test with arguments
Pyrigger.L.get_cmd_args(test, "-v").run()
```

## Subclassing Example

To add default arguments to all pyrig commands:

```python
# myapp/dev/management/pyrigger.py
from collections.abc import Callable
from typing import Any
from pyrig.dev.management.pyrigger import Pyrigger as BasePyrigger
from pyrig.src.processes import Args

class Pyrigger(BasePyrigger):
    @classmethod
    def get_cmd_args(cls, cmd: Callable[..., Any], *args: str) -> Args:
        # Add verbose flag to all commands
        return super().get_cmd_args(cmd, "--verbose", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [CLI Documentation](../cli/index.md) - pyrig CLI reference
