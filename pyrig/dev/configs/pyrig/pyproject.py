"""Pyrig-specific pyproject.toml configuration overrides.

Extends the base PyprojectConfigFile with pyrig-specific PyPI classifiers and
keywords. Only active when pyrig itself is the project being configured.

The conditional class definition uses ``src_pkg_is_pyrig()`` to ensure this
class is only discoverable via ``__subclasses__()`` when running within pyrig's
repository. Other projects depending on pyrig will not inherit these settings.

Example:
    When generating pyproject.toml for pyrig itself::

        >>> from pyrig.dev.configs.pyrig.pyproject import PyprojectConfigFile
        >>> configs = PyprojectConfigFile.L.get_configs()
        >>> "project-setup" in configs["project"]["keywords"]
        True
        >>> any("Build Tools" in c for c in configs["project"]["classifiers"])
        True

See Also:
    pyrig.dev.configs.pyproject.PyprojectConfigFile: Base pyproject.toml config
    pyrig.dev.utils.packages.src_pkg_is_pyrig: Package detection utility
"""

from typing import Any

from pyrig.dev.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile
from pyrig.dev.utils.packages import src_pkg_is_pyrig

if src_pkg_is_pyrig():

    class PyprojectConfigFile(BasePyprojectConfigFile):
        """Pyrig-specific pyproject.toml configuration.

        Extends base PyprojectConfigFile with pyrig-specific PyPI metadata:
        development status, intended audience, topic classifiers, and keywords
        relevant to project scaffolding and automation tools.

        Only instantiated when pyrig is the current project (via conditional
        class definition). Other projects using pyrig as a dependency will use
        the base PyprojectConfigFile instead.

        See Also:
            pyrig.dev.configs.pyproject.PyprojectConfigFile: Parent class
        """

        @classmethod
        def make_python_version_classifiers(cls) -> list[str]:
            """Generate PyPI classifiers with pyrig-specific metadata.

            Prepends pyrig-specific classifiers to the base classifiers:
            development status, intended audience, and topic categories.

            Returns:
                Classifier list with pyrig-specific entries first, followed by
                Python version, OS, and typing classifiers from parent.
            """
            classifiers = super().make_python_version_classifiers()

            dev_statuses = ("Development Status :: 5 - Production/Stable",)
            intended_audiences = ("Intended Audience :: Developers",)
            topics = (
                "Topic :: Software Development :: Build Tools",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Topic :: Software Development :: Quality Assurance",
                "Topic :: Software Development :: Testing",
                "Topic :: System :: Installation/Setup",
                "Topic :: System :: Software Distribution",
            )
            return [*dev_statuses, *intended_audiences, *topics, *classifiers]

        @classmethod
        def _get_configs(cls) -> dict[str, Any]:
            """Generate complete pyproject.toml config with pyrig-specific keywords.

            Extends base configuration by adding keywords relevant to pyrig's
            purpose as a project scaffolding and automation toolkit.

            Returns:
                Complete pyproject.toml configuration dict with pyrig keywords.
            """
            configs = super()._get_configs()
            keywords = [
                "project-setup",
                "automation",
                "scaffolding",
                "cli",
                "testing",
                "ci-cd",
                "devops",
                "packaging",
            ]
            configs["project"]["keywords"] = keywords
            return configs
