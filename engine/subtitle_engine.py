"""
Kinetic Typography & ASS Subtitle Engine
Generates high-retention animated subtitles with keyword color pop,
bold drop shadows, and exact millisecond alignment.
"""

from pathlib import Path

def format_ass_timestamp(seconds: float) -> str:
    """Converts seconds into ASS subtitle timestamp format: H:MM:SS.cs"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def generate_ass_subtitles(timeline_cues: list, output_path: Path, video_type: str = "short", width: int = 1080, height: int = 1920):
    """
    Builds an Advanced SubStation Alpha (.ass) file with karaoke color highlights.
    Shorts: large centered text (Impact 74pt), safe from YouTube UI overlay zones.
    Long: bottom documentary subtitles (Arial Bold 48pt).
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if video_type == "short":
        font_name = "Impact"
        font_size = 76
        # Alignment 2 = Bottom-center; MarginV 620 keeps text out of the YouTube Shorts title/audio bar
        margin_v = 640
        primary_color = "&H00FFFFFF"    # White
        highlight_color = "&H00E6FF00"  # Electric Gold/Cyan (&H00BBGGRR)
        outline_color = "&H00000000"    # Black outline
        back_color = "&H80000000"       # Semi-transparent shadow
        outline_width = 6
        shadow_depth = 4
    else:
        font_name = "Arial"
        font_size = 46
        margin_v = 130
        primary_color = "&H00FFFFFF"
        highlight_color = "&H00E6FF00"
        outline_color = "&H00000000"
        back_color = "&HB0000000"
        outline_width = 4
        shadow_depth = 3

    header = f"""[Script Info]
Title: Machine Economy Dynamic Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: {width}
PlayResY: {height}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},{back_color},-1,0,0,0,100,100,2,0,1,{outline_width},{shadow_depth},2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines = []
    
    # Keyword patterns to automatically highlight with electric color
    highlight_keywords = {
        "AI", "A-I", "AGI", "A-G-I", "$40B", "$40 TRILLION", "BILLION", "TRILLION",
        "ROBOT", "ROBOTS", "MACHINE", "ECONOMY", "AUTONOMOUS", "COLLAPSE", "REPLACE",
        "2027", "2028", "CAPITAL", "MONEY", "FUTURE", "OBSOLETE", "WALL STREET"
    }

    for cue in timeline_cues:
        start_sec = cue["start_ms"] / 1000.0
        end_sec = cue["end_ms"] / 1000.0
        text = cue["text"].strip()

        # Split longer sentences into 3-5 word punchy chunks
        words = text.split()
        if len(words) <= 5:
            # Highlight keyword if present
            colored_words = []
            for w in words:
                clean_w = w.strip(".,!?:;\"'").upper()
                if clean_w in highlight_keywords or any(k in clean_w for k in ["$", "%"]):
                    colored_words.append(f"{{\\c{highlight_color}\\b1}}{w}{{\\c{primary_color}\\b0}}")
                else:
                    colored_words.append(w)
            
            line_text = " ".join(colored_words)
            dialogue_lines.append(
                f"Dialogue: 0,{format_ass_timestamp(start_sec)},{format_ass_timestamp(end_sec)},Default,,0,0,0,,{line_text}"
            )
        else:
            # Subdivide sentence duration proportionally across word groups
            group_size = 4
            num_groups = (len(words) + group_size - 1) // group_size
            total_duration = end_sec - start_sec
            group_duration = total_duration / num_groups

            for g_idx in range(num_groups):
                g_start = start_sec + g_idx * group_duration
                g_end = min(end_sec, g_start + group_duration)
                group_words = words[g_idx * group_size : (g_idx + 1) * group_size]

                colored_words = []
                for w in group_words:
                    clean_w = w.strip(".,!?:;\"'").upper()
                    if clean_w in highlight_keywords or any(k in clean_w for k in ["$", "%"]):
                        colored_words.append(f"{{\\c{highlight_color}\\b1}}{w}{{\\c{primary_color}\\b0}}")
                    else:
                        colored_words.append(w)

                line_text = " ".join(colored_words)
                dialogue_lines.append(
                    f"Dialogue: 0,{format_ass_timestamp(g_start)},{format_ass_timestamp(g_end)},Default,,0,0,0,,{line_text}"
                )

    full_content = header + "\n".join(dialogue_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)

    return output_path

