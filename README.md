# AI Research Paper Explainer

Turn the plain text of an academic paper into a plain-language explanation,
organized by section — with **no LLM calls**. Everything is pure Python
(standard library only): section detection, extractive sentence scoring, and
rule-based jargon simplification are all implemented from scratch.

This project targets the specific structure of academic papers (Abstract,
Introduction, Related Work, Methods, Results, Discussion, Conclusion) rather
than doing generic text summarization — it knows what a "contribution
statement" or a "numeric result" looks like in a paper, and extracts them
explicitly.

## What it does

1. **Section detection** — splits the paper into its standard sections by
   matching common header variants (e.g. "Methodology", "Materials and
   Methods", and "Approach" all map to the canonical `Methods` section).
2. **Extractive scoring** — within each section, scores every sentence with
   a from-scratch TF-IDF-style scheme (sentences are treated as mini
   "documents"; words that are frequent within a sentence but rare across
   the section score highest) and keeps the top N per section, in their
   original order.
3. **Plain-language rewriting pass** (rule-based, not a paraphraser):
   - A hand-authored **jargon dictionary** substitutes academic phrasing
     with plainer wording (e.g. `"statistically significant (p<0.05)"` →
     `"the result is unlikely to be due to chance"`, `"we propose a novel
     X"` → `"we introduce a new X"`).
   - **Sentence-length simplification** splits sentences longer than a
     configurable word threshold at a conjunction (`which`, `but`,
     `because`, `while`, ...) into two shorter sentences.
   - **Acronym expansion** detects `"Full Term (ACRONYM)"` definitions
     anywhere in the paper and spells the acronym back out in plain
     language the first time it's used again later in the text.
4. **Contribution extraction** — pattern-matches phrases like `"we
   propose"`, `"we show"`, `"our contribution"` in the Abstract/Introduction
   to surface the paper's stated claim.
5. **Numeric result extraction** — regex-matches percentages, p-values, and
   "Nx" speedups (plus plain numbers next to result keywords like
   "accuracy" or "improvement") in the Results/Discussion sections.

## How to run it

No dependencies to install — pure standard library.

```bash
python explain.py samples/sample1_adaptive_sparse_retraining.txt
```

Optional flags:

```bash
python explain.py paper.txt --sentences-per-section 2 --max-words 20
```

Three original, synthetic sample papers are bundled in `samples/` (none of
these are real papers — they were written for this project to exercise
section detection, jargon simplification, and acronym expansion):

- `sample1_adaptive_sparse_retraining.txt` — a full paper with all seven
  standard sections and an `ASR`/`CNN` acronym pair.
- `sample2_synthetic_dialogue_corpus.txt` — a full paper with an `LSTM`
  acronym and a denser numeric-results section.
- `sample3_minimal_missing_sections.txt` — a short paper missing
  Introduction, Related Work, and Discussion, used to demonstrate graceful
  handling of missing sections.

## Example: before → after

Original sentence from `samples/sample1_adaptive_sparse_retraining.txt`
(Introduction section):

> "Prior approaches to pruning typically remove weights after a model has
> already converged, which necessitates a lengthy fine-tuning phase to
> recover lost accuracy, and this two-stage process substantially increases
> total training time."

Plain-language output produced by `explain.py`:

> "Prior approaches to pruning typically remove weights after a model has
> already converged."
> "This necessitates a lengthy fine-tuning phase to recover lost accuracy,
> and this two-stage process greatly increases total training time."

Note the sentence was split at "which" and `substantially` → `greatly`.

Another example, from the Abstract, showing jargon substitution and acronym
handling together:

- Before: `"We propose a novel Adaptive Sparse Retraining (ASR) procedure
  ... a statistically significant (p<0.05) improvement of 3.1 percentage
  points ..."`
- After (contribution extraction, unchanged wording, shown verbatim so the
  claim isn't misquoted):
  `"We propose a novel Adaptive Sparse Retraining (ASR) procedure that
  prunes redundant weights during training rather than after it..."`
- After (plain-language section rewrite):
  `"What we add is a training-time pruning schedule that requires no
  separate fine-tuning phase."`

And the CLI's extracted numeric results for that paper include lines like:

```
- [Results] On the primary benchmark, ASR achieves 92.4% top-1 accuracy at
  61% sparsity, compared to 89.3% for the standard post-training pruning
  baseline at the same sparsity level, a statistically significant
  (p<0.05) improvement. (numbers: 92.4%, 61%, 89.3%, p<0.05)
```

## Project layout

```
explain.py                    CLI entry point
paperexplainer/
  sections.py                 header detection + section splitting
  textutils.py                sentence splitting, tokenization, stopwords
  scoring.py                  from-scratch TF-IDF extractive scoring
  jargon.py                   jargon dictionary + sentence-length splitting
  acronyms.py                 acronym definition detection + expansion
  extraction.py                contribution-statement + numeric-result extraction
  explainer.py                 orchestrates everything into one report
samples/                      3 original synthetic sample papers
tests/                        unit tests (unittest / pytest compatible)
.github/workflows/tests.yml   CI: runs tests on Python 3.11 and 3.12
```

## Design notes / limitations

- This is **extractive + rule-based**, not generative. It never invents a
  sentence; it selects and lightly rewrites sentences that already exist in
  the paper. That means the output is always traceable back to the source
  text, but it also means the rewriting is sometimes grammatically awkward
  (e.g. substituting a long jargon phrase mid-sentence can leave odd
  wording) rather than fluent, unlike an LLM paraphrase.
- Section detection relies on the paper using recognizable header lines on
  their own line (e.g. `Methods` or `3. Methodology`). Papers with
  unconventional formatting may not split cleanly — the tool degrades
  gracefully in that case (see `sample3_minimal_missing_sections.txt` and
  the corresponding test) rather than crashing.
- Acronym expansion only spells out the **first** later standalone use of
  an acronym after its definition, by design, so the plain-language text
  stays readable rather than replacing every subsequent mention.

## Running the tests

```bash
python -m unittest discover -s tests -v
# or, if pytest is installed:
python -m pytest tests/
```

All tests use only the Python standard library.

## License

MIT — see [LICENSE](LICENSE).
