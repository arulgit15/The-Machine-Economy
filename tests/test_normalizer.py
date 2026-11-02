import unittest
from engine.normalizer import normalize_text_for_speech, semantic_chunk_text

class TestNormalizer(unittest.TestCase):
    def test_currency_and_numbers(self):
        sample = "In 2027, the AI market will reach $40B and 85% of SaaS firms will run on LLMs."
        res = normalize_text_for_speech(sample)
        self.assertIn("twenty twenty-seven", res)
        self.assertIn("forty billion dollars", res)
        self.assertIn("85 percent", res)
        self.assertIn("A-I", res)
        self.assertIn("L-L-M's", res)

    def test_semantic_chunking(self):
        text = (
            "The autonomous machine economy is arriving faster than anticipated. "
            "Wall Street models predict a $50T shift in global labor capital. "
            "Are you ready for the post-2026 economic reality? Let's break it down."
        )
        chunks = semantic_chunk_text(text, max_chars=120)
        self.assertTrue(len(chunks) >= 3)
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 120)
            self.assertTrue(chunk[0].isupper() or chunk[0].isdigit() or chunk[0] == '"')

if __name__ == "__main__":
    unittest.main()

