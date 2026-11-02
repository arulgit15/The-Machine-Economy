import unittest
from pathlib import Path
from engine.thumb_engine import create_high_ctr_thumbnail

class TestThumbnail(unittest.TestCase):
    def test_thumb_generation(self):
        out = Path("output/test_thumb.jpg")
        create_high_ctr_thumbnail("WHO OWNS THEM?", out)
        self.assertTrue(out.exists())
        self.assertGreater(out.stat().st_size, 10000)
        print(f"\nThumbnail generated successfully at {out} ({out.stat().st_size} bytes)")

if __name__ == "__main__":
    unittest.main()

