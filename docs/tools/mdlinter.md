# MDLinter (rumdl)

Type-safe wrapper for [rumdl](https://github.com/rvben/rumdl), the fast
Markdown linter.

rumdl is a Rust-based Markdown linter that enforces consistent formatting and
catches common issues.

## Subclassing Example

```python
# myapp/rig/tools/mdlinter.py
from pyrig.rig.tools.mdlinter import MDLinter as BaseMDL
from pyrig.src.processes import Args

class MDLinter(BaseMDL):
    @classmethod
    def check_args(cls, *args: str) -> Args:
        return super().check_args("--verbose", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
