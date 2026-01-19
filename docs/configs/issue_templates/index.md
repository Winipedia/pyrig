# Issue Templates Configuration

GitHub issue templates that provide structured forms for bug reports and feature
requests.

## Overview

Issue templates are YAML files in `.github/ISSUE_TEMPLATE/` that create
interactive forms when users open new issues on GitHub. They ensure consistent,
actionable issue reports.

## Files

| File | Description |
|------|-------------|
| [bug_report.yml](bug_report.md) | Bug report template with reproduction steps |
| [feature_request.yml](feature_request.md) | Feature request template |
| [config.yml](config.md) | Template chooser configuration |

## Location

All files are placed in `.github/ISSUE_TEMPLATE/`:

```text
.github/
└── ISSUE_TEMPLATE/
    ├── bug_report.yml
    ├── feature_request.yml
    └── config.yml
```

## How It Works

When a user clicks "New Issue" on your GitHub repository:

1. GitHub reads the templates from `.github/ISSUE_TEMPLATE/`
2. Displays a template chooser (if multiple templates exist)
3. User selects a template
4. GitHub renders the YAML form fields as an interactive web form
5. User fills in the form and submits

## Template Design

Minimal, generic templates that work for any project type.

## Automatic Creation

```bash
uv run pyrig mkroot
```

This creates all three template files in `.github/ISSUE_TEMPLATE/`.

## Customization

Each template can be customized by editing the generated YAML files. The
validation only checks that the files exist and are non-empty, allowing full
customization.

## See Also

- [GitHub Docs: Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
