"""Detect acronym-definition patterns like "Support Vector Machine (SVM)"
and expand the acronym's first later standalone use back into the full
term, so a reader doesn't have to scroll back to find the definition.
"""

import re

# "Some Capitalized Phrase (ACRONYM)" where the phrase is 1-6 words.
_DEFINITION_RE = re.compile(
    r"\b((?:[A-Z][a-zA-Z']*(?:[\s-]+)){0,5}[A-Z][a-zA-Z']*)\s*\(([A-Z]{2,6})\)"
)


def _looks_like_valid_acronym(full_term, acronym):
    """Cheap sanity check: the acronym's first letter should match the
    full term's first letter, and the full term should have at least as
    many significant words as roughly justifies the acronym length.
    """
    words = full_term.split()
    if not words:
        return False
    if words[0][0].upper() != acronym[0].upper():
        return False
    return len(words) >= 1


def find_acronym_definitions(text):
    """Scan `text` for "Full Term (ACRONYM)" definitions.

    Returns a dict mapping ACRONYM -> full term, in order of first
    appearance (Python dicts preserve insertion order).
    """
    definitions = {}
    for match in _DEFINITION_RE.finditer(text):
        full_term, acronym = match.group(1).strip(), match.group(2)
        if acronym in definitions:
            continue
        if not _looks_like_valid_acronym(full_term, acronym):
            continue
        definitions[acronym] = full_term
    return definitions


def expand_acronyms(text, definitions=None):
    """Replace the first standalone use of each defined acronym that
    occurs AFTER its defining "Full Term (ACRONYM)" span with the full
    term, so at least one later mention is spelled out in plain
    language. Earlier/defining occurrences are left untouched.

    Returns the rewritten text.
    """
    if definitions is None:
        definitions = find_acronym_definitions(text)
    if not definitions:
        return text

    result = text
    for acronym, full_term in definitions.items():
        # Find where the definition itself sits, so we only touch
        # occurrences after it.
        def_match = re.search(
            re.escape(full_term) + r"\s*\(" + re.escape(acronym) + r"\)",
            result,
        )
        search_start = def_match.end() if def_match else 0

        standalone_re = re.compile(r"\b" + re.escape(acronym) + r"\b")
        later_match = standalone_re.search(result, search_start)
        if later_match:
            result = (
                result[: later_match.start()]
                + full_term
                + result[later_match.end():]
            )

    return result
