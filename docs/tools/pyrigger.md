# Pyrigger (pyrig)

Type-safe wrapper for pyrig CLI commands. Used internally by pyrig for executing
its own commands programmatically.

## Subclassing Example

```python
# myapp/dev/tools/pyrigger.py
from collections.abc import Callable
from typing import Any
from pyrig.rig.tools.pyrigger import Pyrigger as BasePyrigger
from pyrig.src.processes import Args

class Pyrigger(BasePyrigger):
    @classmethod
    def get_cmd_args(cls, *args: str, cmd: Callable[..., Any]) -> Args:
        return super().get_cmd_args("--verbose", *args, cmd=cmd)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [CLI Documentation](../cli/index.md) - pyrig CLI reference
