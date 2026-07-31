"""
make_portrait_svg.py — Generate a halftone dot-matrix portrait SVG.

Instead of ASCII characters, this uses circles of varying radii to
represent brightness. Darker areas get larger dots, lighter areas
get smaller dots (or no dot at all). This preserves facial features
much better than character-based ASCII art.

The result is an animated SVG where dots fade in with a radial sweep
from the center outward.

Usage:
    python scripts/make_portrait_svg.py [source-prepped.png] [output.svg]
"""

import sys
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# --- Configuration ---
GRID_COLS = 80       # number of dot columns
GRID_ROWS = 90       # number of dot rows
DOT_SPACING = 6.0    # pixels between dot centers
MAX_RADIUS = 2.8     # max dot radius for darkest pixels
MIN_RADIUS = 0.3     # min dot radius for lightest visible pixels
BRIGHTNESS_CUTOFF = 0.85  # pixels brighter than this get no dot

# SVG styling
BG_COLOR = "#0d1117"
DOT_COLOR = "#c9d1d9"

# Animation
ANIM_DURATION = 2.5  # total reveal time in seconds


def image_to_dots(img_path: str) -> list[tuple[float, float, float]]:
    """
    Convert image to a list of (x, y, radius) dot positions.
    Returns dots sorted by distance from center for the radial reveal.
    """
    img = Image.open(img_path).convert("L")

    # Apply slight gaussian blur to smooth out noise
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    # Resize to grid dimensions
    img = img.resize((GRID_COLS, GRID_ROWS), Image.LANCZOS)
    pixels = np.array(img, dtype=np.float64) / 255.0  # normalize to 0-1

    dots = []
    cx = GRID_COLS / 2.0
    cy = GRID_ROWS / 2.0

    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            brightness = pixels[row, col]

            # Skip very bright pixels (background)
            if brightness > BRIGHTNESS_CUTOFF:
                continue

            # Map brightness to radius: dark=large dot, light=small dot
            # Invert: 0 (black) -> MAX_RADIUS, BRIGHTNESS_CUTOFF (light) -> MIN_RADIUS
            t = brightness / BRIGHTNESS_CUTOFF  # 0 to 1
            radius = MAX_RADIUS * (1 - t) + MIN_RADIUS * t

            if radius < MIN_RADIUS:
                continue

            x = col * DOT_SPACING + DOT_SPACING / 2
            y = row * DOT_SPACING + DOT_SPACING / 2

            # Distance from center (for animation ordering)
            dist = math.sqrt((col - cx) ** 2 + (row - cy) ** 2)
            dots.append((x, y, radius, dist))

    # Sort by distance from center
    dots.sort(key=lambda d: d[3])
    return dots


def build_svg(dots: list[tuple], output_path: str) -> None:
    """Build SVG with radial fade-in animation."""
    width = GRID_COLS * DOT_SPACING + DOT_SPACING
    height = GRID_ROWS * DOT_SPACING + DOT_SPACING
    padding = 16
    total_width = width + padding * 2
    total_height = height + padding * 2

    max_dist = max(d[3] for d in dots) if dots else 1.0

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {total_width:.0f} {total_height:.0f}" '
        f'width="{total_width:.0f}" height="{total_height:.0f}">\n'
    )

    # Background
    parts.append(
        f'  <rect width="{total_width:.0f}" height="{total_height:.0f}" '
        f'fill="{BG_COLOR}" rx="8" />\n'
    )

    # Animation style — use delay classes (bands) to reduce file size
    NUM_BANDS = 40  # number of animation delay bands
    band_duration = ANIM_DURATION / NUM_BANDS

    parts.append("  <style>\n")
    parts.append(
        "    @keyframes dotFadeIn {\n"
        "      from { opacity: 0; transform: scale(0); }\n"
        "      to { opacity: 1; transform: scale(1); }\n"
        "    }\n"
    )
    parts.append(
        "    .dot {\n"
        "      opacity: 0;\n"
        "      animation: dotFadeIn 0.2s ease-out forwards;\n"
        "      transform-origin: center;\n"
        "    }\n"
    )
    for b in range(NUM_BANDS):
        delay = b * band_duration
        parts.append(f"    .d{b} {{ animation-delay: {delay:.2f}s; }}\n")
    parts.append("  </style>\n")

    # Draw dots with band-based animation delays
    for i, (x, y, radius, dist) in enumerate(dots):
        band = min(int((dist / max_dist) * NUM_BANDS), NUM_BANDS - 1)
        px = x + padding
        py = y + padding

        parts.append(
            f'  <circle class="dot d{band}" cx="{px:.1f}" cy="{py:.1f}" r="{radius:.2f}" '
            f'fill="{DOT_COLOR}" />\n'
        )

    parts.append("</svg>\n")

    Path(output_path).write_text("".join(parts), encoding="utf-8")
    print(f"[make_portrait_svg] Written {output_path} ({len(dots)} dots, {GRID_COLS}x{GRID_ROWS} grid)")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "mukund-ascii.svg"

    if not Path(input_file).exists():
        print(f"Error: '{input_file}' not found. Run prep_photo.py first.")
        sys.exit(1)

    dots = image_to_dots(input_file)
    build_svg(dots, output_file)
