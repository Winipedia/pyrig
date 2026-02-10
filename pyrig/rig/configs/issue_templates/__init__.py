"""GitHub issue template configuration management.

Manages GitHub issue templates in `.github/ISSUE_TEMPLATE/` directory:

- Bug report template (BUG-REPORT.yml)
- Feature request template (FEATURE-REQUEST.yml)
- Template chooser config (config.yml)

Templates are fetched from stevemao/github-issue-templates with fallback
to bundled resource files.

See Also:
    https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
    pyrig.rig.configs.base.yml.YmlConfigFile
"""
