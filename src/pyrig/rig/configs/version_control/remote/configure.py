"""Shell script that applies repository configuration via the GitHub CLI."""

from pathlib import Path

from pyrig.rig.configs.base.shell import ShellConfigFile
from pyrig.rig.configs.version_control.remote.settings import (
    RepositorySettingsConfigFile,
)
from pyrig.rig.tools.version_control.remote.controller import (
    RemoteVersionController,
)


class ConfigureRepositoryConfigFile(ShellConfigFile):
    """Configuration file for `.github/configure.sh`.

    Defines shell functions that read `.github/settings.json` and apply its
    contents to the repository via the GitHub CLI, plus a function that
    enables GitHub's private vulnerability reporting feature. The script is
    meant to be invoked directly rather than sourced as a library: running
    it runs every function it defines.

    Every function calls `gh api` against this repository directly, so only
    a token accepted by `gh` (`GH_TOKEN` or `GITHUB_TOKEN`) needs to already
    be set in the environment.
    """

    def script(self) -> str:
        """Return the required shell script content, below the shared header.

        Returns:
            The shared setup code, the `settings`, `rulesets`, and
            `vulnerability_reporting` shell function definitions, and
            the trailing block that runs every function.
        """
        return f"""{self.global_content()}

{self.scripts_content()}

{self.footer_content()}
"""

    def parent_path(self) -> Path:
        """Return the `RemoteVersionController`'s config directory."""
        return RemoteVersionController.I.config_dir()

    def stem(self) -> str:
        """Return `"configure"`."""
        return "configure"

    def scripts_content(self) -> str:
        """Return the content of all scripts defined in this file.

        Returns:
            The concatenation of every script returned by `scripts()`.
        """
        return "\n\n".join(self.scripts())

    def scripts(self) -> tuple[str, ...]:
        """Return the shell function definitions that make up the script."""
        return (
            self.repository_settings_script(),
            self.rulesets_script(),
            self.vulnerability_reporting_script(),
        )

    def repository_settings_script(self) -> str:
        """Return the `settings` shell function as a multi-line string.

        Returns:
            Function definition that pipes the `repository` key of the
            settings file into `gh api` as a `PATCH` request.
        """
        settings_path = RepositorySettingsConfigFile.I.path().as_posix()
        repository_key = RepositorySettingsConfigFile.I.repository_key()
        endpoint = f'"repos/${{{self.repo_variable()}}}"'
        api_call = RemoteVersionController.I.api_method_input_args(
            endpoint=endpoint,
            method="PATCH",
            input_="-",
        )
        return f"""{self.repository_settings_function()}() {{
  jq '.{repository_key}' {settings_path} | {api_call}
}}"""

    def repository_settings_function(self) -> str:
        """Return `"settings"`, the function name."""
        return "settings"

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
        return rf"""{self.rulesets_function()}() {{
  local endpoint="repos/{repo_ref}/rulesets"
  jq --compact-output '.{rulesets_key}[]' {settings_path} | while read -r ruleset; do
    id=$({get_ruleset_id_call} \
      | jq --raw-output --argjson r "{ruleset_ref}" '{ruleset_filter}')
    if [[ -z {id_ref} ]]; then method="POST"; else method="PUT"; fi
    url="{endpoint_ref}${{id:+/{id_ref}}}"
    {ruleset_call} <<<"{ruleset_ref}"
  done
}}"""

    def rulesets_function(self) -> str:
        """Return `"rulesets"`, the function name."""
        return "rulesets"

    def vulnerability_reporting_script(self) -> str:
        """Return the `vulnerability_reporting` shell function.

        Returns:
            Function definition that `PUT`s the GitHub API endpoint that
            enables private vulnerability reporting for the repository.
        """
        endpoint = (
            f'"repos/${{{self.repo_variable()}}}/private-vulnerability-reporting"'
        )
        api_call = RemoteVersionController.I.api_method_args(
            endpoint=endpoint,
            method="PUT",
        )
        return f"""{self.vulnerability_reporting_function()}() {{
  {api_call}
}}"""

    def vulnerability_reporting_function(self) -> str:
        """Return `"vulnerability_reporting"`, the function name."""
        return "vulnerability_reporting"

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

    def global_content(self) -> str:
        """Return the content defined outside any function, shared by all of them.

        Defined once at the top of the script rather than inside each
        function for reuse. Any other variable or setup shared across functions in
        the future would also be returned here.

        Returns:
            Currently just the `repo_variable()` variable assignment.
        """
        return f'{self.repo_variable()}="{RemoteVersionController.I.repository()}"'

    def repo_variable(self) -> str:
        """Return `"repo"`, the shell variable name holding `owner/repo`."""
        return "repo"
