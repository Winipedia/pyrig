"""Pyrig-specific configuration overrides.

Configuration classes in this package extend the default ``ConfigFile`` subclasses
with metadata and settings tailored to pyrig. They are conditionally defined at
import time using ``src_package_is_pyrig()``, which means they are only registered
as subclasses when pyrig itself is the active project. When pyrig is used as a
dependency in another project, these classes are never defined and therefore never
appear in subclass discovery, so they have no effect on other projects.
"""
