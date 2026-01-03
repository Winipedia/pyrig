# Tool Wrappers

pyrig wraps external tools in type-safe Python classes. Each Tool class
constructs command arguments that can be inspected, modified, and executed.

## Architecture

- [Architecture](architecture.md) - How the Tool system works, the `.L`
  property, and replacing tools

## Tools

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
print(args)  # Args(['ruff', 'check'])

# Execute
args.run()
```

## See Also

- [Tooling](../more/tooling.md) - Why pyrig chose each tool
- [Trade-offs](../more/drawbacks.md) - What you sacrifice and gain
