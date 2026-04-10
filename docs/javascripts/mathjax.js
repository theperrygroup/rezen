// MathJax configuration for ReZEN documentation.
//
// This file is loaded before the MathJax CDN script, so configuration must be
// defined on `window.MathJax` ahead of time.

window.MathJax = {
  tex: {
    inlineMath: [
      ["\\(", "\\)"],
      ["$", "$"],
    ],
    displayMath: [
      ["\\[", "\\]"],
      ["$$", "$$"],
    ],
    processEscapes: true,
  },
  options: {
    processHtmlClass: "arithmatex",
  },
};

(function () {
  function typeset() {
    if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
      window.MathJax.typesetPromise();
    }
  }

  // Material for MkDocs (navigation.instant) hook
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(typeset);
  } else {
    document.addEventListener("DOMContentLoaded", typeset);
  }
})();

