# ResourcesInitConfigFile

## Overview

**File Location:** `{package_name}/resources/__init__.py`
**ConfigFile Class:** `ResourcesInitConfigFile`
**File Type:** Python
**Priority:** Standard

Creates the `resources` package for storing static resource files (templates, data files, images, etc.) that need to be bundled with your application. This package works seamlessly with PyInstaller for creating standalone executables.

## Purpose

The `{package_name}/resources/__init__.py` file establishes the resources package:

- **Package Marker** - Makes `resources` a valid Python package
- **Resource Storage** - Provides a place for static files
- **PyInstaller Compatible** - Works with frozen executables
- **Importlib Resources** - Uses standard library for resource access
- **Bundling** - Resources are automatically included in distributions

### Why pyrig manages this file

pyrig creates `resources/__init__.py` to:
1. **Consistent structure** - All pyrig projects have a `resources` package
2. **Resource bundling** - Ensures resources are included in packages
3. **PyInstaller support** - Resources work in frozen executables
4. **Best practices** - Uses `importlib.resources` for access
5. **Package discovery** - Ensures Python recognizes `resources` as a package

The file is created during `pyrig init` with only the docstring from pyrig's `resources` package.

## File Location

The file is placed in your package's `resources` directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   └── resources/
│       ├── __init__.py  # <-- Here
│       ├── config.json
│       ├── template.txt
│       └── icon.png
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   └── resources/
│       ├── __init__.py  # <-- Mirrored from here
│       ├── GITIGNORE
│       ├── LATEST_PYTHON_VERSION
│       └── MIT_LICENSE_TEMPLATE
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `resources.__init__`:

```python
"""__init__ module."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.resources.__init__`
- **Required:** Yes (minimal package marker)
- **Purpose:** Documents the package
- **Why pyrig sets it:** Provides context for the package

**Why only the docstring:**
- **Minimal** - Doesn't impose implementation
- **Flexible** - You can add your own resources
- **Documentation** - Preserves pyrig's documentation
- **Package marker** - Makes directory a valid package

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/resources/__init__.py`

**File contents:**
```python
"""__init__ module."""
```

## What Are Resources?

Resources are static files that your application needs at runtime:

- **Configuration files** - JSON, YAML, TOML templates
- **Data files** - CSV, XML, text files
- **Templates** - HTML, email templates
- **Images** - Icons, logos, graphics
- **Binary files** - Fonts, audio, video

### Why Use a Resources Package?

**Benefits:**
- **Bundling** - Automatically included in distributions
- **PyInstaller** - Works in frozen executables
- **Relative paths** - No hardcoded file paths
- **Cross-platform** - Works on Windows, macOS, Linux
- **Standard library** - Uses `importlib.resources`

## Accessing Resources

### Using pyrig's Utility

```python
from pyrig.src.resource import get_resource_path
import my_awesome_project.resources as resources

# Get path to a resource file
config_path = get_resource_path("config.json", resources)
data = config_path.read_text()
```

### Using importlib.resources Directly

```python
from importlib.resources import files
import my_awesome_project.resources as resources

# Get path to a resource file
resource_path = files(resources) / "config.json"
data = resource_path.read_text()
```

### In Context Manager (Recommended for PyInstaller)

```python
from importlib.resources import as_file, files
import my_awesome_project.resources as resources

# Use context manager for PyInstaller compatibility
resource = files(resources) / "config.json"
with as_file(resource) as path:
    data = path.read_text()
```

## Adding Resources

### Example: Configuration Template

```json
// my_awesome_project/resources/config.json
{
  "app_name": "my-awesome-project",
  "version": "1.0.0",
  "settings": {
    "debug": false,
    "log_level": "INFO"
  }
}
```

```python
# Access in your code
from pyrig.src.resource import get_resource_path
import my_awesome_project.resources as resources

config_path = get_resource_path("config.json", resources)
import json

config = json.loads(config_path.read_text())
print(config["app_name"])  # "my-awesome-project"
```

### Example: Text Template

```
// my_awesome_project/resources/email_template.txt
Hello {name},

Welcome to {app_name}!

Best regards,
The Team
```

```python
# Access in your code
from pyrig.src.resource import get_resource_path
import my_awesome_project.resources as resources

template_path = get_resource_path("email_template.txt", resources)
template = template_path.read_text()

email = template.format(name="Alice", app_name="My Awesome Project")
print(email)
```

### Example: Binary Resource

```python
# my_awesome_project/resources/icon.png (binary file)

# Access in your code
from pyrig.src.resource import get_resource_path
import my_awesome_project.resources as resources

icon_path = get_resource_path("icon.png", resources)
icon_data = icon_path.read_bytes()

# Use with PIL/Pillow
from PIL import Image
image = Image.open(icon_path)
```

## Pyrig's Resources

Pyrig uses resources for its own templates:

### GITIGNORE

```python
# pyrig/resources/GITIGNORE
# Contains the standard Python .gitignore template
```

### LATEST_PYTHON_VERSION

```python
# pyrig/resources/LATEST_PYTHON_VERSION
# Contains the latest Python version number
```

### MIT_LICENSE_TEMPLATE

```python
# pyrig/resources/MIT_LICENSE_TEMPLATE
# Contains the MIT License template
```

### Accessing Pyrig's Resources

```python
from pyrig.src.resource import get_resource_path
import pyrig.resources as resources

# Get the MIT license template
license_path = get_resource_path("MIT_LICENSE_TEMPLATE", resources)
license_text = license_path.read_text()
```

## PyInstaller Integration

Resources work seamlessly with PyInstaller:

### Development (Source)

```python
# Resources accessed from filesystem
/path/to/my_awesome_project/resources/config.json
```

### Production (PyInstaller Bundle)

```python
# Resources extracted to temporary directory
/tmp/_MEIxxxxxx/my_awesome_project/resources/config.json
```

### Why It Works

`importlib.resources` handles both cases transparently:
- **Development** - Reads from source directory
- **PyInstaller** - Extracts from bundle to temp directory
- **No code changes** - Same code works in both environments

## Organizing Resources

### Flat Structure

```
my_awesome_project/
└── resources/
    ├── __init__.py
    ├── config.json
    ├── template.txt
    └── icon.png
```

### Nested Structure

```
my_awesome_project/
└── resources/
    ├── __init__.py
    ├── configs/
    │   ├── __init__.py
    │   ├── dev.json
    │   └── prod.json
    ├── templates/
    │   ├── __init__.py
    │   ├── email.txt
    │   └── report.html
    └── images/
        ├── __init__.py
        ├── icon.png
        └── logo.png
```

```python
# Access nested resources
import my_awesome_project.resources.configs as configs
from pyrig.src.resource import get_resource_path

dev_config_path = get_resource_path("dev.json", configs)
```

## Customization

You can add utilities to the `__init__.py`:

### Example: Resource Loader Utilities

```python
# my_awesome_project/resources/__init__.py
"""__init__ module."""

import json
from pathlib import Path
from importlib.resources import files


def load_json(filename: str) -> dict:
    """Load a JSON resource file."""
    resource = files(__package__) / filename
    return json.loads(resource.read_text())


def load_template(filename: str) -> str:
    """Load a text template resource."""
    resource = files(__package__) / filename
    return resource.read_text()


def get_resource_bytes(filename: str) -> bytes:
    """Load a binary resource file."""
    resource = files(__package__) / filename
    return resource.read_bytes()
```

```python
# Use in your code
from my_awesome_project.resources import load_json, load_template

config = load_json("config.json")
template = load_template("email_template.txt")
```

### Example: Resource Registry

```python
# my_awesome_project/resources/__init__.py
"""__init__ module."""

from importlib.resources import files


class ResourceRegistry:
    """Registry of available resources."""

    @classmethod
    def list_resources(cls) -> list[str]:
        """List all available resources."""
        resource_dir = files(__package__)
        return [f.name for f in resource_dir.iterdir() if f.is_file()]

    @classmethod
    def resource_exists(cls, filename: str) -> bool:
        """Check if a resource exists."""
        return filename in cls.list_resources()


# Export for convenience
__all__ = ["ResourceRegistry"]
```

## Related Files

- **`{package_name}/__init__.py`** - Main package init (created by pyrig)
- **`{package_name}/dev/__init__.py`** - Dev package init (created by pyrig)
- **`{package_name}/dev/configs/__init__.py`** - Configs package init ([configs-init.md](configs-init.md))
- **`{package_name}/dev/builders/__init__.py`** - Builders package init ([builders-init.md](builders-init.md))

## Common Issues

### Issue: Resource not found

**Symptom:** `FileNotFoundError: Resource 'config.json' not found`

**Cause:** Resource file doesn't exist or wrong package

**Solution:**
```bash
# Ensure resource exists
ls my_awesome_project/resources/config.json

# Ensure you're using the correct package
# Correct:
import my_awesome_project.resources as resources

# Incorrect:
import my_awesome_project as resources
```

### Issue: Resource not included in distribution

**Symptom:** Resource works in development but not in installed package

**Cause:** Resource not included in package data

**Solution:**
```toml
# pyproject.toml
[tool.uv]
package = true

# Resources are automatically included if they're in the package directory
```

Pyrig's `pyproject.toml` configuration automatically includes all files in the package directory.

### Issue: PyInstaller can't find resource

**Symptom:** Resource works in development but not in PyInstaller bundle

**Cause:** Not using `importlib.resources`

**Solution:**
```python
# Don't use hardcoded paths
# Bad:
path = Path("my_awesome_project/resources/config.json")

# Good: Use importlib.resources
from importlib.resources import files
import my_awesome_project.resources as resources

resource = files(resources) / "config.json"
```

### Issue: Want to modify resources at runtime

**Symptom:** Need to update resource files

**Cause:** Resources are read-only in distributions

**Solution:**

Resources should be read-only templates. For runtime data:

```python
# Copy resource to user directory
from pathlib import Path
from pyrig.src.resource import get_resource_path
import my_awesome_project.resources as resources

# Get template from resources
template_path = get_resource_path("config.json", resources)
template = template_path.read_text()

# Write to user directory
user_config = Path.home() / ".my-awesome-project" / "config.json"
user_config.parent.mkdir(parents=True, exist_ok=True)
user_config.write_text(template)

# Modify user config
import json
config = json.loads(user_config.read_text())
config["user_setting"] = "value"
user_config.write_text(json.dumps(config, indent=2))
```

## Best Practices

### ✅ DO

- **Use importlib.resources** - Standard library, PyInstaller compatible
- **Keep resources read-only** - Don't modify in place
- **Use descriptive names** - `email_template.txt`, not `template1.txt`
- **Organize by type** - Group related resources
- **Document resources** - Add README in resources directory

### ❌ DON'T

- **Don't use hardcoded paths** - Use `importlib.resources`
- **Don't store secrets** - Use environment variables
- **Don't store large files** - Keep resources small
- **Don't modify resources** - Copy to user directory first
- **Don't use absolute paths** - Use package-relative paths

## Advanced Usage

### Resource with Fallback

```python
# my_awesome_project/resources/__init__.py
"""__init__ module."""

from importlib.resources import files
from pathlib import Path


def get_config_path() -> Path:
    """Get config path with fallback."""
    # Try user config first
    user_config = Path.home() / ".my-awesome-project" / "config.json"
    if user_config.exists():
        return user_config

    # Fall back to resource template
    resource = files(__package__) / "config.json"
    return Path(str(resource))
```

### Resource Caching

```python
# my_awesome_project/resources/__init__.py
"""__init__ module."""

from functools import lru_cache
from importlib.resources import files
import json


@lru_cache(maxsize=None)
def load_cached_json(filename: str) -> dict:
    """Load and cache a JSON resource."""
    resource = files(__package__) / filename
    return json.loads(resource.read_text())
```

### Resource Validation

```python
# my_awesome_project/resources/__init__.py
"""__init__ module."""

from importlib.resources import files
import json


def validate_resource(filename: str) -> bool:
    """Validate a JSON resource file."""
    try:
        resource = files(__package__) / filename
        json.loads(resource.read_text())
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False
```

## See Also

- [importlib.resources](https://docs.python.org/3/library/importlib.resources.html) - Official Python docs
- [PyInstaller](https://pyinstaller.org/) - Creating standalone executables
- [Package Data](https://packaging.python.org/en/latest/guides/using-manifest-in/) - Including data files
- [configs/__init__.py](configs-init.md) - Configs package init
- [builders/__init__.py](builders-init.md) - Builders package init
- [src/__init__.py](src-init.md) - Src package init
- [Getting Started Guide](../getting-started.md) - Initial project setup


