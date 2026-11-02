"""
Global Channel & Automation Configuration
Channel: The Machine Economy & Speculative Tech
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
BGM_DIR = ASSETS_DIR / "bgm"
SFX_DIR = ASSETS_DIR / "sfx"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
FONTS_DIR.mkdir(parents=True, exist_ok=True)
BGM_DIR.mkdir(parents=True, exist_ok=True)
SFX_DIR.mkdir(parents=True, exist_ok=True)

# API Keys (Loaded from environment variables or GitHub Secrets)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
YT_REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN", "")

# Channel Persona & Tone
CHANNEL_NAME = "The Machine Economy"
NICHE = "Speculative Tech, AI Agents, Autonomous Labor & Post-2026 Economics"
DEFAULT_VOICE = os.getenv("VOICE_NAME", "en-US-ChristopherNeural")
VOICE_RATE = "+0%"
VOICE_PITCH = "+0Hz"

# Visual Theme: Dark Cyber-Terminal Aesthetic
THEME = {
    "bg_color": "#0B0C10",
    "card_bg": "#1F2833",
    "accent_cyan": "#66FCF1",
    "accent_teal": "#45A29E",
    "accent_gold": "#FFE600",
    "text_main": "#FFFFFF",
    "text_dim": "#C5C6C7",
    "font_main": "Arial-Bold",
}

# Video Formats
FORMATS = {
    "short": {
        "width": 1080,
        "height": 1920,
        "fps": 30,
        "duration_min": 30,
        "duration_max": 58,
    },
    "long": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "duration_min": 180,
        "duration_max": 600,
    }
}

# YouTube Audio Standards
AUDIO_CONFIG = {
    "target_lufs": -14.0,  # YouTube standard
    "sample_rate": 48000,
    "sidechain": {
        "threshold": 0.03,
        "ratio": 8,
        "attack": 20,
        "release": 300,
        "makeup": 1,
    }
}

# YouTube API Quota Safeguard
MAX_DAILY_UPLOADS = 3
DEFAULT_PRIVACY_STATUS = os.getenv("YT_PRIVACY_STATUS", "public")  # default public for hands-free automation

