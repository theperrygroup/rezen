"""Markdown extension to make tables collapsible by default.

This extension wraps rendered HTML ``<table>`` elements in a ``<details>`` block
with a ``<summary>`` label. This makes tables start collapsed in the static HTML
output (no JavaScript required), which avoids a flash of expanded tables on
initial page load.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape as html_escape
from html.parser import HTMLParser
from typing import Any, Optional
from xml.etree import ElementTree as etree

from markdown import Markdown
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor
from markdown.treeprocessors import Treeprocessor


def _as_bool(value: Any) -> bool:
    """Convert a config value to bool safely.

    Markdown extension configs sometimes arrive as strings (e.g., "false"),
    where ``bool("false")`` would incorrectly evaluate to True. This helper
    normalizes common string boolean values.

    Args:
        value: Raw config value.

    Returns:
        Parsed boolean value.
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}

    return bool(value)


class _CollapsibleTablesTreeprocessor(Treeprocessor):
    """Wrap HTML tables in a ``<details>`` element."""

    def __init__(
        self,
        md: Markdown,
        *,
        summary_text: str,
        open_by_default: bool,
        collapse_classed_tables: bool,
    ) -> None:
        """Initialize the processor.

        Args:
            md: Markdown instance.
            summary_text: Text to display in the details summary.
            open_by_default: Whether tables should be expanded by default.
            collapse_classed_tables: Whether to collapse tables that include a
                ``class`` attribute.
        """
        super().__init__(md)
        self._summary_text = summary_text
        self._open_by_default = open_by_default
        self._collapse_classed_tables = collapse_classed_tables

    def run(self, root: etree.Element) -> etree.Element:  # type: ignore[override]
        """Process the HTML element tree.

        Args:
            root: Root HTML element.

        Returns:
            The modified root element.
        """
        self._process_element(root, in_code_block=False, in_collapsible=False)
        return root

    def _process_element(
        self,
        element: etree.Element,
        *,
        in_code_block: bool,
        in_collapsible: bool,
    ) -> None:
        """Recursively process an element and its children."""
        next_in_code_block = in_code_block or self._is_code_like(element)
        next_in_collapsible = in_collapsible or self._is_rezen_collapsible(element)

        children = list(element)
        for idx, child in enumerate(children):
            if child.tag == "table" and self._should_wrap_table(
                child,
                in_code_block=next_in_code_block,
                in_collapsible=next_in_collapsible,
            ):
                details = self._wrap_table(child)

                # Preserve tail whitespace/text when replacing the node.
                details.tail, child.tail = child.tail, None

                element.remove(child)
                element.insert(idx, details)
                continue

            self._process_element(
                child,
                in_code_block=next_in_code_block,
                in_collapsible=next_in_collapsible,
            )

    @staticmethod
    def _class_list(element: etree.Element) -> list[str]:
        """Return a list of CSS classes for an element."""
        class_attr = (element.get("class") or "").strip()
        if not class_attr:
            return []
        return class_attr.split()

    def _is_code_like(self, element: etree.Element) -> bool:
        """Return True if the element represents a code block container."""
        if element.tag in {"pre", "code"}:
            return True

        classes = set(self._class_list(element))
        return bool(classes.intersection({"highlight", "codehilite", "linenodiv"}))

    def _is_rezen_collapsible(self, element: etree.Element) -> bool:
        """Return True if the element is already a ReZEN collapsible container."""
        if element.tag != "details":
            return False
        return "rezen-collapsible-table" in self._class_list(element)

    def _should_wrap_table(
        self,
        table: etree.Element,
        *,
        in_code_block: bool,
        in_collapsible: bool,
    ) -> bool:
        """Determine whether a table should be wrapped.

        Args:
            table: Table element.
            in_code_block: Whether the table is inside a code-like container.
            in_collapsible: Whether the table is already inside a collapsible
                container.

        Returns:
            True if the table should be wrapped; otherwise False.
        """
        if in_code_block or in_collapsible:
            return False

        classes = set(self._class_list(table))
        if "highlighttable" in classes:
            return False

        if not self._collapse_classed_tables and "class" in table.attrib:
            return False

        return True

    def _wrap_table(self, table: etree.Element) -> etree.Element:
        """Wrap a table in a ``<details>`` element and return the wrapper."""
        details = etree.Element("details")
        details.set("class", "rezen-collapsible-table")
        if self._open_by_default:
            details.set("open", "open")

        summary = etree.SubElement(details, "summary")
        summary.set("class", "rezen-collapsible-table__summary")
        summary.text = self._summary_text

        details.append(table)
        return details


@dataclass(frozen=True)
class _TagState:
    """State for an open HTML tag during streaming parse."""

    tag: str
    started_code_like: bool
    started_collapsible_table: bool


class _CollapsibleTablesHTMLRewriter(HTMLParser):
    """Rewrite an HTML fragment to wrap eligible tables with ``<details>``.

    Note:
        Python-Markdown stashes raw HTML blocks (e.g., mkdocstrings output) and
        reinserts them later. Treeprocessors do not see inside those blocks, so
        we also rewrite the final HTML string in a postprocessor.
    """

    def __init__(
        self,
        *,
        summary_text: str,
        open_by_default: bool,
        collapse_classed_tables: bool,
    ) -> None:
        """Initialize the rewriter.

        Args:
            summary_text: Text to display in the details summary.
            open_by_default: Whether tables should be expanded by default.
            collapse_classed_tables: Whether to collapse tables that include a
                ``class`` attribute.
        """
        super().__init__(convert_charrefs=False)
        self._summary_text = summary_text
        self._open_by_default = open_by_default
        self._collapse_classed_tables = collapse_classed_tables

        self._out: list[str] = []
        self._tag_stack: list[_TagState] = []
        self._wrapped_table_stack: list[bool] = []
        self._code_like_depth = 0
        self._collapsible_table_depth = 0

    def get_output(self) -> str:
        """Return the rewritten HTML."""
        return "".join(self._out)

    @staticmethod
    def _split_classes(class_attr: Optional[str]) -> set[str]:
        """Split a ``class`` attribute into a set of classes."""
        if not class_attr:
            return set()
        return {cls for cls in class_attr.split() if cls}

    def _is_code_like(self, tag: str, classes: set[str]) -> bool:
        """Return True if this tag should be treated as a code-like container."""
        if tag in {"pre", "code"}:
            return True
        return bool(classes.intersection({"highlight", "codehilite", "linenodiv"}))

    def _is_collapsible_details(self, tag: str, classes: set[str]) -> bool:
        """Return True if this tag is a ReZEN collapsible-table details."""
        return tag == "details" and "rezen-collapsible-table" in classes

    def _in_code_like(self) -> bool:
        return self._code_like_depth > 0

    def _in_collapsible_table(self) -> bool:
        return self._collapsible_table_depth > 0

    def _should_wrap_table(self, attrs: list[tuple[str, Optional[str]]]) -> bool:
        """Return True if the current ``<table>`` should be wrapped."""
        if self._in_code_like() or self._in_collapsible_table():
            return False

        attr_map = {k: v for k, v in attrs}
        classes = self._split_classes(attr_map.get("class"))
        if "highlighttable" in classes:
            return False

        if not self._collapse_classed_tables and "class" in attr_map:
            return False

        return True

    def _emit_details_open(self) -> None:
        """Emit the opening ``<details>`` and ``<summary>``."""
        if self._open_by_default:
            self._out.append('<details class="rezen-collapsible-table" open="open">')
        else:
            self._out.append('<details class="rezen-collapsible-table">')
        self._out.append('<summary class="rezen-collapsible-table__summary">')
        self._out.append(html_escape(self._summary_text))
        self._out.append("</summary>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        classes = self._split_classes(dict(attrs).get("class"))

        started_code_like = self._is_code_like(tag, classes)
        started_collapsible = self._is_collapsible_details(tag, classes)

        if started_code_like:
            self._code_like_depth += 1
        if started_collapsible:
            self._collapsible_table_depth += 1

        self._tag_stack.append(
            _TagState(
                tag=tag,
                started_code_like=started_code_like,
                started_collapsible_table=started_collapsible,
            )
        )

        if tag == "table":
            should_wrap = self._should_wrap_table(attrs)
            self._wrapped_table_stack.append(should_wrap)
            if should_wrap:
                self._emit_details_open()

        self._out.append(self.get_starttag_text() or f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        self._out.append(f"</{tag}>")

        if tag == "table":
            wrapped = self._wrapped_table_stack.pop() if self._wrapped_table_stack else False
            if wrapped:
                self._out.append("</details>")

        # Pop stack until we find the matching tag; adjust depth counters.
        while self._tag_stack:
            state = self._tag_stack.pop()
            if state.started_code_like:
                self._code_like_depth = max(0, self._code_like_depth - 1)
            if state.started_collapsible_table:
                self._collapsible_table_depth = max(
                    0, self._collapsible_table_depth - 1
                )
            if state.tag == tag:
                break

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, Optional[str]]]
    ) -> None:
        # Self-closing tables aren't expected, but handle them defensively.
        if tag == "table" and self._should_wrap_table(attrs):
            self._emit_details_open()
            self._out.append(self.get_starttag_text() or f"<{tag} />")
            self._out.append("</details>")
            return

        self._out.append(self.get_starttag_text() or f"<{tag} />")

    def handle_data(self, data: str) -> None:
        self._out.append(data)

    def handle_entityref(self, name: str) -> None:
        self._out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._out.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self._out.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self._out.append(f"<!{decl}>")


class _CollapsibleTablesPostprocessor(Postprocessor):
    """Postprocess HTML to wrap tables inside raw HTML blocks."""

    def __init__(
        self,
        md: Markdown,
        *,
        summary_text: str,
        open_by_default: bool,
        collapse_classed_tables: bool,
    ) -> None:
        """Initialize the postprocessor.

        Args:
            md: Markdown instance.
            summary_text: Text to display in the details summary.
            open_by_default: Whether tables should be expanded by default.
            collapse_classed_tables: Whether to collapse tables that include a
                ``class`` attribute.
        """
        super().__init__(md)
        self._summary_text = summary_text
        self._open_by_default = open_by_default
        self._collapse_classed_tables = collapse_classed_tables

    def run(self, text: str) -> str:  # type: ignore[override]
        """Rewrite the HTML output.

        Args:
            text: HTML fragment for the current page.

        Returns:
            The rewritten HTML fragment.
        """
        rewriter = _CollapsibleTablesHTMLRewriter(
            summary_text=self._summary_text,
            open_by_default=self._open_by_default,
            collapse_classed_tables=self._collapse_classed_tables,
        )
        rewriter.feed(text)
        rewriter.close()
        return rewriter.get_output()


class CollapsibleTablesExtension(Extension):
    """Markdown extension to render tables as collapsed-by-default details."""

    config = {
        "summary_text": ["Show table", "Summary label for each collapsed table"],
        "open_by_default": [False, "Whether tables should be open by default"],
        "collapse_classed_tables": [
            True,
            "Whether tables that include a class attribute should be collapsed",
        ],
    }

    def extendMarkdown(self, md: Markdown) -> None:
        """Register the extension with Markdown.

        Args:
            md: Markdown instance.
        """
        md.treeprocessors.register(
            _CollapsibleTablesTreeprocessor(
                md,
                summary_text=str(self.getConfig("summary_text")),
                open_by_default=_as_bool(self.getConfig("open_by_default")),
                collapse_classed_tables=_as_bool(self.getConfig("collapse_classed_tables")),
            ),
            "rezen-collapsible-tables",
            priority=2,
        )
        # Run after raw HTML has been reinserted so mkdocstrings tables are seen.
        md.postprocessors.register(
            _CollapsibleTablesPostprocessor(
                md,
                summary_text=str(self.getConfig("summary_text")),
                open_by_default=_as_bool(self.getConfig("open_by_default")),
                collapse_classed_tables=_as_bool(self.getConfig("collapse_classed_tables")),
            ),
            "rezen-collapsible-tables-post",
            priority=0,
        )


def makeExtension(**kwargs: Any) -> Extension:
    """Create the Markdown extension.

    Args:
        **kwargs: Markdown extension configuration.

    Returns:
        The configured Markdown extension.
    """
    return CollapsibleTablesExtension(**kwargs)

