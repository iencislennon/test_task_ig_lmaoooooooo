"""Strip markdown noise out of a raw README so the LLM sees fewer wasted tokens."""

from __future__ import annotations

import re

_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_IMAGE_OR_BADGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
_HTML_TAG = re.compile(r"<[^>]+>")
_BLANK_RUN = re.compile(r"\n{3,}")
_HEADING = re.compile(r"^#{1,6}\s*(.+)$", re.MULTILINE)


def clean_readme(raw_text: str) -> str:
    """Remove badges, images, HTML comments/tags, and collapse blank lines."""
    text = _HTML_COMMENT.sub("", raw_text)
    text = _IMAGE_OR_BADGE.sub("", text)
    text = _HTML_TAG.sub("", text)
    text = _BLANK_RUN.sub("\n\n", text)
    return text.strip()


def extract_title(raw_text: str) -> str | None:
    """Return the first markdown heading in the README, if any."""
    match = _HEADING.search(raw_text)
    return match.group(1).strip() if match else None
