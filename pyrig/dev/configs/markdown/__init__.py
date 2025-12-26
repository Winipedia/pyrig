"""Markdown configuration file management.

This subpackage provides configuration file managers for Markdown documentation
files, including README.md and MkDocs documentation pages.

The subpackage includes:
    - **ReadmeConfigFile**: Manages README.md with project name header and badges
    - **docs subpackage**: Manages MkDocs documentation files
        - **IndexConfigFile**: Manages docs/index.md (home page)
        - **ApiConfigFile**: Manages docs/api.md (API reference)

All Markdown files are generated with:
    - Project name headers
    - Status badges (build, coverage, version, etc.)
    - Proper formatting and structure
    - Integration with MkDocs for documentation sites

Modules:
    readme: README.md configuration management
    docs: MkDocs documentation files (index.md, api.md)

See Also:
    pyrig.dev.configs.base.badges_md.BadgesMarkdownConfigFile
        Base class for Markdown files with badges
    pyrig.dev.configs.docs.mkdocs.MkdocsConfigFile
        MkDocs configuration for building documentation sites
"""
