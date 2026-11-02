import asyncio
import unittest
from pathlib import Path
from engine.audio_engine import build_audio_track

class TestAudioEngine(unittest.TestCase):
    def test_audio_pipeline(self):
        sample_script = (
            "By 2027, the autonomous machine economy will process over $40B in automated transactions. "
            "Neural agent swarms are eliminating traditional corporate bottlenecks. "
            "Are you positioned for this transition, or will your business be left behind?"
        )
        test_dir = Path("output/test_audio_run")
        test_dir.mkdir(parents=True, exist_ok=True)

        result = asyncio.run(build_audio_track(sample_script, test_dir))
        
        self.assertTrue(Path(result["voice_path"]).exists())
        self.assertTrue(Path(result["final_audio_path"]).exists())
        self.assertTrue(Path(result["timeline_path"]).exists())
        self.assertGreater(result["duration_sec"], 5.0)
        self.assertGreater(len(result["cues"]), 0)
        print(f"\nAudio test successful! Duration: {result['duration_sec']:.2f}s, Cues: {len(result['cues'])}")

if __name__ == "__main__":
    unittest.main()

