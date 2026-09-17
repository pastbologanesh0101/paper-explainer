"""Rule-based "plain language" rewriting pass.

This is intentionally NOT a paraphrasing model. It is a hand-authored
dictionary of academic-jargon phrases mapped to plainer wording, plus a
sentence-length simplifier that splits long sentences at conjunctions.
Acronym expansion lives in acronyms.py.
"""

import re

# Ordered (not a dict) so longer/more specific phrases are tried before
# shorter ones that could be a substring of them. Matching is applied in
# this order, longest phrase first within any tie.
JARGON_SUBSTITUTIONS = [
    (r"a statistically significant\s*\(p\s*<\s*0\.05\)\s*improvement",
     "an improvement that is unlikely to be due to chance"),
    (r"a statistically significant\s*\(p\s*<\s*0\.05\)\s*increase",
     "an increase that is unlikely to be due to chance"),
    (r"a statistically significant\s*\(p\s*<\s*0\.05\)\s*decrease",
     "a decrease that is unlikely to be due to chance"),
    (r"statistically significant\s*\(p\s*<\s*0\.05\)",
     "the result is unlikely to be due to chance"),
    (r"statistically significant\s*\(p\s*<\s*0\.01\)",
     "the result is very unlikely to be due to chance"),
    (r"statistically significant",
     "the result is unlikely to be due to chance"),
    (r"we propose a novel", "we introduce a new"),
    (r"we present a novel", "we introduce a new"),
    (r"we introduce a novel", "we introduce a new"),
    (r"we propose", "we introduce"),
    (r"we present", "we introduce"),
    (r"our contribution is", "what we add is"),
    (r"our main contribution", "the main new thing we add"),
    (r"the proposed approach", "our approach"),
    (r"the proposed method", "our method"),
    (r"a wide range of", "many different"),
    (r"a plethora of", "many"),
    (r"a significant improvement", "a large improvement"),
    (r"a significant increase", "a large increase"),
    (r"a significant decrease", "a large decrease"),
    (r"empirical evidence suggests", "our data suggests"),
    (r"it is worth noting that", "notably,"),
    (r"it can be observed that", "you can see that"),
    (r"it should be noted that", "note that"),
    (r"the results indicate that", "the results show that"),
    (r"the results demonstrate that", "the results show that"),
    (r"in the context of", "when it comes to"),
    (r"with respect to", "regarding"),
    (r"in order to", "to"),
    (r"prior to", "before"),
    (r"subsequent to", "after"),
    (r"in light of", "given"),
    (r"the aforementioned", "this"),
    (r"heretofore", "until now"),
    (r"state[- ]of[- ]the[- ]art", "the best current"),
    (r"outperforms", "does better than"),
    (r"outperformed", "did better than"),
    (r"underperforms", "does worse than"),
    (r"underperformed", "did worse than"),
    (r"demonstrates", "shows"),
    (r"demonstrate", "show"),
    (r"demonstrated", "showed"),
    (r"utilize[sd]?", "use"),
    (r"leverage[sd]?", "use"),
    (r"methodology", "method"),
    (r"efficacy", "effectiveness"),
    (r"novel", "new"),
    (r"sufficient", "enough"),
    (r"numerous", "many"),
    (r"facilitate[sd]?", "help"),
    (r"subsequently", "afterward"),
    (r"furthermore", "also"),
    (r"moreover", "also"),
    (r"however,", "but,"),
    (r"therefore,", "so,"),
    (r"approximately", "about"),
    (r"a substantial", "a large"),
    (r"substantially", "greatly"),
    (r"indicates that", "shows that"),
    (r"in conclusion,", "to sum up,"),
]

# Conjunctions/connectors at which an over-long sentence can be split
# into two sentences. Matched with a preceding comma, which is the
# common pattern in academic writing ("..., which means that...").
_SPLIT_CONNECTORS = [
    "which", "but", "and", "because", "while", "although", "since",
    "whereas",
]

_SPLIT_RE = re.compile(
    r",\s+(" + "|".join(_SPLIT_CONNECTORS) + r")\s+",
    re.IGNORECASE,
)


def _compile_substitutions():
    ordered = sorted(JARGON_SUBSTITUTIONS, key=lambda pair: len(pair[0]), reverse=True)
    compiled = []
    for pattern, replacement in ordered:
        compiled.append((re.compile(pattern, re.IGNORECASE), replacement))
    return compiled


_COMPILED_SUBSTITUTIONS = _compile_substitutions()


def _match_case(original, replacement):
    """Roughly preserve capitalization of the matched span when
    substituting, so we don't produce a lowercase word at a sentence
    start.
    """
    if original[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def apply_jargon_substitutions(text):
    """Apply the jargon -> plain-language dictionary to `text`.

    Returns (new_text, substitutions_made) where substitutions_made is a
    list of (matched_phrase, replacement) tuples in the order applied.
    """
    substitutions_made = []
    result = text
    for regex, replacement in _COMPILED_SUBSTITUTIONS:
        def _sub(match, replacement=replacement):
            matched_text = match.group(0)
            substitutions_made.append((matched_text, replacement))
            return _match_case(matched_text, replacement)

        result = regex.sub(_sub, result)
    return result, substitutions_made


def simplify_sentence_length(sentence, max_words=25):
    """If `sentence` exceeds `max_words` words, try to split it at a
    conjunction into two shorter sentences. Returns a list of one or
    two sentences.
    """
    words = sentence.split()
    if len(words) <= max_words:
        return [sentence]

    m = _SPLIT_RE.search(sentence)
    if not m:
        return [sentence]

    left = sentence[: m.start()].strip()
    connector = m.group(1)
    right = sentence[m.end():].strip()

    if not left or not right:
        return [sentence]

    # Turn "..., which shows X" into "... . This shows X" for readability.
    if connector.lower() == "which":
        right_sentence = "This " + right
    else:
        right_sentence = connector.capitalize() + " " + right

    if not left.endswith((".", "!", "?")):
        left += "."
    if not right_sentence.endswith((".", "!", "?")):
        right_sentence += "."

    return [left, right_sentence]


def plain_language_pass(sentence, max_words=25):
    """Full rule-based simplification pass for a single sentence:
    jargon substitution, then length-based splitting.

    Returns (list_of_output_sentences, substitutions_made).
    """
    substituted, substitutions_made = apply_jargon_substitutions(sentence)
    pieces = simplify_sentence_length(substituted, max_words=max_words)
    return pieces, substitutions_made
