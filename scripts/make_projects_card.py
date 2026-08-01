"""
make_projects_card.py — Generate an animated projects table SVG.

Renders a terminal-style table: Project | What it does | Stack,
with project names as colored links (visual only — see README for
actual clickable links) and rows fading in with a stagger.

Usage:
    python scripts/make_projects_card.py   # writes projects-card.svg
"""

import os
import textwrap
from pathlib import Path

OUTPUT = "projects-card.svg"
STATIC = os.environ.get("STATIC", "0") == "1"

TITLE = "ls projects/"

# (name, description, stack, accent_color)
PROJECTS = [
    (
        "EKIA",
        "Agentic AI code debugging assistant \u2014 5-node LangGraph pipeline with FAISS + Neo4j GraphRAG",
        "Python, FastAPI, LangGraph, Llama3, Neo4j",
        "#58a6ff",
    ),
    (
        "Refine",
        "AI resume optimizer raising ATS scores by 45%",
        "FastAPI, TypeScript, Gemini 2.5, PostgreSQL",
        "#d2a8ff",
    ),
    (
        "FinMate",
        "SMS-based UPI expense tracker (92%+ parse accuracy)",
        "React Native, TypeScript, SQLite, Supabase",
        "#7ee787",
    ),
    (
        "Apta",
        "Smart lifestyle recommender \u2014 TF-IDF + cosine similarity",
        "Next.js, FastAPI, scikit-learn",
        "#f78166",
    ),
    (
        "V-Track",
        "Vehicle tracking & security with ESP32 + Google Geolocation",
        "React, Flask, Google Maps API, Docker",
        "#ffa657",
    ),
]

# --- Colors ---
BG_COLOR = "#0d1117"
BORDER_COLOR = "#30363d"
HEADER_BG = "#161b22"
HEADER_COLOR = "#8b949e"
DESC_COLOR = "#c9d1d9"
STACK_COLOR = "#8b949e"
ROW_ALT_BG = "#11151c"
DIVIDER_COLOR = "#21262d"

# --- Layout ---
FONT_SIZE = 12.5
NAME_COL_X = 20
NAME_COL_W = 90
DESC_COL_X = 120
DESC_COL_W = 330
STACK_COL_X = 480
CARD_WIDTH = 800
ROW_PADDING_Y = 14
LINE_HEIGHT = 16
HEADER_HEIGHT = 34
DESC_WRAP_WIDTH = 42
STACK_WRAP_WIDTH = 24

ROW_DELAY = 0.18
ROW_DURATION = 0.4


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(text, width=width) or [""]


def build_svg() -> str:
    mono = "font-family=\"'Courier New', monospace\""

    # Precompute wrapped lines and row heights
    row_data = []
    for name, desc, stack, color in PROJECTS:
        desc_lines = wrap(desc, DESC_WRAP_WIDTH)
        stack_lines = wrap(stack, STACK_WRAP_WIDTH)
        num_lines = max(len(desc_lines), len(stack_lines), 1)
        row_h = ROW_PADDING_Y * 2 + num_lines * LINE_HEIGHT
        row_data.append((name, desc_lines, stack_lines, color, row_h))

    title_bar_h = 40
    total_height = title_bar_h + HEADER_HEIGHT + sum(r[4] for r in row_data) + 8

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {CARD_WIDTH} {total_height:.0f}" '
        f'width="{CARD_WIDTH}" height="{total_height:.0f}">\n'
    )

    if not STATIC:
        parts.append("  <style>\n")
        parts.append(
            "    @keyframes rowFadeIn {\n"
            "      from { opacity: 0; transform: translateY(6px); }\n"
            "      to { opacity: 1; transform: translateY(0); }\n"
            "    }\n"
        )
        parts.append(
            "    .proj-row {\n"
            "      opacity: 0;\n"
            "      animation: rowFadeIn 0.4s ease forwards;\n"
            "    }\n"
        )
        for i in range(len(row_data) + 1):
            parts.append(
                f"    .pr-{i} {{ animation-delay: {i * ROW_DELAY:.2f}s; }}\n"
            )
        parts.append("  </style>\n")

    # Outer card
    parts.append(
        f'  <rect x="0" y="0" width="{CARD_WIDTH}" height="{total_height:.0f}" '
        f'rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1" />\n'
    )

    # Title bar
    cls = f' class="proj-row pr-0"' if not STATIC else ""
    parts.append(f'  <g{cls}>\n')
    parts.append(
        f'    <rect x="0" y="0" width="{CARD_WIDTH}" height="{title_bar_h}" '
        f'rx="8" fill="{HEADER_BG}" />\n'
    )
    parts.append(
        f'    <rect x="0" y="{title_bar_h - 8}" width="{CARD_WIDTH}" height="8" fill="{HEADER_BG}" />\n'
    )
    # traffic-light dots
    for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'    <circle cx="{20 + i * 16}" cy="{title_bar_h / 2}" r="5" fill="{c}" />\n')
    parts.append(
        f'    <text x="{CARD_WIDTH / 2}" y="{title_bar_h / 2 + 4}" {mono} '
        f'font-size="13" fill="{HEADER_COLOR}" text-anchor="middle">'
        f'mukund@github ~ $ <tspan fill="#c9d1d9">{esc(TITLE)}</tspan></text>\n'
    )
    parts.append("  </g>\n")

    y = title_bar_h

    # Column headers
    header_y = y + HEADER_HEIGHT / 2 + 4
    parts.append(
        f'  <rect x="0" y="{y}" width="{CARD_WIDTH}" height="{HEADER_HEIGHT}" fill="{HEADER_BG}" opacity="0.4" />\n'
    )
    parts.append(
        f'  <text x="{NAME_COL_X}" y="{header_y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{HEADER_COLOR}">Project</text>\n'
    )
    parts.append(
        f'  <text x="{DESC_COL_X}" y="{header_y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{HEADER_COLOR}">What it does</text>\n'
    )
    parts.append(
        f'  <text x="{STACK_COL_X}" y="{header_y}" {mono} font-size="{FONT_SIZE}" '
        f'font-weight="bold" fill="{HEADER_COLOR}">Stack</text>\n'
    )
    y += HEADER_HEIGHT
    parts.append(
        f'  <line x1="0" y1="{y}" x2="{CARD_WIDTH}" y2="{y}" stroke="{DIVIDER_COLOR}" stroke-width="1" />\n'
    )

    # Rows
    for idx, (name, desc_lines, stack_lines, color, row_h) in enumerate(row_data):
        cls = f' class="proj-row pr-{idx + 1}"' if not STATIC else ""
        row_center_y = y + row_h / 2

        if idx % 2 == 1:
            parts.append(
                f'  <rect x="0" y="{y}" width="{CARD_WIDTH}" height="{row_h}" fill="{ROW_ALT_BG}" />\n'
            )

        parts.append(f'  <g{cls}>\n')

        # Project name (colored, underlined to suggest link)
        name_y = row_center_y + FONT_SIZE / 3
        parts.append(
            f'    <text x="{NAME_COL_X}" y="{name_y}" {mono} font-size="{FONT_SIZE}" '
            f'font-weight="bold" fill="{color}" text-decoration="underline">{esc(name)}</text>\n'
        )

        # Description (wrapped, vertically centered block)
        desc_start_y = row_center_y - (len(desc_lines) - 1) * LINE_HEIGHT / 2 + FONT_SIZE / 3
        for i, line in enumerate(desc_lines):
            parts.append(
                f'    <text x="{DESC_COL_X}" y="{desc_start_y + i * LINE_HEIGHT:.1f}" {mono} '
                f'font-size="{FONT_SIZE}" fill="{DESC_COLOR}">{esc(line)}</text>\n'
            )

        # Stack (wrapped, vertically centered block)
        stack_start_y = row_center_y - (len(stack_lines) - 1) * LINE_HEIGHT / 2 + FONT_SIZE / 3
        for i, line in enumerate(stack_lines):
            parts.append(
                f'    <text x="{STACK_COL_X}" y="{stack_start_y + i * LINE_HEIGHT:.1f}" {mono} '
                f'font-size="{FONT_SIZE}" fill="{STACK_COLOR}">{esc(line)}</text>\n'
            )

        parts.append("  </g>\n")

        y += row_h
        if idx < len(row_data) - 1:
            parts.append(
                f'  <line x1="0" y1="{y}" x2="{CARD_WIDTH}" y2="{y}" stroke="{DIVIDER_COLOR}" stroke-width="0.5" />\n'
            )

    parts.append("</svg>\n")
    return "".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"[make_projects_card] Written {OUTPUT} ({'static' if STATIC else 'animated'})")
