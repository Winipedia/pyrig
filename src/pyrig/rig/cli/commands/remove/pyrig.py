"""Backend for the `rm pyrig` CLI command that ejects pyrig from a project."""

from pyrig_runtime.core.dependencies.discovery import dependent_packages
from pyrig_runtime.core.strings import snake_to_kebab_case

import pyrig
from pyrig.rig.configs.version_control.hooks.manager import (
    VersionControlHookManagerConfigFile,
)
from pyrig.rig.configs.version_control.remote.workflows.health_check import (
    HealthCheckWorkflowConfigFile,
)
from pyrig.rig.tools.packages.manager import PackageManager
from pyrig.rig.tools.pyrigger import Pyrigger


def remove_pyrig() -> None:
    """Remove pyrig and its footprint from the project entirely.

    Runs the full removal sequence: strips the `pyrig mk local` step from
    the health check workflow, removes the `pyrig sync` hook from the
    version control hook pipeline, then uninstalls pyrig and its plugins
    from the dev dependency group.

    Warning:
        One-way: everything pyrig previously generated is left in place as
        plain, standalone output, but pyrig itself is no longer wired into
        the project afterward.
    """
    remove_pyrig_step_from_health_check_workflow()
    remove_pyrig_hooks()
    uninstall_pyrig()


def remove_pyrig_step_from_health_check_workflow() -> None:
    """Remove the `pyrig mk local` step from the health check workflow."""
    configs = HealthCheckWorkflowConfigFile.I.load()
    configs["jobs"][next(iter(HealthCheckWorkflowConfigFile.I.job_health_checks()))][
        "steps"
    ].remove(
        HealthCheckWorkflowConfigFile.I.step_create_version_control_ignored_files(),
    )
    HealthCheckWorkflowConfigFile.I.dump(configs=configs)


def remove_pyrig_hooks() -> None:
    """Remove pyrig's hooks from the version control hook pipeline."""
    configs = VersionControlHookManagerConfigFile.I.load()
    hooks = next(repo for repo in configs["repos"] if repo["repo"] == "local")["hooks"]
    for hook in Pyrigger.I.hooks():
        hooks.remove(hook)
    VersionControlHookManagerConfigFile.I.dump(configs=configs)


def uninstall_pyrig() -> None:
    """Uninstall pyrig and its plugins from the dev dependency group."""
    PackageManager.I.remove_group_dev_args(
        Pyrigger.I.name(),
        *(snake_to_kebab_case(dep.__name__) for dep in dependent_packages(pyrig)),
    ).run()
