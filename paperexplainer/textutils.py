"""Small shared text-processing helpers: sentence splitting and
tokenization. No third-party dependencies.
"""

import re

# A conservative set of abbreviations that should NOT trigger a sentence
# break even though they end with a period.
_ABBREVIATIONS = {
    "e.g.", "i.e.", "etc.", "et al.", "fig.", "eq.", "vs.", "approx.",
    "no.", "cf.", "dr.", "mr.", "mrs.", "ms.", "prof.",
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'\(])")

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']*")

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "so", "of", "to",
    "in", "on", "for", "with", "as", "by", "at", "from", "is", "are",
    "was", "were", "be", "been", "being", "this", "that", "these",
    "those", "it", "its", "we", "our", "us", "they", "their", "you",
    "your", "i", "he", "she", "his", "her", "them", "which", "who",
    "whom", "what", "when", "where", "how", "why", "not", "no", "can",
    "could", "will", "would", "shall", "should", "may", "might", "must",
    "do", "does", "did", "has", "have", "had", "than", "into", "such",
    "also", "more", "most", "some", "other", "each", "all", "both",
    "over", "under", "up", "down", "out", "about", "between", "while",
    "after", "before", "because",
}


def split_sentences(text):
    """Split a block of text into a list of sentences.

    Handles a short list of common abbreviations so "e.g." or "et al."
    don't create spurious sentence breaks. This is a heuristic, not a
    full NLP sentence tokenizer.
    """
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return []

    # Protect abbreviations by temporarily replacing their periods.
    protected = text
    placeholder_map = {}
    for i, abbr in enumerate(_ABBREVIATIONS):
        token = "@@ABBR{}@@".format(i)
        pattern = re.compile(re.escape(abbr), re.IGNORECASE)
        if pattern.search(protected):
            placeholder_map[token] = abbr
            protected = pattern.sub(token, protected)

    raw_sentences = _SENTENCE_SPLIT_RE.split(protected)

    sentences = []
    for s in raw_sentences:
        for token, abbr in placeholder_map.items():
            s = s.replace(token, abbr)
        s = s.strip()
        if s:
            sentences.append(s)
    return sentences


def tokenize_words(text):
    """Lowercase word tokens (letters, hyphens, apostrophes only)."""
    return [w.lower() for w in _WORD_RE.findall(text)]


def content_words(text):
    """Word tokens with stopwords removed."""
    return [w for w in tokenize_words(text) if w not in STOPWORDS and len(w) > 1]
