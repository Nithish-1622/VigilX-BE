from __future__ import annotations

import re
import unicodedata

# Regex for HTML tags
_HTML_TAG_RE = re.compile(r"<[^>]+>")
# Regex for redundant consecutive whitespace
_MULTIPLE_SPACES_RE = re.compile(r"[ \t]+")
# Regex for excess consecutive newlines
_MULTIPLE_NEWLINES_RE = re.compile(r"\n{3,}")


def clean_text(
    text: str,
    strip_html: bool = True,
    normalize_unicode: bool = True,
    fix_whitespace: bool = True,
) -> str:
    """
    Clean and normalize a single string text.

    - Removes HTML tags if strip_html is True.
    - Normalizes Unicode characters (NFC) if normalize_unicode is True.
    - Replaces non-printable control characters.
    - Trims leading/trailing whitespace and compresses consecutive spaces/newlines.
    """
    if not isinstance(text, str):
        text = str(text or "")

    # Strip null bytes and non-printable control chars except \n, \r, \t
    text = "".join(ch for ch in text if ch in ("\n", "\r", "\t") or (ord(ch) >= 32 and ord(ch) != 127))

    if normalize_unicode:
        text = unicodedata.normalize("NFC", text)

    if strip_html:
        text = _HTML_TAG_RE.sub(" ", text)

    if fix_whitespace:
        # Standardize curly quotes and special dashes
        text = (
            text.replace("“", '"')
            .replace("”", '"')
            .replace("‘", "'")
            .replace("’", "'")
            .replace("—", "-")
            .replace("–", "-")
        )
        text = _MULTIPLE_SPACES_RE.sub(" ", text)
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = _MULTIPLE_NEWLINES_RE.sub("\n\n", text)

    return text.strip()


def clean_dataset_rows(
    rows: list[dict[str, str]],
    strip_html: bool = True,
    normalize_unicode: bool = True,
    fix_whitespace: bool = True,
) -> list[dict[str, str]]:
    """
    Apply text cleaning to all prompt and completion fields in a list of row dicts.
    """
    cleaned_rows: list[dict[str, str]] = []
    for row in rows:
        cleaned_row = dict(row)
        if "prompt" in cleaned_row:
            cleaned_row["prompt"] = clean_text(
                cleaned_row["prompt"],
                strip_html=strip_html,
                normalize_unicode=normalize_unicode,
                fix_whitespace=fix_whitespace,
            )
        if "completion" in cleaned_row:
            cleaned_row["completion"] = clean_text(
                cleaned_row["completion"],
                strip_html=strip_html,
                normalize_unicode=normalize_unicode,
                fix_whitespace=fix_whitespace,
            )
        cleaned_rows.append(cleaned_row)
    return cleaned_rows
