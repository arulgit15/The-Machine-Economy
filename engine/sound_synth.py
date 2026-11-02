"""
Procedural Sound & Synth Generator
Generates high-fidelity royalty-free ambient cyberpunk synth pads and SFX
using pure mathematics (NumPy + Wave), guaranteeing zero copyright strikes.
"""

import math
import wave
import struct
from pathlib import Path
import numpy as np

def generate_ambient_cyber_pad(output_path: Path, duration_sec: float = 60.0, sample_rate: int = 48000):
    """
    Synthesizes a deep cinematic cyberpunk drone/pad chord:
    D minor (D2, A2, F3, C4) with slow LFO pulse and sub-bass resonance.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    
    # Fundamental frequencies for cinematic Dm7 (D2=73.42Hz, A2=110Hz, F3=174.6Hz, C4=261.6Hz)
    freqs = [73.42, 110.0, 174.61, 261.63, 36.71] # 36.71Hz is sub-bass D1
    
    signal = np.zeros_like(t)
    for i, f in enumerate(freqs):
        # Detuned oscillators for rich chorus effect
        osc1 = np.sin(2 * np.pi * f * t)
        osc2 = np.sin(2 * np.pi * (f * 1.003) * t)
        
        # Slow LFO (0.15 Hz to 0.3 Hz) for breathing pulsation
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (0.1 + 0.05 * i) * t)
        weight = 0.25 if f > 100 else 0.4
        signal += (osc1 + osc2) * 0.5 * lfo * weight

    # Soft tape saturation curve to prevent harsh clipping
    signal = np.tanh(signal * 0.8)
    
    # Smooth fade in and fade out (2 seconds)
    fade_len = int(sample_rate * 2.0)
    if len(signal) > 2 * fade_len:
        signal[:fade_len] *= np.linspace(0, 1, fade_len)
        signal[-fade_len:] *= np.linspace(1, 0, fade_len)

    # Normalize to -18 dBFS for perfect background music bed
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val * 0.25

    # Convert to 16-bit PCM WAV
    audio_int16 = (signal * 32767).astype(np.int16)

    # Make stereo
    stereo = np.column_stack((audio_int16, audio_int16))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())

    return output_path

def generate_whoosh_sfx(output_path: Path, duration_sec: float = 0.7, sample_rate: int = 48000):
    """Synthesizes a clean cinematic whoosh transition sound."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    
    # White noise base
    noise = np.random.uniform(-1.0, 1.0, len(t))
    
    # Frequency sweep modulation (whoosh curve)
    # Bell curve envelope
    center = duration_sec / 2.0
    envelope = np.exp(-((t - center) ** 2) / (2 * (0.12 ** 2)))
    
    # Low frequency sweep
    sweep_freq = 150 + 800 * envelope
    sine_sweep = np.sin(2 * np.pi * sweep_freq * t)
    
    combined = (noise * 0.4 + sine_sweep * 0.6) * envelope
    combined = np.tanh(combined * 1.2) * 0.5
    
    audio_int16 = (combined * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())

    return output_path

def generate_click_sfx(output_path: Path, duration_sec: float = 0.08, sample_rate: int = 48000):
    """Synthesizes a high-tech UI digital click/blip for data points."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    freq = 2400.0  # Crisp tech chirp
    decay = np.exp(-t * 65.0)
    signal = np.sin(2 * np.pi * freq * t) * decay * 0.4
    
    audio_int16 = (signal * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))

    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo.tobytes())

    return output_path

