"""
The Machine Economy - Autonomous YouTube Channel Pipeline
Master Orchestration CLI
"""

import sys
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

# Ensure standard UTF-8 console output on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from config.settings import OUTPUT_DIR, DEFAULT_VOICE, DEFAULT_PRIVACY_STATUS
from engine.script_engine import generate_video_package
from engine.audio_engine import build_audio_track
from engine.thumb_engine import create_high_ctr_thumbnail
from engine.video_engine import build_composite_video
from engine.yt_uploader import upload_video_to_youtube

def run_pipeline(
    video_type: str = "short",
    specific_topic: str = None,
    voice: str = DEFAULT_VOICE,
    dry_run: bool = True,
    privacy_status: str = DEFAULT_PRIVACY_STATUS
):
    print("=" * 70)
    print(f"[PIPELINE] STARTING: The Machine Economy Channel ({video_type.upper()})")
    print(f"[PIPELINE] Timestamp: {datetime.now().isoformat()}")
    print("=" * 70)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_DIR / f"{video_type}_{timestamp_str}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. Script & SEO Package Generation
    print("\n[1/5] [SCRIPT] Generating Algorithmic Script & SEO Metadata...")
    package = generate_video_package(video_type=video_type, specific_topic=specific_topic)
    print(f"  * Title: {package['title']}")
    print(f"  * Hook: {package['hook'][:80]}...")
    print(f"  * Scenes: {len(package.get('scenes', []))} visual cues generated.")

    # 2. Audio Synthesis & Sidechain Mixing
    print("\n[2/5] [AUDIO] Synthesizing Zero-Glitch Audio & Mixing BGM (EBU R128 -14 LUFS)...")
    audio_info = asyncio.run(
        build_audio_track(
            text=package["script_clean"],
            output_dir=run_dir,
            voice=voice
        )
    )
    print(f"  * Master Audio Duration: {audio_info['duration_sec']:.2f}s")
    print(f"  * Timeline Cues Extracted: {len(audio_info['cues'])}")

    # 3. High-CTR Thumbnail Generation
    print("\n[3/5] [THUMBNAIL] Rendering High-CTR Thumbnail (3-Word Rule + Cyber Tension)...")
    thumb_path = run_dir / "thumbnail.jpg"
    thumb_text = package.get("seo", {}).get("thumbnail_text", "WHO OWNS THEM?")
    create_high_ctr_thumbnail(
        title_text=thumb_text,
        output_path=thumb_path,
        sub_tag=f"MACHINE ECONOMY // {datetime.now().year}"
    )
    print(f"  * Thumbnail generated at: {thumb_path}")

    # 4. Multi-Track Video Composition
    print("\n[4/5] [VIDEO] Compositing Video (B-Roll + Kinetic ASS Subtitles + HUD Overlay)...")
    video_path = run_dir / f"final_{video_type}.mp4"
    build_composite_video(
        package=package,
        audio_info=audio_info,
        output_path=video_path,
        video_type=video_type
    )
    print(f"  * Video master rendered at: {video_path}")
    print(f"  * File Size: {video_path.stat().st_size / (1024 * 1024):.2f} MB")

    # 5. YouTube Upload
    print("\n[5/5] [PUBLISH] Publishing / Dry-Run Distribution...")
    upload_result = upload_video_to_youtube(
        video_path=video_path,
        thumbnail_path=thumb_path,
        metadata={
            "title": package["title"],
            "description": package["seo"]["description"],
            "tags": package["seo"]["tags"]
        },
        privacy_status=privacy_status,
        dry_run=dry_run
    )

    print("\n" + "=" * 70)
    print("[PIPELINE] COMPLETE: ALL STAGES FINISHED")
    print(f"Video: {video_path}")
    print(f"Thumbnail: {thumb_path}")
    print(f"Status: {upload_result['status']}")
    print("=" * 70)

    return {
        "video_path": str(video_path),
        "thumb_path": str(thumb_path),
        "upload_result": upload_result
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous YouTube Channel Pipeline")
    parser.add_argument("--type", choices=["short", "long"], default="short", help="Video format (short or long)")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic idea")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="TTS voice name")
    parser.add_argument("--live", action="store_true", help="Set for live YouTube upload (default is dry-run)")
    parser.add_argument("--privacy", type=str, default=DEFAULT_PRIVACY_STATUS, choices=["private", "unlisted", "public"])

    args = parser.parse_args()

    run_pipeline(
        video_type=args.type,
        specific_topic=args.topic,
        voice=args.voice,
        dry_run=not args.live,
        privacy_status=args.privacy
    )
