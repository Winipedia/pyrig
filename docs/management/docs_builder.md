# DocsBuilder (mkdocs)

Type-safe wrapper for [MkDocs](https://www.mkdocs.org/), the static site
generator for documentation.

## Overview

`DocsBuilder` wraps mkdocs commands for:

- Building documentation (`mkdocs build`)

MkDocs creates beautiful documentation sites from Markdown files, with support
for themes, plugins, and GitHub Pages deployment.

## Methods

| Method | Command | Description |
|--------|---------|-------------|
| `get_build_args(*args)` | `mkdocs build` | Build static site |

## Usage

```python
from pyrig.dev.management.docs_builder import DocsBuilder

# Build documentation
DocsBuilder.L.get_build_args().run()

# Build with strict mode
DocsBuilder.L.get_build_args("--strict").run()

# Build to custom directory
DocsBuilder.L.get_build_args("-d", "public/").run()
```

## Subclassing Example

To add default flags:

```python
# myapp/dev/management/docs_builder.py
from pyrig.dev.management.docs_builder import DocsBuilder as BaseDB
from pyrig.src.processes import Args

class DocsBuilder(BaseDB):
    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        # Always use strict mode
        return super().get_build_args("--strict", *args)
```

## Related

- [Architecture](architecture.md) - How the Tool system works
- [Tooling - MkDocs](../more/tooling.md#mkdocs) - Why pyrig uses MkDocs
- [MkDocs Config](../configs/mkdocs.md) - mkdocs.yml configuration
