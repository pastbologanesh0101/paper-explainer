#!/usr/bin/env python3
"""CLI entry point for AI Research Paper Explainer.

Usage:
    python explain.py paper.txt
"""

import argparse
import sys

from paperexplainer.explainer import explain_paper, format_explanation


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="explain.py",
        description=(
            "Turn a plain-text academic paper into a plain-language "
            "explanation organized by section (Abstract, Introduction, "
            "Methods, Results, Conclusion, ...). No LLM calls: rule-based "
            "extractive summarization + jargon simplification."
        ),
    )
    parser.add_argument("paper", help="Path to a plain-text (.txt) research paper.")
    parser.add_argument(
        "--sentences-per-section",
        type=int,
        default=3,
        help="How many key sentences to extract per section (default: 3).",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=25,
        help="Sentences longer than this are split at a conjunction (default: 25).",
    )
    args = parser.parse_args(argv)

    try:
        with open(args.paper, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as exc:
        print("Error reading {}: {}".format(args.paper, exc), file=sys.stderr)
        return 1

    explanation = explain_paper(
        text,
        sentences_per_section=args.sentences_per_section,
        max_words=args.max_words,
    )
    report = format_explanation(explanation, paper_title=args.paper)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
