"""Base classes for configuration file management.

Provides a layered hierarchy of abstract base classes for declaring, validating,
and managing project configuration files. Subclasses declare what a configuration
file should contain; the base classes handle the full lifecycle of reading,
merging, validating, and writing that content to disk.

The hierarchy is organized by increasing specialization: [ConfigFile][] is the
root abstract class that defines the complete config lifecycle, format-specific
subclasses add parsing and serialization for plain text, Python, Markdown, and
JSON files, and domain-specific subclasses build on those to support tasks such as
module copying.

To add a new configuration file, subclass the appropriate format base, implement
the required abstract methods, and let the framework handle validation, merging,
and writing automatically.
"""
