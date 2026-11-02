"""
Dynamic Visual Engine & Asset Manager
Fetches HD B-Roll from Pexels API or synthesizes procedural cyber-tech backgrounds,
and renders dynamic HUD data cards, animated metrics, and transition overlays.
"""

import os
import math
import requests
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from config.settings import PEXELS_API_KEY, PIXABAY_API_KEY, THEME

def create_procedural_cyber_frame(width: int, height: int, frame_idx: int, total_frames: int) -> Image.Image:
    """
    Renders an animated dark cyber-terminal frame with a moving perspective grid,
    digital scanning line, and glowing ambient background.
    """
    img = Image.new("RGBA", (width, height), THEME["bg_color"])
    draw = ImageDraw.Draw(img)

    t = frame_idx / max(1, total_frames)

    # Ambient deep gradient
    center_y = int(height * 0.6)
    draw.rectangle([(0, center_y), (width, height)], fill="#0D1117")

    # Perspective Cyber Grid (Horizontal scanning lines moving downward)
    grid_lines = 14
    for i in range(grid_lines):
        progress = (i / grid_lines + t * 0.5) % 1.0
        y = int(center_y + (height - center_y) * (progress ** 2.2))
        alpha = int(40 + 160 * progress)
        color = (69, 162, 158, alpha)
        draw.line([(0, y), (width, y)], fill=color, width=2)

    # Vertical perspective lines converging to horizon center
    horizon_x = width // 2
    for offset_ratio in np.linspace(-1.5, 1.5, 15):
        bottom_x = int(horizon_x + offset_ratio * width * 0.8)
        draw.line([(horizon_x, center_y), (bottom_x, height)], fill=(69, 162, 158, 80), width=2)

    # Tech Scanner Bar moving vertically across the screen
    scan_y = int((t * 2.0 % 1.0) * height)
    draw.line([(0, scan_y), (width, scan_y)], fill=(102, 252, 241, 100), width=3)

    # Subtle corner framing brackets (HUD aesthetic)
    margin = 40
    bracket_len = 50
    hud_color = THEME["accent_cyan"]
    # Top-Left
    draw.line([(margin, margin), (margin + bracket_len, margin)], fill=hud_color, width=3)
    draw.line([(margin, margin), (margin, margin + bracket_len)], fill=hud_color, width=3)
    # Top-Right
    draw.line([(width - margin, margin), (width - margin - bracket_len, margin)], fill=hud_color, width=3)
    draw.line([(width - margin, margin), (width - margin, margin + bracket_len)], fill=hud_color, width=3)
    # Bottom-Left
    draw.line([(margin, height - margin), (margin + bracket_len, height - margin)], fill=hud_color, width=3)
    draw.line([(margin, height - margin), (margin, height - margin - bracket_len)], fill=hud_color, width=3)
    # Bottom-Right
    draw.line([(width - margin, height - margin), (width - margin - bracket_len, height - margin)], fill=hud_color, width=3)
    draw.line([(width - margin, height - margin), (width - margin, height - margin - bracket_len)], fill=hud_color, width=3)

    return img

def render_procedural_background_video(output_path: Path, width: int, height: int, duration_sec: float = 4.0, fps: int = 30):
    """
    Renders an animated seamless procedural MP4 background loop.
    Renders a crisp 4.0 second loop in ~2.5 seconds, which FFmpeg can loop indefinitely.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Render a clean 4.0 second loop (120 frames) for ultra-fast generation and looping
    loop_duration = min(4.0, duration_sec)
    total_frames = int(loop_duration * fps)

    cmd = [
        "ffmpeg", "-y",
        "-loglevel", "error",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgba",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        str(output_path)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for i in range(total_frames):
        frame = create_procedural_cyber_frame(width, height, i, total_frames)
        proc.stdin.write(frame.tobytes())

    proc.stdin.close()
    proc.wait()
    return output_path

def render_stat_hud_card(title: str, value: str, subtitle: str, width: int = 600, height: int = 260) -> Image.Image:
    """Renders a sleek glowing HUD data metric card to overlay on the video."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Translucent card background
    draw.rounded_rectangle([(10, 10), (width - 10, height - 10)], radius=16, fill=(15, 23, 42, 215), outline=(102, 252, 241, 200), width=3)

    # Glowing top accent line
    draw.line([(25, 20), (width - 25, 20)], fill=(255, 230, 0, 230), width=4)

    # Default font fallback
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_value = ImageFont.truetype("impact.ttf", 68)
        font_sub = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font_title = ImageFont.load_default()
        font_value = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Title (e.g. CAPITAL REALLOCATION)
    draw.text((35, 38), title.upper(), font=font_title, fill=THEME["accent_cyan"])

    # Draw Main Value (e.g. $40 TRILLION)
    draw.text((35, 82), value.upper(), font=font_value, fill=THEME["accent_gold"])

    # Draw Subtitle (e.g. By 2027 Projected)
    draw.text((35, 178), subtitle, font=font_sub, fill=THEME["text_dim"])

    return img

def fetch_pixabay_broll(query: str, output_path: Path, clip_index: int = 0) -> bool:
    """Fetches high-definition royalty-free b-roll from Pixabay API with clip variation."""
    api_key = os.getenv("PIXABAY_API_KEY", PIXABAY_API_KEY)
    if not api_key:
        return False

    # Extract 2-3 essential keywords for broader match on Pixabay
    clean_q = " ".join([w for w in query.split() if len(w) > 3][:3])
    url = f"https://pixabay.com/api/videos/?key={api_key}&q={requests.utils.quote(clean_q)}&video_type=all&per_page=10"

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            hits = data.get("hits", [])
            if hits:
                selected_hit = hits[clip_index % len(hits)]
                vids = selected_hit.get("videos", {})
                # Try large, then medium, then small
                target = vids.get("large", {}) or vids.get("medium", {}) or vids.get("small", {})
                download_url = target.get("url")
                if download_url:
                    vid_data = requests.get(download_url, timeout=30).content
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(vid_data)
                    return True
    except Exception as e:
        print(f"[MediaEngine] Pixabay download fallback: {e}")
    return False

def fetch_stock_broll(query: str, output_path: Path, orientation: str = "portrait", clip_index: int = 0) -> bool:
    """Tries fetching from Pixabay or Pexels, falling back gracefully."""
    # 1. Try Pixabay with clip index variation
    if fetch_pixabay_broll(query, output_path, clip_index=clip_index):
        return True
    # 2. Try Pexels
    if fetch_pexels_broll(query, output_path, orientation=orientation):
        return True
    return False

