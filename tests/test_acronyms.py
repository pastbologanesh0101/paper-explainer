import unittest

from paperexplainer.acronyms import expand_acronyms, find_acronym_definitions


class TestAcronymHandling(unittest.TestCase):
    def test_definition_pattern_is_detected(self):
        text = (
            "We train a Support Vector Machine (SVM) classifier on the "
            "extracted features."
        )
        definitions = find_acronym_definitions(text)
        self.assertIn("SVM", definitions)
        self.assertEqual(definitions["SVM"], "Support Vector Machine")

    def test_multiple_acronyms_are_detected_in_order(self):
        text = (
            "We compare a Support Vector Machine (SVM) to a Random Forest (RF) "
            "classifier and a Convolutional Neural Network (CNN)."
        )
        definitions = find_acronym_definitions(text)
        self.assertEqual(list(definitions.keys()), ["SVM", "RF", "CNN"])

    def test_first_later_use_is_expanded_to_full_term(self):
        text = (
            "We train a Support Vector Machine (SVM) classifier. "
            "Later, the SVM achieved high accuracy. The SVM was fast too."
        )
        expanded = expand_acronyms(text)
        # The defining sentence keeps "SVM" in parentheses, but the very
        # next standalone mention should be spelled out.
        self.assertIn("Support Vector Machine (SVM) classifier", expanded)
        self.assertIn("the Support Vector Machine achieved high accuracy", expanded)


if __name__ == "__main__":
    unittest.main()
