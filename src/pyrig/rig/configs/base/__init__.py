"""Abstract base classes for declarative configuration file management.

Subclasses declare what a configuration file must contain; the base
infrastructure handles reading, merging, validating, and writing to disk
automatically across the full config lifecycle.

The hierarchy specializes from a common lifecycle contract through
format-specific bases to domain-specific uses. To introduce a new
configuration file type, subclass the appropriate format layer and
implement its abstract methods.
"""
