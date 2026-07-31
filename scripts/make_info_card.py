"""
make_info_card.py — Generate a neofetch-style info card SVG.

Displays role, stack, highlights in a terminal-like panel with
line-by-line fade+slide animation (SMIL/CSS keyframes).

Set STATIC=1 env var to emit a frozen frame (no animation).

Usage:
    python scripts/make_info_card.py   # writes info-card.svg
"""

import os
from pathlib import Path

# --- Configuration ---
OUTPUT = "info-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

# Card content (neofetch-style key: value pairs)
TITLE_USER = "mukund"
TITLE_HOST = "github"
SEPARATOR_LEN = 24

INFO_LINES = [
    ("Now", "GSoC'26 @ FOSSASIA · Django Plugin Dev"),
    ("Prev", "SortUs · AI/ML Intern · FastAPI + RF"),
    ("Stack", "Python · TypeScript · React · FastAPI"),
    ("AI/ML", "LangChain · RAG · Neo4j · Llama3"),
    ("DB", "PostgreSQL · MongoDB · Redis · SQLite"),
    ("Cloud", "AWS · GCP · Docker · Vercel"),
    ("Editor", "Kiro / Cursor · Claude · Neovim"),
    ("CP", "700+ solved · CodeChef 3★ · LC 1668"),
    ("Focus", "Agentic AI · Full-Stack · Open Source"),
]

# Colors
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
TITLE_COLOR = "#58a6ff"
KEY_COLOR = "#79c0ff"
VALUE_COLOR = "#c9d1d9"
SEPARATOR_COLOR = "#484f58"
ACCENT_COLORS = ["#f78166", "#d2a8ff", "#7ee787", "#79c0ff", "#ffa657", "#ff7b72"]

# Layout
FONT_SIZE = 13
LINE_HEIGHT = 22
PADDING_X = 24
PADDING_Y = 24
CARD_WIDTH = 460
CARD_RADIUS = 8

# Animation
LINE_DELAY = 0.15  # stagger between lines (seconds)
LINE_DURATION = 0.4  # fade-in duration per line


def build_svg() -> str:
    # Calculate height
    num_lines = 2 + len(INFO_LINES)  # title + separator + info lines
    content_height = num_lines * LINE_HEIGHT + 16
    card_height = content_height + PADDING_Y * 2

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {CARD_WIDTH} {card_height}" '
        f'width="{CARD_WIDTH}" height="{card_height}">\n'
    )

    # Styles with keyframe animation
    if not STATIC:
        parts.append("  <style>\n")
        parts.append(
            "    @keyframes fadeSlideIn {\n"
            "      from { opacity: 0; transform: translateX(-8px); }\n"
            "      to { opacity: 1; transform: translateX(0); }\n"
            "    }\n"
        )
        parts.append(
            "    .info-line {\n"
            "      opacity: 0;\n"
            "      animation: fadeSlideIn 0.4s ease forwards;\n"
            "    }\n"
        )
        for i in range(num_lines):
            delay = i * LINE_DELAY
            parts.append(
                f"    .line-{i} {{ animation-delay: {delay:.2f}s; }}\n"
            )
        parts.append("  </style>\n")

    # Background card
    parts.append(
        f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="{card_height}" '
        f'rx="{CARD_RADIUS}" ry="{CARD_RADIUS}" '
        f'fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1" />\n'
    )

    y = PADDING_Y + FONT_SIZE
    line_idx = 0

    # Title line: mukund@github
    cls = f' class="info-line line-{line_idx}"' if not STATIC else ""
    parts.append(f'  <g{cls}>\n')
    parts.append(
        f'    <text x="{PADDING_X}" y="{y}" '
        f'font-family="\'Courier New\', monospace" font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{TITLE_COLOR}">'
        f'{TITLE_USER}<tspan fill="{VALUE_COLOR}">@</tspan>{TITLE_HOST}'
        f"</text>\n"
    )
    parts.append("  </g>\n")
    y += LINE_HEIGHT
    line_idx += 1

    # Separator line
    cls = f' class="info-line line-{line_idx}"' if not STATIC else ""
    separator = "─" * SEPARATOR_LEN
    parts.append(f'  <g{cls}>\n')
    parts.append(
        f'    <text x="{PADDING_X}" y="{y}" '
        f'font-family="\'Courier New\', monospace" font-size="{FONT_SIZE}" '
        f'fill="{SEPARATOR_COLOR}">{separator}</text>\n'
    )
    parts.append("  </g>\n")
    y += LINE_HEIGHT
    line_idx += 1

    # Info lines
    for i, (key, value) in enumerate(INFO_LINES):
        cls = f' class="info-line line-{line_idx}"' if not STATIC else ""
        accent = ACCENT_COLORS[i % len(ACCENT_COLORS)]
        parts.append(f'  <g{cls}>\n')
        # Colored bullet
        parts.append(
            f'    <text x="{PADDING_X}" y="{y}" '
            f'font-family="\'Courier New\', monospace" font-size="{FONT_SIZE}" '
            f'fill="{accent}">●</text>\n'
        )
        # Key
        parts.append(
            f'    <text x="{PADDING_X + 16}" y="{y}" '
            f'font-family="\'Courier New\', monospace" font-size="{FONT_SIZE}" '
            f'font-weight="bold" fill="{KEY_COLOR}">{key}'
            f'<tspan fill="{SEPARATOR_COLOR}"> ~ </tspan>'
            f'<tspan fill="{VALUE_COLOR}" font-weight="normal">{value}</tspan>'
            f"</text>\n"
        )
        parts.append("  </g>\n")
        y += LINE_HEIGHT
        line_idx += 1

    parts.append("</svg>\n")
    return "".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"[make_info_card] Written {OUTPUT} ({'static' if STATIC else 'animated'})")
