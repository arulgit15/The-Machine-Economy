"""
High-CTR Algorithmic Thumbnail Engine
Generates 1280x720 high-contrast thumbnails following the 3-Word Rule,
intense color contrast, HUD framing, and mobile readability.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from config.settings import THEME

def create_high_ctr_thumbnail(
    title_text: str,
    output_path: Path,
    width: int = 1280,
    height: int = 720,
    sub_tag: str = "SPECULATIVE TECH // 2027"
) -> Path:
    """
    Renders a high-converting thumbnail with bold typography, high-contrast drop shadows,
    cyber gradient lighting, and HUD aesthetic brackets.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (width, height), "#0B0C10")
    draw = ImageDraw.Draw(img)

    # Background: Dramatic radial glow from bottom-right (cyan/amber tension)
    glow_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.ellipse(
        [(width - 450, height - 450), (width + 350, height + 350)],
        fill=(0, 242, 254, 85)
    )
    glow_draw.ellipse(
        [(-200, -200), (500, 500)],
        fill=(255, 230, 0, 45)
    )
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(120))
    img.paste(glow_img, (0, 0), glow_img)

    # Cyber Grid Accent lines
    for y in range(400, height, 45):
        draw.line([(0, y), (width, y)], fill=(31, 40, 51), width=1)

    # Fonts
    try:
        font_sub = ImageFont.truetype("arialbd.ttf", 32)
        font_main = ImageFont.truetype("impact.ttf", 108)
    except Exception:
        font_sub = ImageFont.load_default()
        font_main = ImageFont.load_default()

    # Draw Category Tag Pill
    tag_x, tag_y = 70, 75
    draw.rounded_rectangle(
        [(tag_x, tag_y), (tag_x + 440, tag_y + 54)],
        radius=8,
        fill=(15, 23, 42),
        outline=(102, 252, 241),
        width=2
    )
    draw.text((tag_x + 22, tag_y + 10), sub_tag, font=font_sub, fill=THEME["accent_cyan"])

    # Format Main Text (Split into 2 or 3 lines max for punchy readability)
    words = title_text.upper().split()
    if len(words) > 3:
        line1 = " ".join(words[:2])
        line2 = " ".join(words[2:])
        lines = [line1, line2]
    else:
        lines = [" ".join(words)]

    text_start_y = 175
    for i, line in enumerate(lines):
        line_y = text_start_y + i * 125
        
        # Draw Deep Black Drop Shadow (4-direction stroke for maximum legibility on mobile)
        shadow_offset = 6
        for dx in [-shadow_offset, 0, shadow_offset]:
            for dy in [-shadow_offset, 0, shadow_offset]:
                draw.text((70 + dx, line_y + dy), line, font=font_main, fill=(0, 0, 0))

        # Main text color: Alternate line 1 (Electric Yellow) and line 2 (Pure White)
        color = THEME["accent_gold"] if i == 0 else "#FFFFFF"
        draw.text((70, line_y), line, font=font_main, fill=color)

    # Frame Border with Cyber Bracket Accents
    border_color = (102, 252, 241)
    b_len = 60
    b_thick = 6
    margin = 25
    # Corners
    # Top-Left
    draw.line([(margin, margin), (margin + b_len, margin)], fill=border_color, width=b_thick)
    draw.line([(margin, margin), (margin, margin + b_len)], fill=border_color, width=b_thick)
    # Top-Right
    draw.line([(width - margin, margin), (width - margin - b_len, margin)], fill=border_color, width=b_thick)
    draw.line([(width - margin, margin), (width - margin, margin + b_len)], fill=border_color, width=b_thick)
    # Bottom-Left
    draw.line([(margin, height - margin), (margin + b_len, height - margin)], fill=border_color, width=b_thick)
    draw.line([(margin, height - margin), (margin, height - margin - b_len)], fill=border_color, width=b_thick)
    # Bottom-Right
    draw.line([(width - margin, height - margin), (width - margin - b_len, height - margin)], fill=border_color, width=b_thick)
    draw.line([(width - margin, height - margin), (width - margin, height - margin - b_len)], fill=border_color, width=b_thick)

    img.save(str(output_path), "JPEG", quality=95)
    return output_path

