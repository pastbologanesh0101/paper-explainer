"""Detect standard academic-paper section headers and split paper text
into a dict of {canonical_section_name: section_body_text}.
"""

import re

# Canonical section names, in the order they conventionally appear.
CANONICAL_ORDER = [
    "Abstract",
    "Introduction",
    "Related Work",
    "Methods",
    "Results",
    "Discussion",
    "Conclusion",
]

# Map from a variant header (lowercase, whitespace-normalized) to the
# canonical section name it belongs to.
_VARIANT_TO_CANONICAL = {
    "abstract": "Abstract",
    "summary": "Abstract",
    "introduction": "Introduction",
    "intro": "Introduction",
    "background": "Related Work",
    "related work": "Related Work",
    "related works": "Related Work",
    "literature review": "Related Work",
    "prior work": "Related Work",
    "methods": "Methods",
    "method": "Methods",
    "methodology": "Methods",
    "materials and methods": "Methods",
    "approach": "Methods",
    "experimental setup": "Methods",
    "results": "Results",
    "result": "Results",
    "results and analysis": "Results",
    "findings": "Results",
    "experiments": "Results",
    "experiments and results": "Results",
    "discussion": "Discussion",
    "analysis": "Discussion",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "concluding remarks": "Conclusion",
    "summary and conclusion": "Conclusion",
    "future work": "Conclusion",
}

# A header line looks like (optionally) a number/roman numeral prefix,
# then one of the known variant phrases, optionally followed by a colon,
# all on its own line.
_NUMBER_PREFIX = r"(?:(?:\d+|[IVXLC]+)[\.\)]\s*)?"

def _build_header_regex():
    # Longest phrases first so "related work" doesn't get shadowed by a
    # shorter accidental submatch, etc.
    phrases = sorted(_VARIANT_TO_CANONICAL.keys(), key=len, reverse=True)
    escaped = [re.escape(p) for p in phrases]
    pattern = (
        r"^\s*" + _NUMBER_PREFIX + r"(" + "|".join(escaped) + r")\s*:?\s*$"
    )
    return re.compile(pattern, re.IGNORECASE)


_HEADER_RE = _build_header_regex()


def is_section_header(line):
    """Return the canonical section name if `line` is a recognized
    section header, else None.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return None
    m = _HEADER_RE.match(stripped)
    if not m:
        return None
    return _VARIANT_TO_CANONICAL[m.group(1).lower()]


def split_sections(text):
    """Split raw paper text into sections.

    Returns an OrderedDict-like plain dict mapping canonical section name
    -> body text (str, leading/trailing whitespace stripped). Any text
    before the first recognized header is stored under "Title/Preamble".
    Sections that are never found are simply absent from the dict, so
    callers must handle missing sections gracefully.
    """
    lines = text.splitlines()
    sections = {}
    current_name = "Title/Preamble"
    buffer = []

    for line in lines:
        header = is_section_header(line)
        if header:
            # Flush whatever we were accumulating.
            body = "\n".join(buffer).strip()
            if body or current_name in sections:
                sections[current_name] = (
                    (sections.get(current_name, "") + "\n" + body).strip()
                    if current_name in sections
                    else body
                )
            elif current_name != "Title/Preamble":
                sections.setdefault(current_name, "")
            current_name = header
            buffer = []
        else:
            buffer.append(line)

    body = "\n".join(buffer).strip()
    if body:
        sections[current_name] = (
            (sections.get(current_name, "") + "\n" + body).strip()
            if current_name in sections
            else body
        )
    else:
        sections.setdefault(current_name, "")

    # Drop an empty preamble bucket.
    if sections.get("Title/Preamble", "") == "":
        sections.pop("Title/Preamble", None)

    return sections


def ordered_sections(sections):
    """Yield (name, body) pairs from a sections dict in canonical
    reading order, followed by any non-standard names at the end.
    """
    seen = set()
    for name in CANONICAL_ORDER:
        if name in sections:
            seen.add(name)
            yield name, sections[name]
    for name, body in sections.items():
        if name not in seen:
            yield name, body
