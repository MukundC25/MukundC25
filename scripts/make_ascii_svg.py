"""
make_ascii_svg.py — Convert a prepped grayscale image into an animated,
monochrome ASCII-art SVG that "types" itself row by row.

The SVG uses SMIL animations (clip-rect wipe per row) so it plays
natively on GitHub without JavaScript.

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png] [output.svg]
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

# Density ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"

# Grid dimensions (characters)
COLS = 100
ROWS = 53

# SVG styling
FONT_SIZE = 10
CHAR_W = 6.0  # monospace char width in px
CHAR_H = 10.0  # line height in px
FG_COLOR = "#c9d1d9"  # light gray on dark bg
BG_COLOR = "#0d1117"  # GitHub dark theme

# Animation timing
ROW_DURATION = 0.06  # seconds per row wipe
CURSOR_WIDTH = 3  # chars wide "cursor block"


def image_to_ascii(img_path: str) -> list[str]:
    """Convert grayscale image to a grid of ASCII characters."""
    img = Image.open(img_path).convert("L")
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    pixels = np.array(img)

    lines = []
    for row in pixels:
        line = ""
        for val in row:
            # Map 0-255 to ramp index (bright=space, dark=dense)
            idx = int(val / 255 * (len(RAMP) - 1))
            # Invert: bright pixels -> sparse chars
            line += RAMP[len(RAMP) - 1 - idx]
        lines.append(line)
    return lines


def build_svg(lines: list[str], output_path: str) -> None:
    """Build an SVG with row-by-row typing animation."""
    width = COLS * CHAR_W + 20
    height = ROWS * CHAR_H + 20

    total_anim_time = ROWS * ROW_DURATION + 1.0  # +1s pause before freeze

    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n'
    )

    # Background
    svg_parts.append(
        f'  <rect width="{width}" height="{height}" fill="{BG_COLOR}" />\n'
    )

    # Style
    svg_parts.append(
        f"  <style>\n"
        f"    text {{\n"
        f"      font-family: 'Courier New', monospace;\n"
        f"      font-size: {FONT_SIZE}px;\n"
        f"      fill: {FG_COLOR};\n"
        f"      white-space: pre;\n"
        f"    }}\n"
        f"  </style>\n"
    )

    # Each row is a <text> inside a <g> with a clip-path that wipes left-to-right
    for i, line in enumerate(lines):
        y = 14 + i * CHAR_H
        delay = i * ROW_DURATION
        clip_id = f"clip-r{i}"

        # Clip rectangle that animates from width=0 to full width
        svg_parts.append(f'  <clipPath id="{clip_id}">\n')
        svg_parts.append(
            f'    <rect x="10" y="{y - CHAR_H + 2}" width="0" height="{CHAR_H + 2}">\n'
        )
        svg_parts.append(
            f'      <animate attributeName="width" '
            f'from="0" to="{COLS * CHAR_W}" '
            f'begin="{delay:.2f}s" dur="{ROW_DURATION * 8:.2f}s" '
            f'fill="freeze" />\n'
        )
        svg_parts.append(f"    </rect>\n")
        svg_parts.append(f"  </clipPath>\n")

        # Escape XML special chars
        escaped = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

        svg_parts.append(f'  <text x="10" y="{y}" clip-path="url(#{clip_id})">')
        svg_parts.append(escaped)
        svg_parts.append("</text>\n")

    # Cursor block that rides down row by row
    cursor_h = CHAR_H
    cursor_w = CURSOR_WIDTH * CHAR_W
    svg_parts.append(
        f'  <rect x="10" y="4" width="{cursor_w}" height="{cursor_h}" '
        f'fill="{FG_COLOR}" opacity="0.7">\n'
    )
    # Animate X position across each row
    svg_parts.append(
        f'    <animate attributeName="x" '
        f'values="{";".join(["10"] + [str(10 + COLS * CHAR_W)] * ROWS)}" '
        f'keyTimes="{";".join([f"{i / ROWS:.4f}" for i in range(ROWS + 1)])}" '
        f'dur="{ROWS * ROW_DURATION:.2f}s" fill="freeze" />\n'
    )
    # Animate Y position down rows
    y_values = [str(4 + i * CHAR_H) for i in range(ROWS)] + [
        str(4 + (ROWS - 1) * CHAR_H)
    ]
    svg_parts.append(
        f'    <animate attributeName="y" '
        f'values="{";".join(y_values)}" '
        f'keyTimes="{";".join([f"{i / ROWS:.4f}" for i in range(ROWS + 1)])}" '
        f'dur="{ROWS * ROW_DURATION:.2f}s" fill="freeze" />\n'
    )
    # Fade out cursor at the end
    svg_parts.append(
        f'    <animate attributeName="opacity" '
        f'from="0.7" to="0" '
        f'begin="{ROWS * ROW_DURATION:.2f}s" dur="0.3s" fill="freeze" />\n'
    )
    svg_parts.append(f"  </rect>\n")

    svg_parts.append("</svg>\n")

    Path(output_path).write_text("".join(svg_parts), encoding="utf-8")
    print(f"[make_ascii_svg] Written {output_path} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "mukund-ascii.svg"

    if not Path(input_file).exists():
        print(f"Error: '{input_file}' not found. Run prep_photo.py first.")
        sys.exit(1)

    lines = image_to_ascii(input_file)
    build_svg(lines, output_file)
