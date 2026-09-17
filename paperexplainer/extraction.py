"""Pattern-matching extraction of (1) the paper's stated contribution/
claim and (2) numeric results mentioned in the paper. No ML, just regex
and keyword proximity.
"""

import re

from .textutils import split_sentences

CONTRIBUTION_PATTERNS = [
    r"\bwe propose\b",
    r"\bwe present\b",
    r"\bwe introduce\b",
    r"\bwe show\b",
    r"\bwe demonstrate\b",
    r"\bwe develop\b",
    r"\bwe design\b",
    r"\bour contribution\b",
    r"\bour main contribution\b",
    r"\bour key contribution\b",
    r"\bthis paper proposes\b",
    r"\bthis paper presents\b",
    r"\bthis paper introduces\b",
    r"\bthis work proposes\b",
    r"\bthis work presents\b",
    r"\bin this paper, we\b",
    r"\bin this work, we\b",
]

_CONTRIBUTION_RE = re.compile("|".join(CONTRIBUTION_PATTERNS), re.IGNORECASE)

RESULT_KEYWORDS = [
    "accuracy", "precision", "recall", "f1", "f-score", "auc", "bleu",
    "rouge", "error rate", "error", "loss", "latency", "throughput",
    "speedup", "improvement", "increase", "decrease", "reduction",
    "outperform", "outperforms", "outperformed", "significant",
    "p-value", "p <", "p<", "p =", "confidence interval", "baseline",
]

# Percentages, "p < 0.05"-style significance values, "Nx" speedups, and
# plain decimal/integer numbers.
_PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
_PVALUE_RE = re.compile(r"\bp\s*[<>=]\s*0?\.\d+")
_MULTIPLIER_RE = re.compile(r"\b\d+(?:\.\d+)?x\b", re.IGNORECASE)
_PLAIN_NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")

_NUMBER_PATTERNS = [_PERCENT_RE, _PVALUE_RE, _MULTIPLIER_RE]


def extract_contribution_statements(sections):
    """Search the Abstract and Introduction (falling back to any other
    available section, in canonical order, if neither is present) for
    sentences that state the paper's contribution or claim.

    Returns a list of matching sentences (original wording, deduplicated,
    in order of appearance). May be empty if no pattern matches.
    """
    search_order = ["Abstract", "Introduction"]
    fallback_order = [
        "Related Work", "Methods", "Results", "Discussion", "Conclusion",
    ]

    found = []
    seen = set()

    def scan(section_names):
        for name in section_names:
            body = sections.get(name)
            if not body:
                continue
            for sentence in split_sentences(body):
                if _CONTRIBUTION_RE.search(sentence) and sentence not in seen:
                    seen.add(sentence)
                    found.append(sentence)

    scan(search_order)
    if not found:
        scan(fallback_order)

    return found


def _numbers_in_sentence(sentence):
    numbers = []
    for pattern in _NUMBER_PATTERNS:
        numbers.extend(pattern.findall(sentence))
    return numbers


def _has_result_keyword(sentence_lower):
    return any(kw in sentence_lower for kw in RESULT_KEYWORDS)


def extract_numeric_results(sections):
    """Find sentences that report numeric results: percentages,
    p-values, "Nx" speedups, or plain numbers that sit alongside a
    result-indicating keyword (e.g. "accuracy", "improvement").

    Searches Results and Discussion first (the conventional home for
    numbers), then falls back to the whole paper if those sections are
    absent.

    Returns a list of dicts: {"sentence": str, "numbers": [str, ...],
    "section": str}.
    """
    search_order = ["Results", "Discussion", "Abstract", "Conclusion"]
    results = []
    seen_sentences = set()

    def scan(section_names):
        for name in section_names:
            body = sections.get(name)
            if not body:
                continue
            for sentence in split_sentences(body):
                if sentence in seen_sentences:
                    continue
                numbers = _numbers_in_sentence(sentence)
                sentence_lower = sentence.lower()
                if not numbers:
                    # Also accept a plain number if it sits next to a
                    # result keyword in the same sentence.
                    plain_numbers = _PLAIN_NUMBER_RE.findall(sentence)
                    if plain_numbers and _has_result_keyword(sentence_lower):
                        numbers = plain_numbers
                if numbers:
                    seen_sentences.add(sentence)
                    results.append(
                        {"sentence": sentence, "numbers": numbers, "section": name}
                    )

    scan(search_order)
    if not results:
        scan(list(sections.keys()))

    return results
