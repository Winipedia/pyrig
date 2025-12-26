"""Base classes for artifact builders.

This package provides the abstract `Builder` base class that defines the
interface and orchestration logic for all artifact builders in the pyrig
ecosystem.

The Builder class handles the complete build lifecycle including temporary
directory management, artifact creation, platform-specific renaming, and
automatic discovery of builder subclasses across dependent packages.

Classes:
    Builder: Abstract base class for all artifact builders.

See Also:
    pyrig.dev.builders.base.base: Full Builder implementation
"""
