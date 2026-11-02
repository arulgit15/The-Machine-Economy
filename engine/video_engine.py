"""
Multi-Track Video Compositor
Combines dynamic multi-scene B-Roll, procedural HUD overlays, kinetic ASS subtitles,
and master ducked audio into an ultra-clean, monetization-safe 1080p MP4.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image

from config.settings import FORMATS
from engine.media_engine import (
    render_procedural_background_video,
    render_stat_hud_card,
    fetch_stock_broll
)
from engine.subtitle_engine import generate_ass_subtitles

def prepare_multi_scene_background(
    scenes: list,
    temp_dir: Path,
    width: int,
    height: int,
    fps: int,
    total_duration: float,
    orientation: str = "portrait"
) -> Path:
    """
    Downloads and normalizes individual B-Roll clips for each scene in the script,
    stitching them into a fast-paced, high-retention visual timeline.
    """
    num_scenes = max(1, len(scenes))
    scene_duration = total_duration / num_scenes
    normalized_clips = []

    for i, sc in enumerate(scenes):
        query = sc.get("visual_query", "cyber technology")
        raw_clip = temp_dir / f"raw_scene_{i}.mp4"
        norm_clip = temp_dir / f"norm_scene_{i}.mp4"

        # Try fetching specific stock clip for this scene
        downloaded = fetch_stock_broll(query, raw_clip, orientation=orientation, clip_index=i)

        if downloaded and raw_clip.exists():
            # Scale, subtle Ken Burns dynamic zoom, crop to format, lock duration, and cinematic grading
            num_frames = max(30, int(scene_duration * fps))
            scale_filter = (
                f"scale=1920:1080:force_original_aspect_ratio=increase,"
                f"zoompan=z='min(zoom+0.0012,1.12)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={width}x{height},"
                f"setsar=1,"
                f"eq=contrast=1.06:brightness=-0.02:saturation=1.1"
            )
            cmd = [
                "ffmpeg", "-y",
                "-loglevel", "error",
                "-stream_loop", "-1",
                "-i", str(raw_clip),
                "-t", f"{scene_duration:.2f}",
                "-vf", scale_filter,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                "-an",
                str(norm_clip)
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if res.returncode == 0 and norm_clip.exists():
                normalized_clips.append(norm_clip)
                continue

        # Fallback to procedural cyber motion if download fails
        render_procedural_background_video(
            norm_clip,
            width=width,
            height=height,
            duration_sec=scene_duration,
            fps=fps
        )
        normalized_clips.append(norm_clip)

    # Concat all normalized clips into a unified visual track
    concat_list_file = temp_dir / "concat_list.txt"
    with open(concat_list_file, "w", encoding="utf-8") as f:
        for clip in normalized_clips:
            # Use forward slashes for ffmpeg concat demuxer
            clean_path = str(clip.resolve()).replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    master_bg = temp_dir / "stitched_background.mp4"
    concat_cmd = [
        "ffmpeg", "-y",
        "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(master_bg)
    ]
    subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    return master_bg if master_bg.exists() else normalized_clips[0]

def build_composite_video(
    package: dict,
    audio_info: dict,
    output_path: Path,
    video_type: str = "short"
) -> Path:
    """
    Renders the final ready-to-publish MP4 video with multi-scene pattern interrupts.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_path.parent / f"temp_{output_path.stem}"
    temp_dir.mkdir(parents=True, exist_ok=True)

    fmt = FORMATS[video_type]
    width = fmt["width"]
    height = fmt["height"]
    fps = fmt["fps"]
    duration = audio_info["duration_sec"]
    orientation = "portrait" if video_type == "short" else "landscape"

    # Step 1: Generate ASS Subtitles
    ass_path = temp_dir / "subtitles.ass"
    generate_ass_subtitles(
        audio_info["cues"],
        ass_path,
        video_type=video_type,
        width=width,
        height=height
    )

    # Step 2: Multi-Scene B-Roll Sequencer (Pattern interrupts every 3-5 seconds)
    scenes = package.get("scenes", [])
    bg_video_path = prepare_multi_scene_background(
        scenes=scenes,
        temp_dir=temp_dir,
        width=width,
        height=height,
        fps=fps,
        total_duration=duration + 0.5,
        orientation=orientation
    )

    # Step 3: Check for HUD Stat Card Overlays
    hud_overlay_image = None
    hud_start_t, hud_end_t = 3.0, 8.0
    num_scenes = max(1, len(scenes))
    scene_dur = duration / num_scenes

    for i, sc in enumerate(scenes):
        overlay = sc.get("stat_overlay", {})
        if overlay.get("show"):
            hud_card = render_stat_hud_card(
                title=overlay.get("title", "SYSTEM METRIC"),
                value=overlay.get("value", "99%"),
                subtitle=overlay.get("subtitle", "Observed"),
                width=int(width * 0.88) if video_type == "short" else 620,
                height=260
            )
            hud_overlay_image = temp_dir / "stat_card.png"
            hud_card.save(str(hud_overlay_image))
            hud_start_t = max(1.5, i * scene_dur)
            hud_end_t = min(duration, hud_start_t + 4.5)
            break

    # Step 4: Formatting the subtitle path with forward slashes for FFmpeg libavfilter compatibility
    ass_filter_path = str(ass_path.resolve()).replace("\\", "/")
    if ":" in ass_filter_path:
        drive, rest = ass_filter_path.split(":", 1)
        ass_filter_path = f"{drive}\\:{rest}"

    master_audio = audio_info["final_audio_path"]

    # Step 5: Final Multi-Track Composition in FFmpeg
    if hud_overlay_image and hud_overlay_image.exists():
        hud_pos_y = 350 if video_type == "short" else 80
        hud_pos_x = "(W-w)/2" if video_type == "short" else 60
        filter_str = (
            f"[0:v]format=yuv420p[base];"
            f"[1:v]format=rgba[hud];"
            f"[base][hud]overlay={hud_pos_x}:{hud_pos_y}:enable='between(t,{hud_start_t:.2f},{hud_end_t:.2f})'[overlaid];"
            f"[overlaid]subtitles='{ass_filter_path}'[outv]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loglevel", "error",
            "-stream_loop", "-1",
            "-i", str(bg_video_path),
            "-i", str(hud_overlay_image),
            "-i", str(master_audio),
            "-filter_complex", filter_str,
            "-map", "[outv]",
            "-map", "2:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{duration:.2f}",
            str(output_path)
        ]
    else:
        filter_str = (
            f"format=yuv420p,"
            f"subtitles='{ass_filter_path}'"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loglevel", "error",
            "-stream_loop", "-1",
            "-i", str(bg_video_path),
            "-i", str(master_audio),
            "-vf", filter_str,
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", f"{duration:.2f}",
            str(output_path)
        ]

    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Video composition failed:\n{res.stderr}")

    return output_path
