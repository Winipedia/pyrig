# PreCommitter (prek)

Type-safe wrapper for [prek](https://github.com/j178/prek), the git hook
manager.

Prek enforces code quality by running linters, formatters, and checks
before each commit.

## Subclassing Example

```python
# myapp/rig/tools/pre_committer.py
from pyrig.rig.tools.pre_committer import PreCommitter as BasePC
from pyrig.src.processes import Args

class PreCommitter(BasePC):
    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        return super().get_run_all_files_args("--show-diff-on-failure", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - prek](../more/tooling.md#prek) - Why pyrig uses
  prek
