import unittest

from paperexplainer.explainer import explain_paper, format_explanation


class TestExplainerGracefulHandling(unittest.TestCase):
    def test_paper_missing_several_sections_does_not_crash(self):
        # No Introduction, Related Work, or Discussion at all.
        text = (
            "Abstract\n"
            "We propose a small heuristic for duplicate detection. We show "
            "it finds 84% of true duplicates.\n\n"
            "Methods\n"
            "We compute token overlap between pairs of reports.\n\n"
            "Results\n"
            "The heuristic achieved 84% recall and a 9% false-positive rate.\n"
        )
        explanation = explain_paper(text)

        self.assertNotIn("Introduction", explanation["sections"])
        self.assertNotIn("Related Work", explanation["sections"])
        self.assertNotIn("Discussion", explanation["sections"])
        self.assertIn("Abstract", explanation["sections"])
        self.assertIn("Methods", explanation["sections"])
        self.assertIn("Results", explanation["sections"])

        self.assertTrue(len(explanation["contribution"]) >= 1)
        self.assertTrue(len(explanation["numeric_results"]) >= 1)

        # format_explanation should also not raise, even with gaps.
        report = format_explanation(explanation, paper_title="test paper")
        self.assertIn("Abstract", report)
        self.assertNotIn("Introduction", report)

    def test_paper_with_no_recognizable_sections_at_all(self):
        text = "Just some unstructured notes with no headers whatsoever."
        explanation = explain_paper(text)
        self.assertEqual(explanation["sections"], {})
        # Should still produce a report string without raising.
        report = format_explanation(explanation, paper_title="empty test")
        self.assertIn("No standard sections", report)


if __name__ == "__main__":
    unittest.main()
