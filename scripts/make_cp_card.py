"""
make_cp_card.py — Generate an animated competitive programming stats SVG.

Renders a terminal-style table of platform ratings with colored
accents per platform, plus a highlights footer. Rows fade + slide in
with a stagger, matching the info-card.svg style.

Usage:
    python scripts/make_cp_card.py   # writes cp-card.svg
"""

import os
from pathlib import Path

OUTPUT = "cp-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

# --- Content ---
TITLE = "neofetch --competitive"

# (platform, color, rating, solved)
ROWS = [
    ("LeetCode", "#FFA116", "1668  (Top 15%)", "200+"),
    ("CodeChef", "#5B4638", "1682  (3\u2605)", "500+"),
    ("Codeforces", "#1F8ACB", "1202  (Pupil)", "\u2014"),
]

HIGHLIGHTS = [
    "700+ problems solved across platforms",
    "Top 20 in CodeChef START196",
    "Top 10 in Diamond League",
]

# --- Colors ---
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
HEADER_COLOR = "#c9d1d9"
LABEL_COLOR = "#8b949e"
VALUE_COLOR = "#c9d1d9"
ACCENT = "#58a6ff"
DIVIDER_COLOR = "#21262d"

# --- Layout ---
FONT_SIZE = 13
LINE_HEIGHT = 24
PADDING_X = 24
PADDING_Y = 22
CARD_WIDTH = 560
CARD_RADIUS = 8
COL_PLATFORM_X = 0
COL_RATING_X = 150
COL_SOLVED_X = 340

LINE_DELAY = 0.15
LINE_DURATION = 0.4


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg() -> str:
    # total lines: title + header + divider + 3 rows + gap + 3 highlight lines
    num_anim_lines = 2 + len(ROWS) + 1 + len(HIGHLIGHTS)
    content_lines = 1 + 1 + 1 + len(ROWS) + 1 + len(HIGHLIGHTS)
    card_height = content_lines * LINE_HEIGHT + PADDING_Y * 2 + 10

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {CARD_WIDTH} {card_height}" '
        f'width="{CARD_WIDTH}" height="{card_height}">\n'
    )

    if not STATIC:
        parts.append("  <style>\n")
        parts.append(
            "    @keyframes fadeSlideIn {\n"
            "      from { opacity: 0; transform: translateX(-8px); }\n"
            "      to { opacity: 1; transform: translateX(0); }\n"
            "    }\n"
        )
        parts.append(
            "    .cp-line {\n"
            "      opacity: 0;\n"
            "      animation: fadeSlideIn 0.4s ease forwards;\n"
            "    }\n"
        )
        for i in range(num_anim_lines):
            parts.append(
                f"    .cl-{i} {{ animation-delay: {i * LINE_DELAY:.2f}s; }}\n"
            )
        parts.append("  </style>\n")

    # Card background
    parts.append(
        f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="{card_height}" '
        f'rx="{CARD_RADIUS}" ry="{CARD_RADIUS}" '
        f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1" />\n'
    )

    y = PADDING_Y + FONT_SIZE
    line_idx = 0
    mono = "font-family=\"'Courier New', monospace\""

    # Title line
    cls = f' class="cp-line cl-{line_idx}"' if not STATIC else ""
    parts.append(f'  <g{cls}>\n')
    parts.append(
        f'    <text x="{PADDING_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{ACCENT}">&gt; <tspan fill="{HEADER_COLOR}">{esc(TITLE)}</tspan></text>\n'
    )
    parts.append("  </g>\n")
    y += LINE_HEIGHT * 1.4
    line_idx += 1

    # Column headers
    cls = f' class="cp-line cl-{line_idx}"' if not STATIC else ""
    parts.append(f'  <g{cls}>\n')
    parts.append(
        f'    <text x="{PADDING_X + COL_PLATFORM_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{LABEL_COLOR}">Platform</text>\n'
    )
    parts.append(
        f'    <text x="{PADDING_X + COL_RATING_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{LABEL_COLOR}">Rating</text>\n'
    )
    parts.append(
        f'    <text x="{PADDING_X + COL_SOLVED_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{LABEL_COLOR}">Solved</text>\n'
    )
    parts.append("  </g>\n")
    y += 10
    line_idx += 1

    # Divider line
    parts.append(
        f'  <line x1="{PADDING_X}" y1="{y}" x2="{CARD_WIDTH - PADDING_X}" y2="{y}" '
        f'stroke="{DIVIDER_COLOR}" stroke-width="1" />\n'
    )
    y += LINE_HEIGHT

    # Platform rows
    for platform, color, rating, solved in ROWS:
        cls = f' class="cp-line cl-{line_idx}"' if not STATIC else ""
        parts.append(f'  <g{cls}>\n')
        parts.append(
            f'    <circle cx="{PADDING_X + 4}" cy="{y - 4}" r="4" fill="{color}" />\n'
        )
        parts.append(
            f'    <text x="{PADDING_X + 14}" y="{y}" {mono} font-size="{FONT_SIZE}" '
            f'font-weight="bold" fill="{color}">{esc(platform)}</text>\n'
        )
        parts.append(
            f'    <text x="{PADDING_X + COL_RATING_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
            f'fill="{VALUE_COLOR}">{esc(rating)}</text>\n'
        )
        parts.append(
            f'    <text x="{PADDING_X + COL_SOLVED_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
            f'fill="{VALUE_COLOR}">{esc(solved)}</text>\n'
        )
        parts.append("  </g>\n")
        y += LINE_HEIGHT
        line_idx += 1

    # Divider before highlights
    y += 4
    parts.append(
        f'  <line x1="{PADDING_X}" y1="{y}" x2="{CARD_WIDTH - PADDING_X}" y2="{y}" '
        f'stroke="{DIVIDER_COLOR}" stroke-width="1" />\n'
    )
    y += LINE_HEIGHT

    # Highlights
    accent_colors = ["#f78166", "#d2a8ff", "#7ee787"]
    for i, highlight in enumerate(HIGHLIGHTS):
        cls = f' class="cp-line cl-{line_idx}"' if not STATIC else ""
        accent = accent_colors[i % len(accent_colors)]
        parts.append(f'  <g{cls}>\n')
        parts.append(
            f'    <text x="{PADDING_X}" y="{y}" {mono} font-size="{FONT_SIZE}" '
            f'fill="{accent}">\u2726</text>\n'
        )
        parts.append(
            f'    <text x="{PADDING_X + 16}" y="{y}" {mono} font-size="{FONT_SIZE}" '
            f'fill="{VALUE_COLOR}">{esc(highlight)}</text>\n'
        )
        parts.append("  </g>\n")
        y += LINE_HEIGHT
        line_idx += 1

    parts.append("</svg>\n")
    return "".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"[make_cp_card] Written {OUTPUT} ({'static' if STATIC else 'animated'})")
