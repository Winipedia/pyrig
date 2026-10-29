"""Shell script that applies repository configuration via the GitHub CLI."""

from pathlib import Path
from typing import override

from pyrig.rig.configs.base.shell import ShellConfigFile
from pyrig.rig.configs.version_control.remote.settings import (
    RepositorySettingsConfigFile,
)
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class ConfigureRepositoryConfigFile(ShellConfigFile):
    """Configuration manager for the repository setup script.

    The generated script requires nonempty `GITHUB_REPOSITORY` and `GH_TOKEN`
    environment variables and is intended to be run directly.
    """

    @override
    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.config_dir()

    @override
    def required_env_vars(self) -> tuple[str, ...]:
        """Return the required names: `GH_TOKEN` and `GITHUB_REPOSITORY`."""
        return ("GH_TOKEN", self.repo_variable())

    @override
    def script(self) -> str:
        """Return the function definitions and the block that runs them.

        Returns:
            The shell function definitions returned by `scripts()` and the
            block that runs every function. The shared header and required
            environment checks are prepended by `content()`.
        """
        return f"""{self.scripts_content()}

{self.footer_content()}
"""

    @override
    def stem(self) -> str:
        """Return `"configure"`."""
        return "configure"

    def footer_content(self) -> str:
        """Return the block that runs every function the script defines.

        Placed at the end of the script, after every function is defined,
        so they all exist by the time this runs. A newly added function
        needs no corresponding change here to run automatically.

        Returns:
            Shell code that loops over and calls every defined function.
        """
        return """for step in $(declare -F | awk '{print $3}'); do
  "${step}"
done"""

    def scripts_content(self) -> str:
        """Return the content of all scripts defined in this file.

        Returns:
            The concatenation of every script returned by `scripts()`.
        """
        return "\n\n".join(sorted(self.scripts()))

    def scripts(self) -> tuple[str, ...]:
        """Return the shell function definitions that make up the script."""
        return (
            self.repo_script(),
            self.rulesets_script(),
            self.release_immutability_script(),
            self.dependency_alerts_script(),
            self.dependency_security_updates_script(),
        )

    def dependency_alerts_script(self) -> str:
        """Return the `dependency_alerts` shell function.

        Returns:
            Function definition that `PUT`s the GitHub API endpoint that
            enables Dependabot alerts (and the dependency graph) for the
            repository.
        """
        endpoint = f'"repos/${{{self.repo_variable()}}}/vulnerability-alerts"'
        api_call = RemoteVersionController.I.api_method_args(
            endpoint=endpoint,
            method="PUT",
        )
        return f"""{self.dependency_alerts_func()}() {{
  {api_call}
}}"""

    def dependency_security_updates_script(self) -> str:
        """Return the `dependency_security_updates` shell function.

        Returns:
            Function definition that `PUT`s the GitHub API endpoint that
            enables Dependabot security updates (automated security fixes)
            for the repository.
        """
        endpoint = f'"repos/${{{self.repo_variable()}}}/automated-security-fixes"'
        api_call = RemoteVersionController.I.api_method_args(
            endpoint=endpoint,
            method="PUT",
        )
        return f"""{self.dependency_security_updates_func()}() {{
  {api_call}
}}"""

    def release_immutability_script(self) -> str:
        """Return the `release_immutability` shell function as a multi-line string.

        Returns:
            Function definition that `PUT`s the GitHub API endpoint that
            enables immutable releases for the repository.
        """
        endpoint = f'"repos/${{{self.repo_variable()}}}/immutable-releases"'
        api_call = RemoteVersionController.I.api_method_args(
            endpoint=endpoint,
            method="PUT",
        )
        return f"""{self.release_immutability_func()}() {{
  {api_call}
}}"""

    def repo_script(self) -> str:
        """Return the `repository` shell function as a multi-line string.

        Returns:
            Function definition that pipes the `repository` key of the
            settings file into `gh api` as a `PATCH` request.
        """
        settings_path = RepositorySettingsConfigFile.I.path().as_posix()
        repo_key = RepositorySettingsConfigFile.I.repo_key()
        endpoint = f'"repos/${{{self.repo_variable()}}}"'
        api_call = RemoteVersionController.I.api_method_input_args(
            endpoint=endpoint,
            method="PATCH",
            input_="-",
        )
        return f"""{self.repo_func()}() {{
  jq '.{repo_key}' {settings_path} | {api_call}
}}"""

    def rulesets_script(self) -> str:
        """Return the `rulesets` shell function as a multi-line string.

        Returns:
            Function definition that creates or updates each entry of the
            `rulesets` key of the settings file, using `POST` to create a
            ruleset or `PUT` to update one that already exists.
        """
        settings_path = RepositorySettingsConfigFile.I.path().as_posix()
        rulesets_key = RepositorySettingsConfigFile.I.rulesets_key()
        repo_ref = f"${{{self.repo_variable()}}}"
        endpoint_ref = "${endpoint}"
        id_ref = "${id}"
        ruleset_ref = "${ruleset}"
        ruleset_filter = ".[] | select(.name==$r.name) | .id"
        method_ref = "${method}"
        get_ruleset_id_call = RemoteVersionController.I.api_args(
            endpoint=f'"{endpoint_ref}"',
        )
        ruleset_call = RemoteVersionController.I.api_method_input_args(
            endpoint='"${url}"',
            method=f'"{method_ref}"',
            input_="-",
        )
        return rf"""{self.rulesets_func()}() {{
  local endpoint="repos/{repo_ref}/rulesets"
  jq --compact-output '.{rulesets_key}[]' {settings_path} | while read -r ruleset; do
    id=$({get_ruleset_id_call} \
      | jq --raw-output --argjson r "{ruleset_ref}" '{ruleset_filter}')
    if [[ -z {id_ref} ]]; then method="POST"; else method="PUT"; fi
    url="{endpoint_ref}${{id:+/{id_ref}}}"
    {ruleset_call} <<<"{ruleset_ref}"
  done
}}"""

    def dependency_alerts_func(self) -> str:
        """Return `"dependency_alerts"`, the function name."""
        return "dependency_alerts"

    def dependency_security_updates_func(self) -> str:
        """Return `"dependency_security_updates"`, the function name."""
        return "dependency_security_updates"

    def release_immutability_func(self) -> str:
        """Return `"release_immutability"`, the function name."""
        return "release_immutability"

    def repo_func(self) -> str:
        """Return `RepositorySettingsConfigFile.I.repo_key()`, the function name.

        Named identically to the settings file key it reads, so both stay
        in sync automatically.
        """
        return RepositorySettingsConfigFile.I.repo_key()

    def repo_variable(self) -> str:
        """Return `"GITHUB_REPOSITORY"`, the Actions variable holding `owner/repo`."""
        return "GITHUB_REPOSITORY"

    def rulesets_func(self) -> str:
        """Return `RepositorySettingsConfigFile.I.rulesets_key()`, the function name.

        Named identically to the settings file key it reads, so both stay
        in sync automatically.
        """
        return RepositorySettingsConfigFile.I.rulesets_key()
