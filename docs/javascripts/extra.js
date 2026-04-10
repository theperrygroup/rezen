// Extra JavaScript for ReZEN Documentation

/**
 * Initialize collapsible tables in the rendered documentation.
 *
 * This wraps tables (or Material's `.md-typeset__table` wrapper) in a `<details>`
 * element so they start collapsed by default.
 */
function initCollapsibleTables() {
  const contentRoot = document.querySelector(".md-content");
  if (!contentRoot) {
    return;
  }

  // Prefer wrapping Material's responsive table wrapper when present.
  const tableWrappers = contentRoot.querySelectorAll(".md-typeset__table");
  tableWrappers.forEach((wrapper) => {
    if (wrapper.closest("details.rezen-collapsible-table")) {
      return;
    }

    // Only collapse "plain" Markdown tables (no explicit class attribute).
    const table = wrapper.querySelector("table");
    if (!table || table.classList.length > 0) {
      return;
    }

    const details = document.createElement("details");
    details.className = "rezen-collapsible-table";

    const summary = document.createElement("summary");
    summary.className = "rezen-collapsible-table__summary";
    summary.textContent = "Show table";

    details.appendChild(summary);
    wrapper.parentNode.insertBefore(details, wrapper);
    details.appendChild(wrapper);
  });

  // Fallback: wrap any tables not already wrapped by `.md-typeset__table`.
  const tables = contentRoot.querySelectorAll(".md-typeset table:not([class])");
  tables.forEach((table) => {
    if (table.closest("details.rezen-collapsible-table")) {
      return;
    }

    // Avoid wrapping any syntax-highlighting/internal tables.
    if (
      table.classList.contains("highlighttable") ||
      table.closest(".highlight, .codehilite, pre")
    ) {
      return;
    }

    const details = document.createElement("details");
    details.className = "rezen-collapsible-table";

    const summary = document.createElement("summary");
    summary.className = "rezen-collapsible-table__summary";
    summary.textContent = "Show table";

    details.appendChild(summary);
    table.parentNode.insertBefore(details, table);
    details.appendChild(table);
  });
}

/**
 * Initialize documentation enhancements.
 *
 * Material for MkDocs uses instant navigation which replaces page content
 * without a full reload. When available, hook into `document$.subscribe`.
 */
function initRezenDocs() {
  initCollapsibleTables();
}

// Material for MkDocs (navigation.instant) hook
if (window.document$ && typeof window.document$.subscribe === "function") {
  window.document$.subscribe(initRezenDocs);
} else {
  document.addEventListener("DOMContentLoaded", initRezenDocs);
}

// Run once for the initial page load (in case `document$` already emitted).
initRezenDocs();
