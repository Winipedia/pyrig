"""Base classes for configuration file management.

This package provides a layered hierarchy of abstract base classes for declaring,
validating, and managing project configuration files. Subclasses define what a
configuration file should contain; the base classes handle the full lifecycle of
reading, merging, validating, and writing that content to disk.

The hierarchy is organized by increasing specialization: a root abstract class
defines the complete config lifecycle, format-specific subclasses add parsing and
serialization for TOML, YAML, JSON, plain text, Python, and Markdown files, and
domain-specific subclasses build on those to support tasks such as module copying
and GitHub Actions workflow generation.

To add a new configuration file, subclass the appropriate format base, implement
the required abstract methods, and let the framework handle validation, merging,
and writing automatically.
"""
