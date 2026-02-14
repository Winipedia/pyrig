# build

Builds all project artifacts by discovering and invoking all discovered
`BuilderConfigFile` subclasses.

## Usage

```bash
uv run pyrig build

# With verbose output to see build details
uv run pyrig -v build

# With detailed logging including module names
uv run pyrig -vv build
```

## What It Does

The `build` command:

1. **Discovers all non-abstract `BuilderConfigFile` subclasses** across the project
   and its dependencies
2. **Invokes each BuilderConfigFile** to create its artifacts
3. **Outputs artifacts** to the `dist/` directory with platform-specific naming

### Built-in Builders

- **BuilderConfigFile** - Base class for all builders
- **PyInstallerBuilder** - Abstract base for creating standalone executables

### Artifact Naming

Artifacts are automatically named with platform suffixes:

- Linux: `myapp-Linux`
- Windows: `myapp-Windows.exe`
- macOS: `myapp-Darwin`

## Creating Custom Builders

Create a custom builder by subclassing `BuilderConfigFile`:

```python
from pathlib import Path
from pyrig.rig.builders.base.base import BuilderConfigFile

class MyBuilder(BuilderConfigFile):
    """Custom artifact builder."""

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Create custom artifacts."""
        # Your build logic here
        output_file = temp_artifacts_dir / "my-artifact"
        output_file.write_text("artifact content")
```

See [Builders Documentation](../../builders/index.md) for complete details.

## When to Use

- Creating release artifacts
- Testing the build process locally
- Generating executables for distribution

## CI/CD Integration

The `build` command is used in the Build workflow. See
[Build Workflow](../../configs/workflows/build.md) for details.

## Related

- [Builders Documentation](../../builders/index.md) - Complete builder system
  documentation
- [Build Workflow](../../configs/workflows/build.md) - CI/CD build process
