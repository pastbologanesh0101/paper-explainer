import unittest

from paperexplainer.scoring import top_sentences


class TestExtractiveScoring(unittest.TestCase):
    def test_picks_the_central_sentence_over_generic_filler(self):
        # Crafted so that "widget" and "detector" are the dominant,
        # repeated topic words, concentrated in one clearly central
        # sentence, while the other sentences are generic filler that
        # barely overlaps in vocabulary.
        text = (
            "This is a short note. "
            "Weather today is mild and unremarkable. "
            "The widget detector combines widget shape analysis and "
            "widget color analysis to classify each widget with a "
            "specialized widget detector model. "
            "Someone had lunch nearby. "
            "Traffic was light this morning."
        )
        top = top_sentences(text, n=1)
        self.assertEqual(len(top), 1)
        self.assertIn("widget detector combines", top[0])

    def test_returns_empty_list_for_empty_text(self):
        self.assertEqual(top_sentences("", n=3), [])

    def test_n_larger_than_sentence_count_returns_all_sentences(self):
        text = "First sentence here. Second sentence here."
        top = top_sentences(text, n=10)
        self.assertEqual(len(top), 2)


if __name__ == "__main__":
    unittest.main()
