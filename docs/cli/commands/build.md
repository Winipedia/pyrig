# build

Builds all project artifacts by invoking all registered BuilderConfigFile
subclasses.

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

1. **Discovers all BuilderConfigFile subclasses** across the project and its
   dependencies
2. **Invokes each builder** to create its artifacts
3. **Outputs artifacts** to the `dist/` directory

### Built-in Builder Base Classes

pyrig provides abstract base classes for building artifacts:

- **BuilderConfigFile** - Base class for all builders
- **PyInstallerBuilder** - Abstract base for creating PyInstaller executables
  (subclass this and implement `get_additional_resource_pkgs()` to use)

### Artifact Naming

Artifacts are automatically named with platform suffixes:

- Linux: `myapp-Linux`
- Windows: `myapp-Windows.exe`
- macOS: `myapp-Darwin`

**Note**: The suffix uses Python's `platform.system()` which returns "Darwin" on
macOS.

## How It Works

The build process:

1. **Creates temporary directory** for isolated builds
2. **Calls `create_artifacts()`** on each builder
3. **Renames artifacts** with platform-specific suffixes
4. **Moves artifacts** to `dist/` directory

## Creating Custom Builders

Create a custom builder by subclassing `BuilderConfigFile`:

```python
from pathlib import Path
from pyrig.dev.builders.base.base import BuilderConfigFile

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

Use `build` when:

- Creating release artifacts
- Testing the build process locally
- Generating executables for distribution

## Autouse Fixture

This command does **not** run in an autouse fixture. It's a manual build
command.

## CI/CD Integration

The `build` command is used in the Build workflow. See
[Build Workflow](../../configs/workflows/build.md) for details.

## Related

- [Builders Documentation](../../builders/index.md) - Complete builder system
  documentation
- [Build Workflow](../../configs/workflows/build.md) - CI/CD build process
