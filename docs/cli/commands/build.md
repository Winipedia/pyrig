# build

Builds all project artifacts by invoking all registered Builder subclasses.

## Usage

```bash
uv run pyrig build
```

## What It Does

The `build` command:

1. **Discovers all Builder subclasses** across the project and its dependencies
2. **Invokes each builder** to create its artifacts
3. **Outputs artifacts** to the `dist/` directory

### Built-in Builders

pyrig includes a PyInstaller builder that creates standalone executables:
- **PyInstallerBuilder** - Creates platform-specific executables from `main.py`

### Artifact Naming

Artifacts are automatically named with platform suffixes:
- Linux: `myapp-Linux`
- Windows: `myapp-Windows.exe`
- macOS: `myapp-macOS`

## How It Works

The build process:

1. **Creates temporary directory** for isolated builds
2. **Calls `create_artifacts()`** on each builder
3. **Renames artifacts** with platform-specific suffixes
4. **Moves artifacts** to `dist/` directory

## Creating Custom Builders

Create a custom builder by subclassing `Builder`:

```python
from pathlib import Path
from pyrig.dev.builders.base.base import Builder

class MyBuilder(Builder):
    """Custom artifact builder."""
    
    @classmethod
    def create_artifacts(cls, artifacts_dir: Path) -> None:
        """Create custom artifacts."""
        # Your build logic here
        output_file = artifacts_dir / "my-artifact"
        output_file.write_text("artifact content")
```

See [Builders Documentation](../../builders/index.md) for complete details.

## When to Use

Use `build` when:
- Creating release artifacts
- Testing the build process locally
- Generating executables for distribution

## Autouse Fixture

This command does **not** run in an autouse fixture. It's a manual build command.

## CI/CD Integration

The `build` command is used in the Build workflow. See [Build Workflow](../../configs/workflows/build.md) for details.

## Related

- [Builders Documentation](../../builders/index.md) - Complete builder system documentation
- [Build Workflow](../../configs/workflows/build.md) - CI/CD build process

