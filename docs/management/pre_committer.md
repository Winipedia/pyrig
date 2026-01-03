# PreCommitter (pre-commit)

Type-safe wrapper for [pre-commit](https://pre-commit.com/), the git hook
manager.

Pre-commit enforces code quality by running linters, formatters, and checks
before each commit.

## Subclassing Example

```python
# myapp/dev/management/pre_committer.py
from pyrig.dev.management.pre_committer import PreCommitter as BasePC
from pyrig.src.processes import Args

class PreCommitter(BasePC):
    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        return super().get_run_all_files_args("--show-diff-on-failure", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - pre-commit](../more/tooling.md#pre-commit) - Why pyrig uses
  pre-commit
