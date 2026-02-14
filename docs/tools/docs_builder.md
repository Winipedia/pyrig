# DocsBuilder (mkdocs)

Type-safe wrapper for [MkDocs](https://www.mkdocs.org/), the static site
generator for documentation.

MkDocs creates beautiful documentation sites from Markdown files, with support
for themes, plugins, and GitHub Pages deployment.

## Subclassing Example

```python
# myapp/rig/tools/docs_builder.py
from pyrig.rig.tools.docs_builder import DocsBuilder as BaseDB
from pyrig.src.processes import Args

class DocsBuilder(BaseDB):
    def build_args(self, *args: str) -> Args:
        return super().build_args("--strict", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - MkDocs](../more/tooling.md#mkdocs) - Why pyrig uses MkDocs
