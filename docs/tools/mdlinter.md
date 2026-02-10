# MDLinter (rumdl)

Type-safe wrapper for [rumdl](https://github.com/rvben/rumdl), the fast
Markdown linter.

rumdl is a Rust-based Markdown linter that enforces consistent formatting and
catches common issues.

## Subclassing Example

```python
# myapp/dev/tools/mdlinter.py
from pyrig.dev.tools.mdlinter import MDLinter as BaseMDL
from pyrig.src.processes import Args

class MDLinter(BaseMDL):
    @classmethod
    def get_check_args(cls, *args: str) -> Args:
        return super().get_check_args("--verbose", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
