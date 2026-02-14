"""Base classes for tool wrappers.

This package provides the abstract base classes used by all tool wrappers in
``pyrig.rig.tools``. The `Tool` class enables type-safe, composable
command-line argument construction, badge generation, and dev-dependency
discovery.

See Also:
    pyrig.rig.tools.base.base: Implementation of `Tool` and `ToolGroup`.
    pyrig.src.processes: Implementation of `Args`, the command container
        returned by ``Tool`` methods.
    pyrig.src.subclass: `SingletonDependencySubclass`, the discovery
        base that ``Tool`` inherits from.
"""
