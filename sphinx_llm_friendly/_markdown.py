from __future__ import annotations

from pathlib import Path
from types import MethodType
from typing import TYPE_CHECKING

from ._llm import prepare_doctree_for_llm
from ._translator import MarkdownTranslator

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.application import Sphinx
    from sphinx.builders.html import StandaloneHTMLBuilder


def write_markdown(app: Sphinx, docname: str, doctree: nodes.document) -> None:
    """Write the Markdown version of *docname* next to its HTML version."""
    doctree = prepare_doctree_for_llm(doctree)
    builder: StandaloneHTMLBuilder = app.builder  # type: ignore[assignment]
    translator = MarkdownTranslator(doctree, builder)
    handlers = app.registry.translation_handlers.get("llm_markdown", {})
    for name, (visit, depart) in handlers.items():
        setattr(translator, f"visit_{name}", MethodType(visit, translator))
        if depart:
            setattr(translator, f"depart_{name}", MethodType(depart, translator))
    doctree.walkabout(translator)
    page = Path(app.outdir, f"{docname}.md")
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(translator.astext(), encoding="utf-8")
