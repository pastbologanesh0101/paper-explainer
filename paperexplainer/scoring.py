"""Extractive sentence scoring, implemented from scratch (no external
NLP libraries). Uses a TF-IDF-style scheme where each sentence in a
section is treated as a "mini document" and words are weighted by how
concentrated they are in a few sentences (inverse sentence frequency)
versus spread across the whole section.
"""

import math

from .textutils import content_words, split_sentences


def _term_frequencies(words):
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    return freq


def score_sentences(sentences):
    """Return a list of importance scores, one per sentence, using a
    TF-IDF scheme computed across the given sentence list.
    """
    if not sentences:
        return []

    tokenized = [content_words(s) for s in sentences]
    n_sentences = len(sentences)

    # Document frequency: in how many sentences does each word appear?
    doc_freq = {}
    for words in tokenized:
        for w in set(words):
            doc_freq[w] = doc_freq.get(w, 0) + 1

    idf = {
        w: math.log((1 + n_sentences) / (1 + df)) + 1.0
        for w, df in doc_freq.items()
    }

    scores = []
    for words in tokenized:
        if not words:
            scores.append(0.0)
            continue
        tf = _term_frequencies(words)
        total = sum(tf.values())
        weight_sum = 0.0
        for w, count in tf.items():
            tf_norm = count / total
            weight_sum += tf_norm * idf.get(w, 0.0)
        # Mild length normalization: very short sentences (e.g. a lone
        # heading fragment) are down-weighted slightly so they don't
        # win purely by having one rare word.
        length_factor = min(1.0, len(words) / 6.0)
        scores.append(weight_sum * (0.5 + 0.5 * length_factor))

    return scores


def top_sentences(text, n=3):
    """Return the top-`n` most important sentences from `text`, in their
    original order of appearance (not sorted by score).
    """
    sentences = split_sentences(text)
    if not sentences:
        return []
    scores = score_sentences(sentences)
    ranked_indices = sorted(
        range(len(sentences)), key=lambda i: scores[i], reverse=True
    )
    chosen = sorted(ranked_indices[:n])
    return [sentences[i] for i in chosen]
