# VersionController (git)

Type-safe wrapper for [Git](https://git-scm.com/), the version control system.

## Subclassing Example

```python
# myapp/rig/tools/version_controller.py
from pyrig.rig.tools.version_controller import VersionController as BaseVC
from pyrig.src.processes import Args

class VersionController(BaseVC):
    @classmethod
    def get_commit_args(cls, *args: str) -> Args:
        # Always sign commits
        return super().get_commit_args("-S", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
