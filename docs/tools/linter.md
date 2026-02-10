# Linter (ruff)

Type-safe wrapper for [Ruff](https://github.com/astral-sh/ruff), the fast Python
linter and formatter.

Ruff is a Rust-based linter that replaces flake8, isort, pyupgrade, and black
with 10-100x faster performance.

## Subclassing Example

```python
# myapp/rig/tools/linter.py
from pyrig.rig.tools.linter import Linter as BaseLinter
from pyrig.src.processes import Args

class Linter(BaseLinter):
    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        return super().get_check_args("--show-source", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - Ruff](../more/tooling.md#ruff) - Why pyrig uses Ruff
