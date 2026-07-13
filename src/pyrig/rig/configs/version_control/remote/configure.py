"""Shell script that applies repository settings and rulesets via the GitHub CLI."""

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
    contents to the repository via the GitHub CLI. The release workflow
    runs this script directly, passing the function it needs as an
    argument (e.g. `bash .github/configure.sh settings`), rather than
    embedding the shell logic directly in the workflow YAML.

    Both functions call `gh api` against this repository directly, so only a
    token accepted by `gh` (`GH_TOKEN` or `GITHUB_TOKEN`) needs to already be
    set in the environment.
    """

    def script_content(self) -> str:
        """Return the required shell script content, below the shared header.

        Returns:
            The shared setup code, the `settings` and `rulesets` shell
            function definitions, and the trailing dispatch line that lets
            the script be run directly.
        """
        return f"""{self.global_content()}

{self.apply_repository_settings_script()}

{self.apply_rulesets_script()}

{self.footer_content()}
"""

    def parent_path(self) -> Path:
        """Return `Path(".github")`."""
        return Path(".github")

    def stem(self) -> str:
        """Return `"configure"`."""
        return "configure"

    def apply_repository_settings_script(self) -> str:
        """Return the `settings` shell function as a multi-line string.

        Returns:
            Function definition that pipes the `repository` key of the
            settings file into `gh api` as a `PATCH` request.
        """
        settings_path = RepositorySettingsConfigFile.I.path().as_posix()
        repository_key = RepositorySettingsConfigFile.I.repository_key()
        endpoint = f"repos/${{{self.repo_variable()}}}"
        return f"""{self.apply_repository_settings_function()}() {{
  jq '.{repository_key}' {settings_path} | gh api "{endpoint}" -X PATCH --input -
}}"""

    def apply_repository_settings_function(self) -> str:
        """Return `"settings"`, the function name."""
        return "settings"

    def apply_rulesets_script(self) -> str:
        """Return the `rulesets` shell function as a multi-line string.

        Returns:
            Function definition that upserts each entry of the `rulesets`
            key of the settings file, using `POST` to create a ruleset or
            `PUT` to update one that already exists.
        """
        settings_path = RepositorySettingsConfigFile.I.path().as_posix()
        rulesets_key = RepositorySettingsConfigFile.I.rulesets_key()
        repo_ref = f"${{{self.repo_variable()}}}"
        endpoint_ref = "${endpoint}"
        id_ref = "${id}"
        ruleset_ref = "${ruleset}"
        method_ref = "${method}"
        return f"""{self.apply_rulesets_function()}() {{
  local endpoint="repos/{repo_ref}/rulesets"
  jq -c '.{rulesets_key}[]' {settings_path} | while read -r ruleset; do
    id=$(gh api "{endpoint_ref}" |
      jq -r --argjson r "{ruleset_ref}" '.[] | select(.name==$r.name) | .id')
    if [[ -z "{id_ref}" ]]; then method="POST"; else method="PUT"; fi
    url="{endpoint_ref}${{id:+/{id_ref}}}"
    gh api "${{url}}" -X "{method_ref}" --input - <<<"{ruleset_ref}"
  done
}}"""

    def apply_rulesets_function(self) -> str:
        """Return `"rulesets"`, the function name."""
        return "rulesets"

    def footer_content(self) -> str:
        """Return the line that invokes the function named by the script's arguments.

        Placed at the end of the script, after every function is defined.
        Lets the script be run directly, e.g. `bash configure.sh settings`,
        instead of requiring it to be sourced first.

        Returns:
            `'"$@"'`.
        """
        return '"$@"'

    def global_content(self) -> str:
        """Return the content defined outside any function, shared by all of them.

        Defined once at the top of the script rather than inside each
        function, since both `settings()` and `rulesets()` reference the
        `repo_variable()` variable. Any other variable or setup shared
        across functions in the future would also be returned here.

        Returns:
            Currently just the `repo_variable()` variable assignment.
        """
        return f'{self.repo_variable()}="{RemoteVersionController.I.repository()}"'

    def repo_variable(self) -> str:
        """Return `"repo"`, the shell variable name holding `owner/repo`."""
        return "repo"
