# MkdocsConfigFile

## Overview

**File Location:** `mkdocs.yml`
**ConfigFile Class:** `MkdocsConfigFile`
**File Type:** YAML configuration
**Priority:** Standard

Configuration file for MkDocs documentation generator. Defines site metadata, navigation structure, and plugins for building documentation websites.

## Purpose

The `mkdocs.yaml` file configures MkDocs documentation:

- **Site Metadata** - Project name and description
- **Navigation Structure** - Documentation menu and page organization
- **Plugins** - Search, Mermaid diagrams, and other extensions
- **Theme Configuration** - Documentation appearance and features

### Why pyrig manages this file

pyrig creates a minimal MkDocs configuration that works out of the box with the documentation structure created by pyrig. The configuration is designed to be extended by users while maintaining compatibility with pyrig's documentation system.

## File Format

YAML configuration with MkDocs-specific structure:

```yaml
site_name: my-project
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - API Reference: api/
plugins:
  - search
  - mermaid2
theme:
  name: material
```

## Default Configuration

Pyrig creates a minimal configuration:

**File location:** `mkdocs.yml`

**File contents:**
```yaml
site_name: pyrig
nav:
- Home: index.md
plugins:
- search
- mermaid2
```

### Configuration Breakdown

#### `site_name`
**Type:** String  
**Default:** Project name from `pyproject.toml`  
**Purpose:** Sets the documentation site title

#### `nav`
**Type:** List of navigation items  
**Default:** `[{"Home": "index.md"}]`  
**Purpose:** Defines the documentation navigation menu

**Structure:**
- Simple page: `- Page Title: page.md`
- Section with pages: `- Section: [page1.md, page2.md]`
- Nested sections: Use indentation

#### `plugins`
**Type:** List of plugin names  
**Default:** `["search", "mermaid2"]`  
**Purpose:** Enables MkDocs plugins

**Included plugins:**
- `search` - Full-text search functionality
- `mermaid2` - Mermaid diagram rendering

## How to Customize

### Adding Pages to Navigation

Edit the `nav` section:

```yaml
nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - User Guide:
      - Installation: guide/installation.md
      - Configuration: guide/configuration.md
  - API Reference: api/
  - About: about.md
```

### Adding a Theme

Install and configure a theme (e.g., Material for MkDocs):

```bash
uv add mkdocs-material --group dev
```

```yaml
theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
  features:
    - navigation.tabs
    - navigation.sections
```

### Adding More Plugins

Install plugins and add to configuration:

```bash
uv add mkdocs-awesome-pages-plugin --group dev
```

```yaml
plugins:
  - search
  - mermaid2
  - awesome-pages
```

### Site Metadata

Add more metadata:

```yaml
site_name: My Project
site_description: A comprehensive guide to my project
site_author: Your Name
site_url: https://myproject.readthedocs.io
repo_url: https://github.com/username/myproject
repo_name: username/myproject
```

## Building Documentation

### Local Preview

Serve documentation locally with live reload:

```bash
mkdocs serve
```

Visit `http://127.0.0.1:8000/` to view the documentation.

### Build Static Site

Generate static HTML:

```bash
mkdocs build
```

Output is in `site/` directory.

### Deploy to GitHub Pages

```bash
mkdocs gh-deploy
```

## Common MkDocs Plugins

### Essential Plugins

- **search** - Full-text search (included by default)
- **mermaid2** - Mermaid diagram support (included by default)
- **awesome-pages** - Automatic navigation from directory structure
- **minify** - Minify HTML/CSS/JS for production

### Documentation Enhancement

- **mkdocstrings** - Auto-generate API docs from docstrings
- **git-revision-date-localized** - Show last update dates
- **macros** - Jinja2 templating in Markdown
- **include-markdown** - Include external Markdown files

## Related Files

- **`docs/index.md`** - Documentation homepage ([docs-index.md](docs-index.md))
- **`docs/`** - Documentation directory
- **`pyproject.toml`** - Project metadata source ([pyproject.md](pyproject.md))

## Common Issues

### Issue: `mermaid2` plugin not found

**Cause:** Plugin not installed

**Solution:**
```bash
uv add mkdocs-mermaid2-plugin --group dev
```

### Issue: Navigation not showing all pages

**Cause:** Pages not listed in `nav` section

**Solution:** Either add pages to `nav` or use the `awesome-pages` plugin for automatic navigation.

### Issue: Theme not found

**Cause:** Theme package not installed

**Solution:**
```bash
# For Material theme
uv add mkdocs-material --group dev
```

## See Also

- [MkDocs Documentation](https://www.mkdocs.org/) - Official MkDocs guide
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - Popular theme
- [docs/index.md](docs-index.md) - Documentation index configuration
- [Getting Started Guide](../getting-started.md) - Initial project setup

