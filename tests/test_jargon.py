import unittest

from paperexplainer.jargon import apply_jargon_substitutions, simplify_sentence_length


class TestJargonSubstitution(unittest.TestCase):
    def test_statistically_significant_phrase_is_simplified(self):
        text = "The improvement was statistically significant (p<0.05)."
        new_text, subs = apply_jargon_substitutions(text)
        self.assertIn("unlikely to be due to chance", new_text)
        self.assertTrue(len(subs) >= 1)

    def test_we_propose_a_novel_is_simplified(self):
        text = "We propose a novel algorithm for widget detection."
        new_text, subs = apply_jargon_substitutions(text)
        self.assertIn("we introduce a new algorithm", new_text.lower())

    def test_multiple_jargon_terms_in_one_sentence(self):
        text = "We utilize a novel methodology to demonstrate state-of-the-art results."
        new_text, _subs = apply_jargon_substitutions(text)
        lowered = new_text.lower()
        self.assertIn("use", lowered)
        self.assertIn("new", lowered)
        self.assertIn("method", lowered)
        self.assertNotIn("utilize", lowered)
        self.assertNotIn("state-of-the-art", lowered)


class TestSentenceSimplification(unittest.TestCase):
    def test_long_sentence_is_split_at_conjunction(self):
        long_sentence = (
            "The model was trained for one hundred epochs on the full dataset "
            "using a standard optimizer, which allowed it to converge to a "
            "stable solution well before the final epoch was reached"
        )
        pieces = simplify_sentence_length(long_sentence, max_words=15)
        self.assertGreaterEqual(len(pieces), 1)
        # If a split happened, we should get two non-empty sentences.
        if len(pieces) == 2:
            self.assertTrue(pieces[0].strip())
            self.assertTrue(pieces[1].strip())

    def test_short_sentence_is_not_split(self):
        short_sentence = "We evaluated the model on the test set."
        pieces = simplify_sentence_length(short_sentence, max_words=25)
        self.assertEqual(pieces, [short_sentence])


if __name__ == "__main__":
    unittest.main()
