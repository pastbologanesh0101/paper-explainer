import unittest

from paperexplainer.extraction import (
    extract_contribution_statements,
    extract_numeric_results,
)


class TestContributionExtraction(unittest.TestCase):
    def test_extracts_we_propose_sentence_from_abstract(self):
        sections = {
            "Abstract": (
                "Widget detection is a hard problem. We propose a new "
                "detector that runs in real time. It works well."
            )
        }
        contributions = extract_contribution_statements(sections)
        self.assertTrue(any("we propose" in c.lower() for c in contributions))

    def test_extracts_our_contribution_sentence_from_introduction(self):
        sections = {
            "Introduction": (
                "Prior work is limited. Our contribution is a faster "
                "training procedure for widget detectors."
            )
        }
        contributions = extract_contribution_statements(sections)
        self.assertTrue(
            any("our contribution" in c.lower() for c in contributions)
        )

    def test_no_contribution_pattern_returns_empty_list(self):
        sections = {"Abstract": "Widgets are interesting objects to study."}
        contributions = extract_contribution_statements(sections)
        self.assertEqual(contributions, [])


class TestNumericResultExtraction(unittest.TestCase):
    def test_extracts_percentage_from_results_section(self):
        sections = {
            "Results": (
                "The detector achieved 91.5% accuracy on the test set. "
                "It ran without crashing."
            )
        }
        results = extract_numeric_results(sections)
        self.assertEqual(len(results), 1)
        self.assertIn("91.5%", results[0]["numbers"])

    def test_extracts_pvalue_and_multiple_numbers(self):
        sections = {
            "Results": (
                "Accuracy improved from 80% to 88%, p < 0.05, a clear gain."
            )
        }
        results = extract_numeric_results(sections)
        self.assertEqual(len(results), 1)
        numbers = results[0]["numbers"]
        self.assertIn("80%", numbers)
        self.assertIn("88%", numbers)
        self.assertTrue(any(n.startswith("p") for n in numbers))

    def test_no_numbers_returns_empty_list(self):
        sections = {"Results": "The detector worked as expected in every trial."}
        results = extract_numeric_results(sections)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
