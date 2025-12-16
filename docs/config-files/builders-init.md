# BuildersInitConfigFile

## Overview

**File Location:** `{package_name}/dev/builders/__init__.py`
**ConfigFile Class:** `BuildersInitConfigFile`
**File Type:** Python
**Priority:** Standard

Creates the `builders` package within your project's `dev` directory. This package is where you define custom Builder classes for generating code, documentation, or other artifacts.

## Purpose

The `{package_name}/dev/builders/__init__.py` file establishes the builders package:

- **Package Marker** - Makes `builders` a valid Python package
- **Builder Organization** - Provides a place for custom Builder classes
- **Pyrig Mirroring** - Mirrors pyrig's `dev.builders` package structure
- **Automatic Discovery** - Builders in this package are automatically discovered
- **Extensibility** - Allows you to create project-specific builders

### Why pyrig manages this file

pyrig creates `dev/builders/__init__.py` to:
1. **Consistent structure** - All pyrig projects have a `builders` package
2. **Builder discovery** - Pyrig automatically finds Builder subclasses here
3. **Customization point** - You can add custom builders
4. **Documentation** - Docstring explains the package's purpose
5. **Package discovery** - Ensures Python recognizes `builders` as a package

The file is created during `pyrig init` with only the docstring from pyrig's `dev.builders` package.

## File Location

The file is placed in your package's `dev/builders` directory:

```
my-awesome-project/
├── my_awesome_project/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── builders/
│           └── __init__.py  # <-- Here
└── pyproject.toml
```

This mirrors pyrig's structure:

```
pyrig/
├── pyrig/
│   ├── __init__.py
│   └── dev/
│       ├── __init__.py
│       └── builders/
│           └── __init__.py  # <-- Mirrored from here
└── pyproject.toml
```

## File Structure

### Docstring Only

The file contains **only the docstring** from pyrig's `dev.builders.__init__`:

```python
"""__init__ module."""
```

- **Type:** Module docstring
- **Default:** Copied from `pyrig.dev.builders.__init__`
- **Required:** Yes (minimal package marker)
- **Purpose:** Documents the package
- **Why pyrig sets it:** Provides context for the package

**Why only the docstring:**
- **Minimal** - Doesn't impose implementation
- **Flexible** - You can add your own builders
- **Documentation** - Preserves pyrig's documentation
- **Package marker** - Makes directory a valid package

## Default Configuration

For a project named `my-awesome-project` with package `my_awesome_project`:

**File location:** `my_awesome_project/dev/builders/__init__.py`

**File contents:**
```python
"""__init__ module."""
```

## What Are Builders?

Builders are classes that generate code, documentation, or other artifacts. They extend the `Builder` base class and are automatically discovered by pyrig.

### Builder Base Class

```python
from pyrig.dev.builders.base import Builder

class MyBuilder(Builder):
    """My custom builder."""

    def build(self) -> None:
        """Build the artifact."""
        # Your build logic here
        pass
```

### Automatic Discovery

Pyrig automatically discovers all Builder subclasses in:
- `{package_name}/dev/builders/`
- Any package that depends on pyrig

This means you can create builders and they'll be automatically available.

## Creating Custom Builders

### Example: Documentation Builder

```python
# my_awesome_project/dev/builders/docs.py
"""Documentation builder."""

from pathlib import Path
from pyrig.dev.builders.base import Builder


class DocsBuilder(Builder):
    """Builds API documentation."""

    def build(self) -> None:
        """Generate API documentation."""
        docs_dir = Path("docs/api")
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Generate documentation
        content = self._generate_api_docs()
        (docs_dir / "index.md").write_text(content)

    def _generate_api_docs(self) -> str:
        """Generate API documentation content."""
        return "# API Documentation\n\nGenerated automatically."
```

### Example: Code Generator

```python
# my_awesome_project/dev/builders/models.py
"""Model code generator."""

from pathlib import Path
from pyrig.dev.builders.base import Builder


class ModelBuilder(Builder):
    """Generates model classes from schema."""

    def build(self) -> None:
        """Generate model classes."""
        models_dir = Path("my_awesome_project/models")
        models_dir.mkdir(parents=True, exist_ok=True)

        # Generate models
        for model_name in ["User", "Post", "Comment"]:
            content = self._generate_model(model_name)
            (models_dir / f"{model_name.lower()}.py").write_text(content)

    def _generate_model(self, name: str) -> str:
        """Generate a model class."""
        return f'''"""Generated {name} model."""

class {name}:
    """The {name} model."""

    def __init__(self):
        """Initialize the {name}."""
        pass
'''
```

### Example: Resource Builder

```python
# my_awesome_project/dev/builders/assets.py
"""Asset builder."""

from pathlib import Path
from pyrig.dev.builders.base import Builder


class AssetBuilder(Builder):
    """Builds static assets."""

    def build(self) -> None:
        """Build static assets."""
        assets_dir = Path("my_awesome_project/assets")
        assets_dir.mkdir(parents=True, exist_ok=True)

        # Copy or generate assets
        self._generate_css()
        self._generate_js()

    def _generate_css(self) -> None:
        """Generate CSS files."""
        css_content = "/* Generated CSS */\nbody { margin: 0; }"
        Path("my_awesome_project/assets/style.css").write_text(css_content)

    def _generate_js(self) -> None:
        """Generate JavaScript files."""
        js_content = "// Generated JS\nconsole.log('Hello');"
        Path("my_awesome_project/assets/app.js").write_text(js_content)
```

## Running Builders

### Using pyrig CLI

```bash
# Run all builders
uv run pyrig build

# Run specific builder
uv run pyrig build --builder DocsBuilder
```

### Programmatically

```python
from my_awesome_project.dev.builders.docs import DocsBuilder

# Run the builder
DocsBuilder().build()
```

## Customization

You can add imports or utilities to the `__init__.py`:

### Example: Export Builders

```python
# my_awesome_project/dev/builders/__init__.py
"""__init__ module."""

from my_awesome_project.dev.builders.docs import DocsBuilder
from my_awesome_project.dev.builders.models import ModelBuilder
from my_awesome_project.dev.builders.assets import AssetBuilder

__all__ = ["DocsBuilder", "ModelBuilder", "AssetBuilder"]
```

### Example: Shared Utilities

```python
# my_awesome_project/dev/builders/__init__.py
"""__init__ module."""

from pathlib import Path


def ensure_dir(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def write_file(path: Path, content: str) -> None:
    """Write content to a file."""
    ensure_dir(path.parent)
    path.write_text(content)
```

## Related Files

- **`{package_name}/dev/__init__.py`** - Dev package init (created by pyrig)
- **`{package_name}/dev/configs/__init__.py`** - Configs package init ([configs-init.md](configs-init.md))
- **`{package_name}/dev/resources/__init__.py`** - Resources package init ([resources-init.md](resources-init.md))
- **`{package_name}/src/__init__.py`** - Src package init ([src-init.md](src-init.md))

## Common Issues

### Issue: Builder not discovered

**Symptom:** Custom builder not found by pyrig

**Cause:** Builder not in the builders package or not a Builder subclass

**Solution:**
```python
# Ensure your builder:
# 1. Is in my_awesome_project/dev/builders/
# 2. Extends Builder base class
# 3. Implements build() method

from pyrig.dev.builders.base import Builder

class MyBuilder(Builder):
    """My builder."""

    def build(self) -> None:
        """Build logic."""
        pass
```

### Issue: Import error for builders package

**Symptom:** `ModuleNotFoundError: No module named 'my_awesome_project.dev.builders'`

**Cause:** Package not installed or `__init__.py` missing

**Solution:**
```bash
# Ensure package is installed
uv sync

# Verify __init__.py exists
ls my_awesome_project/dev/builders/__init__.py

# If missing, run pyrig init
uv run pyrig init
```

### Issue: Want to organize builders in subpackages

**Symptom:** Too many builders in one directory

**Cause:** Flat structure doesn't scale

**Solution:**
```bash
# Create subpackages
mkdir my_awesome_project/dev/builders/docs
mkdir my_awesome_project/dev/builders/code
mkdir my_awesome_project/dev/builders/assets

# Add __init__.py to each
touch my_awesome_project/dev/builders/docs/__init__.py
touch my_awesome_project/dev/builders/code/__init__.py
touch my_awesome_project/dev/builders/assets/__init__.py
```

```python
# my_awesome_project/dev/builders/docs/__init__.py
"""Documentation builders."""

from my_awesome_project.dev.builders.docs.api import APIDocsBuilder
from my_awesome_project.dev.builders.docs.user import UserDocsBuilder

__all__ = ["APIDocsBuilder", "UserDocsBuilder"]
```

## Best Practices

### ✅ DO

- **Keep builders focused** - One builder, one responsibility
- **Use descriptive names** - `APIDocsBuilder`, not `Builder1`
- **Implement build()** - Required method for all builders
- **Handle errors** - Builders should fail gracefully
- **Document builders** - Add docstrings explaining what they build

### ❌ DON'T

- **Don't remove the docstring** - Pyrig expects it
- **Don't put business logic here** - Builders are for generation
- **Don't make builders stateful** - Keep them simple
- **Don't hardcode paths** - Use Path objects and configuration
- **Don't create circular dependencies** - Keep builders independent

## Advanced Usage

### Builder with Configuration

```python
# my_awesome_project/dev/builders/configurable.py
"""Configurable builder."""

from pathlib import Path
from typing import Any
from pyrig.dev.builders.base import Builder


class ConfigurableBuilder(Builder):
    """Builder that accepts configuration."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize with configuration."""
        super().__init__()
        self.config = config or {}

    def build(self) -> None:
        """Build using configuration."""
        output_dir = Path(self.config.get("output_dir", "output"))
        output_dir.mkdir(parents=True, exist_ok=True)

        content = self.config.get("content", "Default content")
        (output_dir / "output.txt").write_text(content)
```

### Builder with Dependencies

```python
# my_awesome_project/dev/builders/dependent.py
"""Builder with dependencies."""

from pyrig.dev.builders.base import Builder
from my_awesome_project.dev.builders.docs import DocsBuilder


class DependentBuilder(Builder):
    """Builder that depends on other builders."""

    def build(self) -> None:
        """Build after running dependencies."""
        # Run dependency first
        DocsBuilder().build()

        # Then do our work
        self._build_index()

    def _build_index(self) -> None:
        """Build index of generated docs."""
        # Implementation here
        pass
```

### Builder with Validation

```python
# my_awesome_project/dev/builders/validated.py
"""Builder with validation."""

from pathlib import Path
from pyrig.dev.builders.base import Builder


class ValidatedBuilder(Builder):
    """Builder that validates before building."""

    def build(self) -> None:
        """Build with validation."""
        if not self._validate():
            raise ValueError("Validation failed")

        self._do_build()

    def _validate(self) -> bool:
        """Validate preconditions."""
        # Check that required files exist
        return Path("schema.json").exists()

    def _do_build(self) -> None:
        """Perform the build."""
        # Implementation here
        pass
```

## See Also

- [Builder Pattern](https://en.wikipedia.org/wiki/Builder_pattern) - Design pattern
- [configs/__init__.py](configs-init.md) - Configs package init
- [resources/__init__.py](resources-init.md) - Resources package init
- [src/__init__.py](src-init.md) - Src package init
- [Getting Started Guide](../getting-started.md) - Initial project setup


