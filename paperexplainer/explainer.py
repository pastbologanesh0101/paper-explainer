"""Top-level orchestration: turn raw paper text into a structured,
plain-language explanation. Ties together section detection, acronym
expansion, extractive scoring, jargon simplification, and the
contribution / numeric-result extractors.
"""

from .acronyms import expand_acronyms, find_acronym_definitions
from .extraction import extract_contribution_statements, extract_numeric_results
from .jargon import plain_language_pass
from .scoring import top_sentences
from .sections import ordered_sections, split_sections


def explain_paper(text, sentences_per_section=3, max_words=25):
    """Build a full explanation of a paper's plain text.

    Returns a dict:
      {
        "acronyms": {ACRONYM: full_term, ...},
        "contribution": [sentence, ...],
        "numeric_results": [{"sentence", "numbers", "section"}, ...],
        "sections": {
            section_name: {
                "key_sentences": [original top sentences, ...],
                "plain_sentences": [rewritten sentences, ...],
            },
            ...
        },
      }
    """
    acronym_definitions = find_acronym_definitions(text)
    expanded_text = expand_acronyms(text, acronym_definitions)

    sections = split_sections(expanded_text)

    contribution = extract_contribution_statements(sections)
    numeric_results = extract_numeric_results(sections)

    section_output = {}
    for name, body in ordered_sections(sections):
        if name == "Title/Preamble":
            continue
        if not body:
            continue
        key_sentences = top_sentences(body, n=sentences_per_section)
        plain_sentences = []
        for sentence in key_sentences:
            pieces, _subs = plain_language_pass(sentence, max_words=max_words)
            plain_sentences.extend(pieces)
        section_output[name] = {
            "key_sentences": key_sentences,
            "plain_sentences": plain_sentences,
        }

    return {
        "acronyms": acronym_definitions,
        "contribution": contribution,
        "numeric_results": numeric_results,
        "sections": section_output,
    }


def format_explanation(explanation, paper_title=None):
    """Render the explanation dict returned by explain_paper() as a
    human-readable plain-text report (what the CLI prints).
    """
    lines = []
    title = paper_title or "Paper Explanation"
    lines.append("=" * len(title))
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")

    if explanation["contribution"]:
        lines.append("STATED CONTRIBUTION / CLAIM")
        lines.append("-" * 27)
        for sentence in explanation["contribution"]:
            lines.append("- " + sentence)
        lines.append("")
    else:
        lines.append("STATED CONTRIBUTION / CLAIM")
        lines.append("-" * 27)
        lines.append("(No explicit contribution statement detected.)")
        lines.append("")

    if explanation["numeric_results"]:
        lines.append("NUMERIC RESULTS FOUND")
        lines.append("-" * 22)
        for item in explanation["numeric_results"]:
            numbers = ", ".join(item["numbers"])
            lines.append(
                "- [{}] {} (numbers: {})".format(
                    item["section"], item["sentence"], numbers
                )
            )
        lines.append("")
    else:
        lines.append("NUMERIC RESULTS FOUND")
        lines.append("-" * 22)
        lines.append("(No numeric results detected.)")
        lines.append("")

    if explanation["acronyms"]:
        lines.append("ACRONYMS DETECTED")
        lines.append("-" * 18)
        for acronym, full_term in explanation["acronyms"].items():
            lines.append("- {} = {}".format(acronym, full_term))
        lines.append("")

    lines.append("PLAIN-LANGUAGE EXPLANATION BY SECTION")
    lines.append("-" * 38)
    if not explanation["sections"]:
        lines.append(
            "(No standard sections were detected in this paper. "
            "Check that it uses headers like 'Abstract', 'Introduction', "
            "'Methods', 'Results', 'Conclusion'.)"
        )
    for name, data in explanation["sections"].items():
        lines.append("")
        lines.append("## " + name)
        for sentence in data["plain_sentences"]:
            lines.append("  " + sentence)

    return "\n".join(lines)
