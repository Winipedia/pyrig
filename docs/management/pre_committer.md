# PreCommitter (pre-commit)

Type-safe wrapper for [pre-commit](https://pre-commit.com/), the git hook
manager.

## Overview

`PreCommitter` wraps pre-commit commands for:

- Installing git hooks (`pre-commit install`)
- Running hooks (`pre-commit run`)
- Running on all files (`pre-commit run --all-files`)

Pre-commit enforces code quality by running linters, formatters, and checks
before each commit.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_install_args(*args)` | `pre-commit install` | Install git hooks |
| `get_run_args(*args)` | `pre-commit run` | Run on staged files |
| `get_run_all_files_args(*args)` | `pre-commit run --all-files` | Run on all files |
| `get_run_all_files_verbose_args(*args)` | `pre-commit run --all-files --verbose` | Run with verbose output |

## Usage

```python
from pyrig.dev.management.pre_committer import PreCommitter

# Install hooks
PreCommitter.L.get_install_args().run()

# Run on staged files
PreCommitter.L.get_run_args().run()

# Run on all files
PreCommitter.L.get_run_all_files_args().run()

# Run with verbose output
PreCommitter.L.get_run_all_files_verbose_args().run()

# Run specific hook
PreCommitter.L.get_run_args("ruff").run()
```

## Subclassing Example

To add custom flags:

```python
# myapp/dev/management/pre_committer.py
from pyrig.dev.management.pre_committer import PreCommitter as BasePC
from pyrig.src.processes import Args

class PreCommitter(BasePC):
    @classmethod
    def get_run_all_files_args(cls, *args: str) -> Args:
        # Show diff on failure
        return super().get_run_all_files_args("--show-diff-on-failure", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - pre-commit](../more/tooling.md#pre-commit) - Why pyrig uses
  pre-commit
- [Pre-commit Config](../configs/pre_commit.md) - .pre-commit-config.yaml
  configuration
