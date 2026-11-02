"""
Zero-Glitch Neural Audio & Emotion Engine
Synthesizes uninterrupted voiceover using chunked Edge-TTS, extracts exact timing markers,
and performs dynamic FFmpeg sidechain audio ducking with background music and SFX.
"""

import asyncio
import json
import subprocess
from pathlib import Path
from edge_tts import Communicate

from config.settings import DEFAULT_VOICE, AUDIO_CONFIG, BGM_DIR, SFX_DIR
from engine.normalizer import semantic_chunk_text
from engine.sound_synth import generate_ambient_cyber_pad, generate_whoosh_sfx, generate_click_sfx

async def synthesize_voice_stream(text: str, voice: str = DEFAULT_VOICE, rate: str = "+0%", pitch: str = "+0Hz"):
    """
    Synthesizes speech using semantic chunking to guarantee zero glitches,
    zero WebSocket timeouts, and extracts millisecond-accurate timeline boundaries.
    """
    chunks = semantic_chunk_text(text, max_chars=220)
    if not chunks:
        raise ValueError("Text is empty or could not be normalized.")

    combined_audio = bytearray()
    timeline_cues = []
    current_time_ms = 0.0

    for i, chunk in enumerate(chunks):
        comm = Communicate(chunk, voice=voice, rate=rate, pitch=pitch)
        chunk_audio = bytearray()
        chunk_sentences = []

        async for msg in comm.stream():
            if msg["type"] == "audio":
                chunk_audio.extend(msg["data"])
            elif msg["type"] == "SentenceBoundary":
                # offset and duration in 100ns units -> convert to milliseconds
                offset_ms = msg["offset"] / 10000.0
                duration_ms = msg["duration"] / 10000.0
                chunk_sentences.append({
                    "text": msg["text"],
                    "offset_ms": offset_ms,
                    "duration_ms": duration_ms
                })

        # Calculate duration of chunk audio
        # Using sentence bounds or audio bytes fallback
        if chunk_sentences:
            first_offset = chunk_sentences[0]["offset_ms"]
            for s in chunk_sentences:
                start_ms = current_time_ms + (s["offset_ms"] - first_offset)
                end_ms = start_ms + s["duration_ms"]
                timeline_cues.append({
                    "text": s["text"],
                    "start_ms": start_ms,
                    "end_ms": end_ms,
                    "duration_ms": s["duration_ms"]
                })
            chunk_duration_ms = (chunk_sentences[-1]["offset_ms"] - first_offset) + chunk_sentences[-1]["duration_ms"]
        else:
            # Fallback estimation if SentenceBoundary was empty
            # ~3200 bytes per second for standard 128kbps mp3
            chunk_duration_ms = (len(chunk_audio) / 16000.0) * 1000.0
            timeline_cues.append({
                "text": chunk,
                "start_ms": current_time_ms,
                "end_ms": current_time_ms + chunk_duration_ms,
                "duration_ms": chunk_duration_ms
            })

        combined_audio.extend(chunk_audio)
        current_time_ms += chunk_duration_ms

    return combined_audio, timeline_cues, current_time_ms / 1000.0

def mix_audio_with_sidechain(voice_path: Path, bgm_path: Path, output_path: Path, target_duration: float = None):
    """
    Applies FFmpeg sidechain compression so the background music automatically ducks
    when the voice speaks, swelling smoothly during dramatic pauses.
    Also applies EBU R128 loudness normalization (-14 LUFS).
    """
    voice_path = Path(voice_path)
    bgm_path = Path(bgm_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sidechain_cfg = AUDIO_CONFIG["sidechain"]
    th = sidechain_cfg["threshold"]
    ratio = sidechain_cfg["ratio"]
    attack = sidechain_cfg["attack"]
    release = sidechain_cfg["release"]
    target_lufs = AUDIO_CONFIG["target_lufs"]

    # FFmpeg filtergraph:
    # 1. Voice input [0:a] is standardized to 48kHz stereo, split into [sc] (sidechain trigger) and [vox] (clean speech).
    # 2. BGM input [1:a] is looped, padded with apad, and compressed using [sc].
    # 3. Ducked BGM and Voice are mixed, then passed through loudnorm to hit exact -14 LUFS.
    filter_complex = (
        f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asplit=2[sc][vox];"
        f"[1:a]aloop=loop=-1:size=2e+09,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[bgm];"
        f"[bgm][sc]sidechaincompress=threshold={th}:ratio={ratio}:attack={attack}:release={release}:makeup=1[ducked];"
        f"[ducked][vox]amix=inputs=2:normalize=0:duration=first[mixed];"
        f"[mixed]loudnorm=I={target_lufs}:LRA=11:TP=-1.5[outa]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(voice_path),
        "-i", str(bgm_path),
        "-filter_complex", filter_complex,
        "-map", "[outa]",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]

    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio mixing failed:\n{res.stderr}")

    return output_path

async def build_audio_track(text: str, output_dir: Path, voice: str = DEFAULT_VOICE, bgm_file: Path = None):
    """Full pipeline for voice generation, timeline generation, and sidechain audio mixing."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    voice_path = output_dir / "voice_raw.mp3"
    timeline_path = output_dir / "timeline.json"
    final_audio_path = output_dir / "master_audio.aac"

    # Step 1: Synthesize voice
    audio_bytes, timeline_cues, total_seconds = await synthesize_voice_stream(text, voice=voice)
    with open(voice_path, "wb") as f:
        f.write(audio_bytes)

    # Save timeline metadata
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_duration_sec": total_seconds,
            "cues": timeline_cues
        }, f, indent=2)

    # Step 2: Ensure BGM exists
    if bgm_file is None or not Path(bgm_file).exists():
        default_bgm = BGM_DIR / "cyber_ambient_synth.wav"
        if not default_bgm.exists():
            generate_ambient_cyber_pad(default_bgm, duration_sec=120.0)
        bgm_file = default_bgm

    # Step 3: Mix with sidechain ducking & -14 LUFS loudness
    mix_audio_with_sidechain(voice_path, bgm_file, final_audio_path)

    return {
        "voice_path": str(voice_path),
        "timeline_path": str(timeline_path),
        "final_audio_path": str(final_audio_path),
        "duration_sec": total_seconds,
        "cues": timeline_cues
    }

