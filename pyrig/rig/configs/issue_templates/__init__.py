"""GitHub issue template configuration management.

Manages GitHub issue templates in `.github/ISSUE_TEMPLATE/` directory:

- Bug report template (bug_report.yml)
- Feature request template (feature_request.yml)
- Template chooser config (config.yml)

Templates are fetched from stevemao/github-issue-templates with fallback
to bundled resource files.

See Also:
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
    pyrig.rig.configs.base.yml.YmlConfigFile
"""
