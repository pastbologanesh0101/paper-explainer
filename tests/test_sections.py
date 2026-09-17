import unittest

from paperexplainer.sections import split_sections


class TestSectionDetection(unittest.TestCase):
    def test_standard_headers_are_detected(self):
        text = (
            "Abstract\n"
            "This paper studies widgets.\n\n"
            "Introduction\n"
            "Widgets are important.\n\n"
            "Methods\n"
            "We built a widget tester.\n\n"
            "Results\n"
            "The widget tester worked.\n\n"
            "Conclusion\n"
            "Widgets are indeed important.\n"
        )
        sections = split_sections(text)

        self.assertIn("Abstract", sections)
        self.assertIn("Introduction", sections)
        self.assertIn("Methods", sections)
        self.assertIn("Results", sections)
        self.assertIn("Conclusion", sections)
        self.assertEqual(sections["Abstract"], "This paper studies widgets.")
        self.assertEqual(sections["Results"], "The widget tester worked.")

    def test_common_header_variants_map_to_canonical_names(self):
        text = (
            "1. Introduction\n"
            "Widgets are important.\n\n"
            "Related Works\n"
            "Others have studied widgets.\n\n"
            "Methodology\n"
            "We used a widget tester.\n\n"
            "Findings\n"
            "It worked well.\n\n"
            "Concluding Remarks\n"
            "Widgets matter.\n"
        )
        sections = split_sections(text)

        # Variant headers should be normalized to canonical names.
        self.assertIn("Introduction", sections)
        self.assertIn("Related Work", sections)
        self.assertIn("Methods", sections)
        self.assertIn("Results", sections)
        self.assertIn("Conclusion", sections)

        self.assertEqual(sections["Related Work"], "Others have studied widgets.")
        self.assertEqual(sections["Methods"], "We used a widget tester.")
        self.assertEqual(sections["Results"], "It worked well.")
        self.assertEqual(sections["Conclusion"], "Widgets matter.")

    def test_missing_sections_are_simply_absent_not_errors(self):
        # A short paper with no Related Work, Discussion, or Introduction.
        text = (
            "Abstract\n"
            "We propose a small heuristic.\n\n"
            "Methods\n"
            "We scored pairs by overlap.\n\n"
            "Results\n"
            "It worked in 84% of cases.\n\n"
            "Conclusion\n"
            "The heuristic is useful.\n"
        )
        sections = split_sections(text)

        self.assertNotIn("Related Work", sections)
        self.assertNotIn("Discussion", sections)
        self.assertNotIn("Introduction", sections)
        self.assertIn("Abstract", sections)
        self.assertIn("Methods", sections)
        self.assertIn("Results", sections)
        self.assertIn("Conclusion", sections)


if __name__ == "__main__":
    unittest.main()
