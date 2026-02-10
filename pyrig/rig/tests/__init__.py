"""Test infrastructure and pytest fixtures for pyrig-based projects.

Provides automatic fixture discovery, test coverage enforcement, and project
validation for pyrig projects. Fixtures from all packages depending on pyrig
are automatically registered via ``conftest.py``.

Subpackages:
    fixtures: Reusable pytest fixtures organized by purpose and scope.

Key Features:
    - Automatic fixture discovery across the dependency chain
    - Test coverage enforcement via autouse fixtures
    - Project structure and configuration validation
    - Factory fixtures for isolated ConfigFile testing
"""
