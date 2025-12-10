# Builder System

pyrig provides an extensible builder system for creating distributable artifacts. Builders are automatically discovered across all packages depending on pyrig and invoked during the release workflow.

## Overview

The builder system enables:

- **Executable Creation** — Build standalone executables with PyInstaller
- **Artifact Generation** — Create any type of distributable artifact
- **Multi-Package Discovery** — Builders from all dependent packages are found automatically
- **CI/CD Integration** — Artifacts are built across OS matrix and attached to releases
- **Platform Naming** — Artifacts are automatically suffixed with platform names

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Builder System                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────────────┐
  │                        Abstract Base Classes                            │
  │                                                                         │
  │   Builder (ABC)                     PyInstallerBuilder (ABC)            │
  │   ├── create_artifacts()            ├── extends Builder                 │
  │   ├── build()                       ├── get_additional_resource_pkgs()  │
  │   ├── rename_artifacts()            ├── get_pyinstaller_options()       │
  │   └── get_non_abstract_subclasses() └── handles icon conversion         │
  └────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                      Your Concrete Builders                             │
  │                                                                         │
  │   MyAppBuilder(PyInstallerBuilder)                                      │
  │   ├── Implements get_additional_resource_pkgs()                         │
  │   └── Creates standalone executable                                     │
  │                                                                         │
  │   MyCustomBuilder(Builder)                                              │
  │   ├── Implements create_artifacts()                                     │
  │   └── Creates any custom artifact                                       │
  └────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                         Output: dist/                                   │
  │                                                                         │
  │   myapp-Linux                                                           │
  │   myapp-Windows.exe                                                     │
  │   myapp-Darwin                                                          │
  └────────────────────────────────────────────────────────────────────────┘
```

## The Builder Base Class

All builders inherit from the abstract `Builder` class:

```python
from abc import ABC, abstractmethod
from pathlib import Path

class Builder(ABC):
    """Abstract base class for artifact builders."""
    
    ARTIFACTS_DIR_NAME = "dist"
    
    @classmethod
    @abstractmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Create artifacts in the temporary directory.
        
        Args:
            temp_artifacts_dir: Where to write artifacts.
        """
    
    def __init__(self) -> None:
        """Initialize the builder and trigger the build."""
        self.build()

    @classmethod
    def build(cls) -> None:
        """Execute the build process."""
        # 1. Create temp directory
        # 2. Call create_artifacts()
        # 3. Move and rename artifacts to dist/
```

### Key Methods

| Method | Purpose |
|--------|---------|
| `create_artifacts()` | Abstract — implement to create your artifacts |
| `build()` | Orchestrates temp dir creation and artifact naming |
| `rename_artifacts()` | Adds platform suffix (e.g., `-Linux`, `-Windows`) |
| `get_artifacts_dir()` | Returns output directory (default: `dist/`) |
| `get_non_abstract_subclasses()` | Discovers all concrete builders |
| `init_all_non_abstract_subclasses()` | Builds all discovered builders |
| `get_app_name()` | Returns project name from pyproject.toml |
| `get_root_path()` | Returns project root directory |

## The PyInstallerBuilder Class

For creating standalone executables, extend `PyInstallerBuilder`:

```python
from types import ModuleType
from pyrig.dev.artifacts.builders.pyinstaller import PyInstallerBuilder

class MyAppBuilder(PyInstallerBuilder):
    """Builds a standalone executable for my application."""

    @classmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Return packages containing resources to bundle."""
        return [my_app.resources, my_app.assets]
```

### PyInstallerBuilder Features

| Feature | Description |
|---------|-------------|
| **Automatic Icon Conversion** | Converts PNG to ICO (Windows) or ICNS (macOS) |
| **Resource Bundling** | Bundles resources from all dependent packages |
| **One-File Mode** | Creates single executable (`--onefile`) |
| **No Console** | Hides console window (`--noconsole`) |
| **Cross-Platform** | Same code works on Linux, Windows, macOS |

### PyInstallerBuilder Methods

| Method | Purpose |
|--------|---------|
| `get_additional_resource_pkgs()` | Abstract — return packages with resources to bundle |
| `get_all_resource_pkgs()` | Combines default + additional resource packages |
| `get_add_datas()` | Builds `--add-data` arguments for PyInstaller |
| `get_pyinstaller_options()` | Returns complete PyInstaller CLI options |
| `get_app_icon_path()` | Returns platform-appropriate icon path |
| `convert_png_to_format()` | Converts icon to ICO/ICNS/PNG |
| `get_app_icon_png_path()` | Returns path to source icon.png |

## Creating a Custom Builder

### Basic Builder

Create a builder in `your_project/dev/artifacts/builders/`:

```python
# your_project/dev/artifacts/builders/my_builder.py
from pathlib import Path
from pyrig.dev.artifacts.builders.base.base import Builder

class MyBuilder(Builder):
    """Creates custom artifacts for my project."""

    @classmethod
    def create_artifacts(cls, temp_artifacts_dir: Path) -> None:
        """Create the artifacts."""
        # Write your artifact to temp_artifacts_dir
        artifact_path = temp_artifacts_dir / "my-artifact.zip"

        # Example: create a zip archive
        import shutil
        shutil.make_archive(
            str(artifact_path.with_suffix("")),
            "zip",
            cls.get_root_path() / "data"
        )
```

### PyInstaller Builder

For executable creation:

```python
# your_project/dev/artifacts/builders/app_builder.py
from types import ModuleType
from pyrig.dev.artifacts.builders.pyinstaller import PyInstallerBuilder

import my_project.resources

class MyAppBuilder(PyInstallerBuilder):
    """Builds standalone executable for my application."""

    @classmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        """Return packages with resources to bundle."""
        return [my_project.resources]
```

### Custom PyInstaller Options

Override methods to customize PyInstaller behavior:

```python
class MyAppBuilder(PyInstallerBuilder):

    @classmethod
    def get_additional_resource_pkgs(cls) -> list[ModuleType]:
        return [my_project.resources]

    @classmethod
    def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
        """Add custom PyInstaller options."""
        options = super().get_pyinstaller_options(temp_artifacts_dir)

        # Add hidden imports
        options.extend(["--hidden-import", "my_module"])

        # Add data files
        options.extend(["--add-data", f"config.yaml{os.pathsep}."])

        # Enable console for debugging
        options.remove("--noconsole")

        return options
```

## Builder Discovery

pyrig automatically discovers all non-abstract Builder subclasses:

```python
from pyrig.dev.artifacts.builders.base.base import Builder

# Get all discovered builders
builders = Builder.get_non_abstract_subclasses()
for builder_cls in builders:
    print(f"Found: {builder_cls.__module__}.{builder_cls.__name__}")
```

### Discovery Mechanism

```python
@classmethod
def get_non_abstract_subclasses(cls) -> list[type["Builder"]]:
    """Discover all non-abstract Builder subclasses."""
    return get_all_nonabst_subcls_from_mod_in_all_deps_depen_on_dep(
        cls,           # Builder class
        pyrig,         # Root dependency
        builders,      # Module to search within
        discard_parents=True,
    )
```

The discovery:
1. Finds all packages depending on pyrig
2. Locates `dev/artifacts/builders/` in each package
3. Imports all modules in those directories
4. Returns all non-abstract Builder subclasses
5. Discards parent classes (only returns leaf implementations)

## Directory Structure

Place your builders in the correct location:

```
your_project/
├── dev/
│   └── artifacts/
│       ├── builders/
│       │   ├── __init__.py
│       │   ├── my_builder.py      # Your builder implementations
│       │   └── app_builder.py
│       └── resources/
│           ├── __init__.py
│           └── icon.png           # Application icon (256x256 recommended)
├── src/
└── pyproject.toml
```

The `__init__.py` in builders is created automatically by:

```python
# your_project/dev/configs/python/builders_init.py
from pyrig.dev.configs.python.builders_init import BuildersInitConfigFile

class BuildersInitConfigFile(BuildersInitConfigFile):
    pass
```

## Running Builders

### Locally

```bash
# Build all artifacts
uv run pyrig build
```

This calls:

```python
# pyrig/dev/artifacts/build.py
def build_artifacts() -> None:
    """Build all artifacts by invoking all registered Builder subclasses."""
    Builder.init_all_non_abstract_subclasses()
```

### In CI/CD

The release workflow automatically builds artifacts across all OS:

```yaml
# .github/workflows/release.yaml
jobs:
  build:
    strategy:
      matrix:
        os:
        - ubuntu-latest
        - windows-latest
        - macos-latest
    runs-on: ${{ matrix.os }}
    steps:
    - name: Build Artifacts
      run: uv run pyrig build

    - name: Upload Artifacts
      uses: actions/upload-artifact@main
      with:
        name: artifacts-${{ matrix.os }}
        path: dist/*
```

## Release Workflow Integration

### Build Job

If builders are defined, the release workflow:

```python
@classmethod
def steps_build(cls) -> list[dict[str, Any]]:
    """Get the steps for building artifacts."""
    non_abstract_builders = Builder.get_non_abstract_subclasses()
    if not non_abstract_builders:
        return [cls.step_no_builder_defined()]  # Skip if no builders
    return [
        *cls.steps_core_matrix_setup(),
        cls.step_build_artifacts(),      # uv run pyrig build
        cls.step_upload_artifacts(),     # Upload to GitHub Actions
    ]
```

### Release Job

Artifacts are downloaded and attached to the GitHub release:

```yaml
- name: Download Artifacts
  uses: actions/download-artifact@main
  with:
    path: dist
    merge-multiple: 'true'

- name: Create Release
  uses: ncipollo/release-action@main
  with:
    artifacts: dist/*
```

## Artifact Naming

Artifacts are automatically renamed with platform suffixes:

```python
@classmethod
def rename_artifacts(cls, artifacts: list[Path]) -> None:
    """Move artifacts with platform-specific names."""
    for artifact in artifacts:
        new_name = f"{artifact.stem}-{platform.system()}{artifact.suffix}"
        # myapp → myapp-Linux
        # myapp.exe → myapp-Windows.exe
```

| Original | Linux | Windows | macOS |
|----------|-------|---------|-------|
| `myapp` | `myapp-Linux` | `myapp-Windows.exe` | `myapp-Darwin` |
| `archive.zip` | `archive-Linux.zip` | `archive-Windows.zip` | `archive-Darwin.zip` |

## Resource Bundling

### How Resources Are Found

PyInstallerBuilder automatically bundles resources from:

1. **Default resources** — From all packages depending on pyrig:
   ```python
   def get_default_additional_resource_pkgs(cls) -> list[ModuleType]:
       return get_same_modules_from_deps_depen_on_dep(resources, pyrig)
   ```

2. **Additional resources** — From your `get_additional_resource_pkgs()`:
   ```python
   def get_all_resource_pkgs(cls) -> list[ModuleType]:
       return [
           *cls.get_default_additional_resource_pkgs(),
           *cls.get_additional_resource_pkgs(),
       ]
   ```

### The --add-data Arguments

Resources are bundled using PyInstaller's `--add-data`:

```python
@classmethod
def get_add_datas(cls) -> list[tuple[Path, Path]]:
    """Build --add-data arguments."""
    add_datas = []
    for pkg in cls.get_all_resource_pkgs():
        pkg_path = to_path(pkg, is_package=True)
        # Walk directory tree and add all files
        for item in pkg_path.rglob("*"):
            if item.is_file():
                relative = item.relative_to(pkg_path)
                add_datas.append((item, relative.parent))
    return add_datas
```

## Icon Handling

### Icon Requirements

Place your icon at:
```
your_project/dev/artifacts/resources/icon.png
```

Recommended specifications:
- Format: PNG
- Size: 256x256 pixels (or larger)
- Transparency: Supported

### Automatic Conversion

PyInstallerBuilder converts the icon based on platform:

```python
@classmethod
def get_app_icon_path(cls, temp_dir: Path) -> Path:
    """Get platform-appropriate icon path."""
    if platform.system() == "Windows":
        return cls.convert_png_to_format("ico", temp_dir)
    if platform.system() == "Darwin":
        return cls.convert_png_to_format("icns", temp_dir)
    return cls.convert_png_to_format("png", temp_dir)
```

| Platform | Format | Extension |
|----------|--------|-----------|
| Windows | ICO | `.ico` |
| macOS | ICNS | `.icns` |
| Linux | PNG | `.png` |

## Troubleshooting

### "No non-abstract builders defined"

**Cause**: No concrete Builder subclasses found.

**Solution**:
1. Create a builder in `dev/artifacts/builders/`
2. Ensure it's not marked `ABC`
3. Ensure `__init__.py` exists

### "ModuleNotFoundError" during build

**Cause**: Missing hidden import.

**Solution**:
```python
@classmethod
def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
    options = super().get_pyinstaller_options(temp_artifacts_dir)
    options.extend(["--hidden-import", "missing_module"])
    return options
```

### "No such file: icon.png"

**Cause**: Icon file missing.

**Solution**:
1. Create `dev/artifacts/resources/icon.png`
2. Or override `get_app_icon_png_path()`

### Artifacts not appearing in release

**Cause**: Upload step failed or artifacts not built.

**Solution**:
1. Check workflow logs for errors
2. Verify builders are discovered: `uv run python -c "from pyrig.dev.artifacts.builders.base.base import Builder; print(Builder.get_non_abstract_subclasses())"`
3. Run `uv run pyrig build` locally to test

### Large executable size

**Cause**: Unnecessary modules bundled.

**Solution**:
```python
@classmethod
def get_pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
    options = super().get_pyinstaller_options(temp_artifacts_dir)
    options.extend(["--exclude-module", "unused_module"])
    return options
```

## Summary

| Component | Description |
|-----------|-------------|
| **Builder** | Abstract base for all artifact builders |
| **PyInstallerBuilder** | Creates standalone executables |
| **create_artifacts()** | Method to implement for custom artifacts |
| **get_additional_resource_pkgs()** | Method to specify resources to bundle |
| **Discovery** | Automatic via `get_non_abstract_subclasses()` |
| **Location** | `your_project/dev/artifacts/builders/` |
| **Output** | `dist/` with platform-suffixed names |
| **CI/CD** | Build across OS matrix, attach to releases |

