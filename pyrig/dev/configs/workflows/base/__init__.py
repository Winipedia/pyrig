"""Base workflow configuration utilities.

This subpackage provides the Workflow base class and utilities for creating
GitHub Actions workflow configuration files.

The Workflow base class provides:
    - **Declarative API**: Build workflow YAML files programmatically
    - **Job Builders**: Utilities for creating common CI/CD jobs
    - **Step Builders**: Reusable step templates for common tasks
    - **Trigger Builders**: Methods for defining workflow triggers
    - **Matrix Strategies**: OS and Python version matrix configuration
    - **Artifact Management**: Upload/download artifact utilities

Key Features:
    - Type-safe workflow configuration
    - Reusable job and step templates
    - Automatic environment setup (uv, Python, caching)
    - Integration with pyrig's management tools
    - Support for multi-OS and multi-Python testing

Modules:
    base: Workflow base class with job/step builders

See Also:
    pyrig.dev.configs.workflows
        Concrete workflow implementations
    GitHub Actions: https://docs.github.com/en/actions
"""
