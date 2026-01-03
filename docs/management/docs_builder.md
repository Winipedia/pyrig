# DocsBuilder (mkdocs)

Type-safe wrapper for [MkDocs](https://www.mkdocs.org/), the static site
generator for documentation.

MkDocs creates beautiful documentation sites from Markdown files, with support
for themes, plugins, and GitHub Pages deployment.

## Subclassing Example

```python
# myapp/dev/management/docs_builder.py
from pyrig.dev.management.docs_builder import DocsBuilder as BaseDB
from pyrig.src.processes import Args

class DocsBuilder(BaseDB):
    @classmethod
    def get_build_args(cls, *args: str) -> Args:
        return super().get_build_args("--strict", *args)
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [Tooling - MkDocs](../more/tooling.md#mkdocs) - Why pyrig uses MkDocs
