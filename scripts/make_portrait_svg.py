"""
make_portrait_svg.py — Embed cartoon photo in SVG with vertical wipe reveal.

Clean top-to-bottom reveal with a scan line riding the edge.
No particles, no gradients, no borders.

Usage:
    python scripts/make_portrait_svg.py [photo.jpg] [output.svg]
"""

import sys
import base64
from pathlib import Path

from PIL import Image
import io

# --- Configuration ---
OUTPUT_W = 380
OUTPUT_H = 340
BORDER_RADIUS = 12
REVEAL_DURATION = 2.5


def load_photo(img_path: str, width: int, height: int) -> str:
    """Load photo, resize to fill, encode as base64."""
    img = Image.open(img_path).convert("RGB")

    img_ratio = img.width / img.height
    target_ratio = width / height

    if img_ratio > target_ratio:
        new_h = height
        new_w = int(height * img_ratio)
    else:
        new_w = width
        new_h = int(width / img_ratio)

    img = img.resize((new_w, new_h), Image.LANCZOS)

    left = (new_w - width) // 2
    top = (new_h - height) // 2
    img = img.crop((left, top, left + width, top + height))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    return f"data:image/png;base64,{b64}"


def build_svg(photo_data: str, output_path: str) -> None:
    """Build SVG with vertical wipe reveal animation."""
    w = OUTPUT_W
    h = OUTPUT_H

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">\n'
    )

    parts.append("  <defs>\n")
    parts.append(
        f'    <clipPath id="frame">\n'
        f'      <rect width="{w}" height="{h}" rx="{BORDER_RADIUS}" />\n'
        f'    </clipPath>\n'
    )
    parts.append(
        f'    <clipPath id="reveal">\n'
        f'      <rect x="0" y="0" width="{w}" height="0">\n'
        f'        <animate attributeName="height" '
        f'from="0" to="{h}" '
        f'dur="{REVEAL_DURATION}s" fill="freeze" />\n'
        f'      </rect>\n'
        f'    </clipPath>\n'
    )
    parts.append("  </defs>\n")

    parts.append(
        f'  <rect width="{w}" height="{h}" rx="{BORDER_RADIUS}" fill="#0d1117" />\n'
    )

    parts.append(f'  <g clip-path="url(#frame)">\n')
    parts.append(f'    <g clip-path="url(#reveal)">\n')
    parts.append(
        f'      <image x="0" y="0" width="{w}" height="{h}" '
        f'href="{photo_data}" />\n'
    )
    parts.append(f'    </g>\n')

    # Scan line
    parts.append(
        f'    <rect x="0" y="0" width="{w}" height="2" fill="#58a6ff" opacity="0.7" rx="1">\n'
        f'      <animate attributeName="y" '
        f'from="0" to="{h}" '
        f'dur="{REVEAL_DURATION}s" fill="freeze" />\n'
        f'      <animate attributeName="opacity" '
        f'values="0.7;0.7;0" keyTimes="0;0.85;1" '
        f'dur="{REVEAL_DURATION}s" fill="freeze" />\n'
        f'    </rect>\n'
    )

    parts.append("  </g>\n")
    parts.append("</svg>\n")

    Path(output_path).write_text("".join(parts), encoding="utf-8")
    print(f"[make_portrait_svg] Written {output_path} (wipe reveal, clean)")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "img2.jpg"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "mukund-ascii.svg"

    if not Path(input_file).exists():
        print(f"Error: '{input_file}' not found.")
        sys.exit(1)

    photo_data = load_photo(input_file, OUTPUT_W, OUTPUT_H)
    build_svg(photo_data, output_file)
