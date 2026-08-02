"""module."""

from pathlib import Path

from pyrig.rig.configs.docs.builder import DocsBuilderConfigFile


class TestDocsBuilderConfigFile:
    """Test class."""

    def test_stem(self) -> None:
        """Test method."""
        assert DocsBuilderConfigFile.I.stem() == "zensical"

    def test_parent_path(self) -> None:
        """Test method."""
        parent_path = DocsBuilderConfigFile.I.parent_path()
        assert parent_path == Path()

    def test__configs(self) -> None:
        """Test method."""
        configs = DocsBuilderConfigFile.I.configs()
        assert isinstance(configs, dict)
        project = configs["project"]
        assert isinstance(project["site_name"], str)
        assert project["site_name"]
        assert isinstance(project["site_description"], str)
        assert project["site_description"]
        assert project["site_url"].startswith("https://")
        assert project["repo_url"].startswith("https://github.com/")
        assert project["edit_uri"] == "edit/main/docs"
        assert project["validation"] == {
            "shadowed_definitions": True,
            "shadowed_footnotes": True,
            "unresolved_footnotes": True,
            "unresolved_references": True,
            "unused_definitions": True,
            "unused_footnotes": True,
        }
        assert project["theme"]["features"] == [
            "content.action.edit",
            "content.action.view",
            "content.code.annotate",
            "content.code.copy",
            "content.code.select",
            "content.footnote.tooltips",
            "content.tabs.link",
            "content.tooltips",
            "navigation.expand",
            "navigation.footer",
            "navigation.indexes",
            "navigation.instant",
            "navigation.instant.prefetch",
            "navigation.instant.preview",
            "navigation.instant.progress",
            "navigation.path",
            "navigation.prune",
            "navigation.sections",
            "navigation.top",
            "navigation.tracking",
            "search.highlight",
            "toc.follow",
        ]
        assert project["theme"]["palette"] == [
            {
                "media": "(prefers-color-scheme: light)",
                "scheme": "default",
                "toggle": {
                    "icon": "lucide/sun",
                    "name": "Switch to dark mode",
                },
            },
            {
                "media": "(prefers-color-scheme: dark)",
                "scheme": "slate",
                "toggle": {
                    "icon": "lucide/moon",
                    "name": "Switch to light mode",
                },
            },
        ]
        handler = project["plugins"]["mkdocstrings"]["handlers"]["python"]
        assert handler["paths"] == ["src"]
        assert handler["inventories"] == ["https://docs.python.org/3/objects.inv"]
        assert handler["options"] == {
            # `filters` is added by pyrig's own `pyrig-overrides` package,
            # which `.I` resolves to in this repo: it disables mkdocstrings'
            # default single-underscore member filter so that methods like
            # `_configs()` — pyrig's own subclassing surface — appear in the
            # API reference.
            "filters": [],
            "backlinks": "tree",
            "docstring_options": {
                "ignore_init_summary": True,
            },
            "docstring_section_style": "list",
            "inherited_members": True,
            "members": True,
            "merge_init_into_class": True,
            "parameter_headings": True,
            "relative_crossrefs": True,
            "scoped_crossrefs": True,
            "separate_signature": True,
            "show_root_heading": True,
            "show_signature_annotations": True,
            "show_signature_type_parameters": True,
            "show_submodules": True,
            "show_symbol_type_heading": True,
            "show_symbol_type_toc": True,
            "signature_crossrefs": True,
            "type_parameter_headings": True,
        }
