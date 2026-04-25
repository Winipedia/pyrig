"""Base classes for artifact builders.

Provides the abstract foundation for all artifact builders in pyrig. Builders
extend the configuration file framework to produce build artifacts such as
executables and packages using a standardized build lifecycle: temporary
workspace management, artifact creation, platform-specific naming, and
output directory management.
"""
