"""Configuration file definitions for project scaffolding.

This package is the discovery root for all ``ConfigFile`` subclasses.
``ConfigFile.dependency_package()`` returns this module, so only subclasses
defined here — and in dependent packages that extend pyrig — are discovered
and validated.

Running ``pyrig sync`` calls ``ConfigFile.validate_concrete_subclasses()``, which
finds every concrete ``ConfigFile`` subclass in this package and in dependent
packages, and validates each one in priority order: creating missing files and
updating out-of-date ones while leaving correct files untouched.

To add a new managed configuration file, define a concrete ``ConfigFile``
subclass (from ``pyrig.rig.configs.base.config_file``) anywhere inside this
package.
"""
