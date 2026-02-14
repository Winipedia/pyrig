# PackageIndex (pypi)

Constructs [PyPI](https://pypi.org/) package URLs and version badge Markdown for
your project.

Unlike other Tool wrappers that wrap external CLI tools, PackageIndex generates
PyPI URLs dynamically from your git remote configuration. It assumes the PyPI
package name matches the Git repository name. It's used internally by pyrig to
populate `[project.urls]` in pyproject.toml and badge links in README files.

## Subclassing Example

```python
# myapp/rig/tools/package_index.py
from pyrig.rig.tools.package_index import PackageIndex as BasePI

class PackageIndex(BasePI):
    @classmethod
    def package_index_url(cls) -> str:
        # Use a private registry instead of PyPI
        _, repo = VersionController.I.repo_owner_and_name(
            check_repo_url=False, url_encode=True
        )
        return f"https://private.registry.example.com/packages/{repo}"
```

## Related

- [Architecture](architecture.md) - Design philosophy and extension mechanisms
- [PackageManager](package_manager.md) - Dependencies, building, and publishing
