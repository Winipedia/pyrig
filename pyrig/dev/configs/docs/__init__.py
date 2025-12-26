"""Documentation configuration file management.

This subpackage provides configuration file managers for documentation-related
files, specifically MkDocs configuration for generating project documentation.

The MkdocsConfigFile class generates a complete mkdocs.yml configuration with:
    - Project metadata (name from pyproject.toml)
    - Material theme with dark/light mode toggle
    - Navigation structure (Home, API)
    - Plugins for search, mermaid diagrams, and API documentation
    - mkdocstrings configuration for Google-style docstrings

The generated documentation site includes:
    - Automatic API documentation from docstrings
    - Search functionality
    - Mermaid diagram support
    - Responsive Material Design theme
    - Dark/light mode toggle

Modules:
    mkdocs: mkdocs.yml configuration management

See Also:
    MkDocs: https://www.mkdocs.org/
    Material for MkDocs: https://squidfunk.github.io/mkdocs-material/
    mkdocstrings: https://mkdocstrings.github.io/
"""
