# api.md

API reference documentation page generated from Python docstrings using
mkdocstrings.

## Purpose

Creates `docs/api.md` with automatic API reference documentation extracted from
your project's Python code. This provides comprehensive documentation of all
modules, classes, functions, and their docstrings.

## Location

**File**: `docs/api.md`

**Created by**: `ApiConfigFile` in `pyrig/rig/configs/markdown/docs/api.py`

## Default Content

```markdown
# API Reference

::: {project_name}
```

The `::: {project_name}` syntax is mkdocstrings notation that automatically
generates documentation for the entire project package.

## How It Works

The mkdocstrings plugin (configured in `mkdocs.yml`) processes the
`::: {project_name}` directive and:

1. **Discovers all modules** in your project package
2. **Extracts docstrings** from modules, classes, functions, and methods
3. **Generates formatted documentation** with type hints, parameters, and return
   values
4. **Creates navigation** for browsing the API reference

## Configuration

The mkdocstrings plugin is configured in `mkdocs.yml` with:

```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
            members: true
            show_source: true
            inherited_members: true
            filters: []
            show_submodules: true
```

**Options**:

- `docstring_style: google` - Uses Google-style docstrings
- `members: true` - Shows all class/module members
- `show_source: true` - Includes source code links
- `inherited_members: true` - Shows inherited methods
- `filters: []` - No filters applied, all members (including private) are shown
- `show_submodules: true` - Includes submodules in documentation

## What Gets Documented

By default, the API reference includes **all code in your project**:

- All modules in `{project_name}/`
- All classes and their methods
- All functions
- All module-level variables
- Development infrastructure (`rig/` folder)
- Source code (`src/` folder)
- Resources (`resources/` folder)

**Note**: This comprehensive approach documents all code, including development
tools and internal utilities. If you need a more focused API reference (e.g.,
only public API from `src/`), you should override the `ApiConfigFile` class
and `MkdocsConfigFile` and customize the content.

## Customizing the API Reference

To create a custom API reference that documents only specific parts of your
project:

### Override ApiConfigFile

Create `myapp/rig/configs/markdown/docs/api.py`:

```python
from pyrig.rig.configs.markdown.docs.api import ApiConfigFile as BaseApiCF
from pyrig.rig.configs.pyproject import PyprojectConfigFile


class ApiConfigFile(BaseApiCF):
    """Custom API reference for public API only."""

    @classmethod
    def lines(cls) -> list[str]:
        """Document only the public API from src/."""
        project_name = PyprojectConfigFile.I.project_name()
        return [
            "# API Reference",
            "",
            "## Public API",
            "",
            f"::: {project_name}.src",
            "    options:",
            "      members:",
            "        - MyPublicClass",
            "        - my_public_function",
            "      show_submodules: false",
            "",
            "## Utilities",
            "",
            f"::: {project_name}.src.utils",
            "",
        ]
```

Common customizations include documenting only `src/`, specific modules, or
specific classes, and excluding private members. Override `lines()` and
return the appropriate mkdocstrings directives.

## Docstring Style

pyrig uses **Google-style docstrings**. Example:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description of the function.

    Longer description with more details about what the
    function does and how to use it.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")
    return len(param1) > param2
```

This will be automatically formatted in the API documentation with proper
sections for parameters, return values, and exceptions.

## See Also

- [MkDocs Configuration](mkdocs.md) - Documentation site configuration
- [Index.md](index_md.md) - Documentation homepage
- [mkdocstrings documentation](https://mkdocstrings.github.io/) - Full
  mkdocstrings reference
