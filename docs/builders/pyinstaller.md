# PyInstaller Builder

pyrig provides `PyInstallerBuilder`, an abstract builder for creating standalone
executables from Python projects using PyInstaller.

Note: The entire reason your main.py file is generated with a
`if __name__ == "__main__":` guard is so that it can be used as an executable
entry point. PyInstaller needs to execute that file to create a proper
executable. We also kept it because it is a Python standard. However, we prefer
using the CLI framework for running code.

## Overview

`PyInstallerBuilder` handles:

- **Executable creation** with PyInstaller
- **Resource bundling** from multiple packages
- **Icon conversion** to platform-specific formats
- **Platform-specific configuration** (Windows/macOS/Linux)
- **Automatic resource discovery** across dependency chain

## Quick Start

### 1. Create a Builder Subclass

```python
from types import ModuleType
from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
import myapp.resources

class MyAppBuilder(PyInstallerBuilder):
    @classmethod
    def additional_resource_pkgs(cls) -> list[ModuleType]:
        """Specify packages containing resources to bundle."""
        return [myapp.resources]
```

A use case we had was that we needed to add the migrations folder for a database
once as we had it not located in the resources directory. Resource modules from
packages depending on pyrig are discovered automatically via
`default_additional_resource_pkgs()`.

### 2. Add an Icon

Place `icon.png` in your resources directory:

```text
myapp/
└── resources/
    └── icon.png  # 256x256 PNG recommended
```

Note: You can also override `app_icon_png_path` to use a different icon at a
custom location. However, it's recommended to keep it in the resources
directory.

### 3. Build

```bash
uv run pyrig build
```

Output: `dist/myapp-Linux` (or `myapp-Darwin`, `myapp-Windows`)

## How It Works

```mermaid
graph TD
    A[PyInstallerBuilder instantiated] --> B[Collect resource packages]
    B --> C[Build PyInstaller options]
    C --> D[Convert icon to platform format]
    D --> E[Run PyInstaller]
    E --> F[Executable created in temp dir]
    F --> G[Move to dist/ with platform suffix]

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#e76f51,stroke:#333,stroke-width:2px,color:#000
    style E fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style F fill:#9d84b7,stroke:#333,stroke-width:2px,color:#000
    style G fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

## Resource Bundling

### Automatic Resource Discovery

Resources are automatically collected from:

1. **All packages depending on pyrig** - their `resources` modules
2. **Your additional packages** - specified in `additional_resource_pkgs`

```mermaid
graph LR
    A[pyrig.resources] --> D[Bundled in executable]
    B[pkg_a.resources] --> D
    C[myapp.resources] --> D

    style A fill:#a8dadc,stroke:#333,stroke-width:2px,color:#000
    style B fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style C fill:#f4a261,stroke:#333,stroke-width:2px,color:#000
    style D fill:#90be6d,stroke:#333,stroke-width:2px,color:#000
```

### Resource Package Structure

```text
myapp/
└── resources/
    ├── __init__.py
    ├── icon.png
    ├── config.json
    └── templates/
        └── default.html
```

All files in resource packages are bundled into the executable as additional
data files using PyInstaller's `collect_data_files` utility. This preserves the
package structure and makes resources accessible at runtime via
`importlib.resources` or `pyrig.src.resource`.

## Icon Management

### Icon Conversion

PyInstaller requires platform-specific icon formats:

- **Windows**: `.ico`
- **macOS**: `.icns`
- **Linux**: `.png` (PyInstaller ignores the `--icon` parameter on Linux,
but the icon is still processed for consistency)

`PyInstallerBuilder` automatically converts your `icon.png` to the appropriate
format for Windows and macOS. On Linux, the PNG icon is passed through without
conversion, but PyInstaller will not embed it in the executable as Linux
executables do not support embedded icons.

### Custom Icon Location

Override `app_icon_png_path` to use a different icon:

```python
from pathlib import Path
from types import ModuleType
from pyrig.rig.builders.pyinstaller import PyInstallerBuilder
import myapp.another_resources_pkg

class MyAppBuilder(PyInstallerBuilder):
    @classmethod
    def additional_resource_pkgs(cls) -> list[ModuleType]:
        return [myapp.another_resources_pkg]

    @classmethod
    def app_icon_png_path(cls) -> Path:
        """Use custom icon location."""
        return cls.root_path() / "assets" / "custom-icon.png"
```

## PyInstaller Options

The builder generates these PyInstaller options:

| Option        | Value                            | Purpose                                       |
| ------------- | -------------------------------- | --------------------------------------------- |
| (positional)  | `cls.main_path()`            | Entry point script (main.py)                  |
| `--name`      | Project name from pyproject.toml | Executable name                               |
| `--onefile`   | Enabled                          | Single executable file                        |
| `--noconsole` | Enabled                          | No console window (GUI mode)                  |
| `--clean`     | Enabled                          | Clean build cache                             |
| `--noconfirm` | Enabled                          | Replace output directory without confirmation |
| `--icon`      | Platform-specific icon           | Application icon                              |
| `--add-data`  | All resource packages            | Bundle resources                              |
| `--workpath`  | Temp directory                   | Build artifacts location                      |
| `--specpath`  | Temp directory                   | Spec file location                            |
| `--distpath`  | Temp directory                   | Output location                               |

### Customizing Options

Override `pyinstaller_options` for full control:

```python
class MyAppBuilder(PyInstallerBuilder):
    @classmethod
    def additional_resource_pkgs(cls) -> list[ModuleType]:
        return [myapp.resources]

    @classmethod
    def pyinstaller_options(cls, temp_artifacts_dir: Path) -> list[str]:
        """Customize PyInstaller options."""
        options = super().pyinstaller_options(temp_artifacts_dir)

        # Remove --noconsole to show console
        options.remove("--noconsole")

        # Add hidden imports
        options.extend(["--hidden-import", "my_hidden_module"])

        return options
```

## Advanced Customization

For details on additional overridable methods (resource management, path
management, icon conversion), see the docstrings in the `PyInstallerBuilder`
class.

### Multiple Resource Packages

```python
import myapp.resources
import myapp.templates
import myapp.data

class MyAppBuilder(PyInstallerBuilder):
    @classmethod
    def additional_resource_pkgs(cls) -> list[ModuleType]:
        return [
            myapp.resources,
            myapp.templates,
            myapp.data,
        ]
```

### Custom Output Directory

```python
class MyAppBuilder(PyInstallerBuilder):
    ARTIFACTS_DIR_NAME = "build/executables"  # Custom output directory

    @classmethod
    def additional_resource_pkgs(cls) -> list[ModuleType]:
        return [myapp.resources]
```

## Multi-Package Example

```text
pyrig (base package)
├── resources/
│   └── base-config.json
│
Package A (depends on pyrig)
├── resources/
│   └── pkg-a-data.json
│
My App (depends on Package A)
├── rig/
│   └── builders/
│       └── executable.py  # MyAppBuilder
└── resources/
    ├── icon.png
    └── app-config.json

Running `uv run pyrig build`:
✓ Discovers MyAppBuilder
✓ Bundles pyrig.resources (base-config.json)
✓ Bundles pkg_a.resources (pkg-a-data.json)
✓ Bundles myapp.resources (icon.png, app-config.json)
✓ Converts icon.png to platform format
✓ Creates executable: dist/myapp-Linux
```

## Requirements

PyInstaller builder requires PyInstaller and Pillow (for icon conversion). These
dependencies are included automatically via `pyrig-dev` when you run
`pyrig init` or `pyrig mkroot`.
