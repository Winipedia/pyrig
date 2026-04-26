"""Pyrig-specific pyproject.toml configuration overrides.

Extends the base pyproject.toml configuration with PyPI classifiers and keywords
relevant to pyrig's purpose as a project scaffolding and automation toolkit.
Only active when pyrig itself is the project being configured.

The conditional class definition gates subclass registration so that
``__subclasses__()`` only discovers this class when running inside pyrig's own
repository, leaving dependent projects unaffected.
"""

from pyrig.core.introspection.packages import src_package_is_pyrig
from pyrig.rig.configs.base.config_file import ConfigDict
from pyrig.rig.configs.pyproject import PyprojectConfigFile as BasePyprojectConfigFile

if src_package_is_pyrig():

    class PyprojectConfigFile(BasePyprojectConfigFile):
        """Pyrig-specific pyproject.toml configuration.

        Extends the base ``PyprojectConfigFile`` with PyPI metadata specific to
        pyrig: development status, intended audience, topic classifiers, and
        project-related keywords for package discovery.

        Only defined when pyrig is the current project (via the module-level
        conditional). Projects that use pyrig as a dependency get the base class
        defaults instead.
        """

        def _configs(self) -> ConfigDict:
            """Build pyproject.toml configuration with pyrig-specific keywords.

            Calls the base implementation and replaces the empty
            ``project.keywords`` list with keywords that describe pyrig's purpose
            as a scaffolding and automation toolkit.

            Returns:
                Complete pyproject.toml configuration dict with pyrig-specific
                keywords populated in the ``project`` section.
            """
            configs = super()._configs()
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

        def make_python_version_classifiers(self) -> list[str]:
            """Build PyPI trove classifiers including pyrig-specific entries.

            Prepends development status, intended audience, and software
            development topic classifiers to the base set of Python version, OS,
            and typing classifiers returned by the parent.

            Returns:
                List of trove classifier strings with pyrig-specific entries
                first, followed by the parent's Python version, OS, and typing
                classifiers.
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

        def dependencies(self, default: list[str] | None = None) -> list[str]:
            """Read runtime dependencies with a pyrig-specific default.

            Overrides the base default from ``[Pyrigger.I.name()]`` to
            ``["typer"]``, reflecting that typer is pyrig's own primary runtime
            dependency.

            Args:
                default: Fallback list used when ``project.dependencies`` is
                    absent in pyproject.toml. Defaults to ``["typer"]``.

            Returns:
                Dependency list from pyproject.toml, or ``default`` if absent.
            """
            if default is None:
                default = ["typer"]
            return super().dependencies(default)
