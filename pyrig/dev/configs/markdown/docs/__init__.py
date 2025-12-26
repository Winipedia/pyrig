"""MkDocs documentation file management.

This subpackage provides configuration file managers for MkDocs documentation
pages in the docs/ directory.

The subpackage includes:
    - **IndexConfigFile**: Manages docs/index.md (home page with badges)
    - **ApiConfigFile**: Manages docs/api.md (API reference with mkdocstrings)

Both files are used by MkDocs to generate the documentation website:
    - index.md serves as the home page
    - api.md generates API documentation from Python docstrings

Modules:
    index: docs/index.md configuration management
    api: docs/api.md configuration management

See Also:
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        MkDocs configuration that references these files
"""
