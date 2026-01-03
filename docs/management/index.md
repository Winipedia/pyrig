# Tool Wrappers

pyrig wraps external tools in type-safe Python classes. Each Tool class
constructs command arguments that can be inspected, modified, and executed.

## Start Here

**[Architecture](architecture.md)** - Understand the design philosophy, the
`.L` pattern, `get_all_subclasses()`, and when customizations propagate
automatically vs when they require explicit overrides.

## Tools

Each tool page shows subclassing examples. For method details, see the source
docstrings.

| Tool | Wraps | Purpose |
|------|-------|---------|
| [PackageManager](package_manager.md) | uv | Dependencies, building, publishing |
| [VersionController](version_controller.md) | git | Version control |
| [Linter](linter.md) | ruff | Linting and formatting |
| [TypeChecker](type_checker.md) | ty | Type checking |
| [ProjectTester](project_tester.md) | pytest | Running tests |
| [PreCommitter](pre_committer.md) | pre-commit | Git hooks |
| [SecurityChecker](security_checker.md) | bandit | Security scanning |
| [MDLinter](mdlinter.md) | rumdl | Markdown linting |
| [DocsBuilder](docs_builder.md) | mkdocs | Documentation |
| [ContainerEngine](container_engine.md) | podman | Container builds |
| [Pyrigger](pyrigger.md) | pyrig | CLI wrapper |

## Quick Example

```python
from pyrig.dev.management.linter import Linter

# Get command arguments
args = Linter.L.get_check_args()
print(args)  # ruff check

# Execute
args.run()
```

## See Also

- [Tooling](../more/tooling.md) - Why pyrig chose each tool
- [Trade-offs](../more/drawbacks.md) - What you sacrifice and gain
