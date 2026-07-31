"""
make_placeholder_ascii.py — Generate a placeholder ASCII portrait SVG
using text-based art until a real photo is processed.

This creates a stylized "MC" monogram with terminal aesthetic.
Replace with a real photo by running:
    python scripts/prep_photo.py your-photo.jpg
    python scripts/make_ascii_svg.py
"""

from pathlib import Path

OUTPUT = "mukund-ascii.svg"

# ASCII art placeholder — stylized initials with border
ASCII_ART = [
    "                                                                                                    ",
    "   ╔══════════════════════════════════════════════════════════════════════════════════════════════╗   ",
    "   ║                                                                                            ║   ",
    "   ║                                                                                            ║   ",
    "   ║                                                                                            ║   ",
    "   ║          ##     ##  ##     ##  ##   ##  ##     ##  ##    ##  ######                         ║   ",
    "   ║          ###   ###  ##     ##  ##  ##   ##     ##  ###   ##  ##   ##                        ║   ",
    "   ║          #### ####  ##     ##  ## ##    ##     ##  ####  ##  ##    ##                       ║   ",
    "   ║          ## ### ##  ##     ##  ####     ##     ##  ## ## ##  ##    ##                       ║   ",
    "   ║          ##  #  ##  ##     ##  ## ##    ##     ##  ##  ####  ##    ##                       ║   ",
    "   ║          ##     ##  ##     ##  ##  ##   ##     ##  ##   ###  ##   ##                        ║   ",
    "   ║          ##     ##   #######   ##   ##   #######   ##    ##  ######                         ║   ",
    "   ║                                                                                            ║   ",
    "   ║                                                                                            ║   ",
    "   ║           ██████╗  ##     ##    ###    ##     ##    ###    ##    ##                         ║   ",
    "   ║          ##    ╚═  ##     ##   ## ##   ##     ##   ## ##   ###   ##                        ║   ",
    "   ║          ##        ##     ##  ##   ##  ##     ##  ##   ##  ####  ##                        ║   ",
    "   ║          ##        #########  ##   ##  ##     ##  ##   ##  ## ## ##                        ║   ",
    "   ║          ##        ##     ##  #######   ##   ##   #######  ##  ####                        ║   ",
    "   ║          ##    ██  ##     ##  ##   ##    ## ##    ##   ##  ##   ###                        ║   ",
    "   ║           ██████╝  ##     ##  ##   ##     ###     ##   ##  ##    ##                        ║   ",
    "   ║                                                                                            ║   ",
    "   ║                                                                                            ║   ",
    "   ║          ─────────────────────────────────────────────────                                 ║   ",
    "   ║          B.Tech ECE · MIT-AOE | Major AI · IIT Ropar                                      ║   ",
    "   ║          GSoC'26 @ FOSSASIA · Full Stack + AI/ML                                          ║   ",
    "   ║          ─────────────────────────────────────────────────                                 ║   ",
    "   ║                                                                                            ║   ",
    "   ║          > Add your photo to generate a real ASCII portrait:                               ║   ",
    "   ║          > python scripts/prep_photo.py your-photo.jpg                                    ║   ",
    "   ║          > python scripts/make_ascii_svg.py                                               ║   ",
    "   ║                                                                                            ║   ",
    "   ║                                                                                            ║   ",
    "   ╚══════════════════════════════════════════════════════════════════════════════════════════════╝   ",
    "                                                                                                    ",
]

# SVG params
FONT_SIZE = 10
CHAR_W = 6.0
CHAR_H = 10.0
FG_COLOR = "#c9d1d9"
BG_COLOR = "#0d1117"
ROWS = len(ASCII_ART)
COLS = len(ASCII_ART[0])
ROW_DURATION = 0.06


def build_svg() -> str:
    width = COLS * CHAR_W + 20
    height = ROWS * CHAR_H + 20

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n'
    )
    parts.append(f'  <rect width="{width}" height="{height}" fill="{BG_COLOR}" />\n')
    parts.append(
        f"  <style>\n"
        f"    text {{\n"
        f"      font-family: 'Courier New', monospace;\n"
        f"      font-size: {FONT_SIZE}px;\n"
        f"      fill: {FG_COLOR};\n"
        f"      white-space: pre;\n"
        f"    }}\n"
        f"  </style>\n"
    )

    for i, line in enumerate(ASCII_ART):
        y = 14 + i * CHAR_H
        delay = i * ROW_DURATION
        clip_id = f"clip-r{i}"

        parts.append(f'  <clipPath id="{clip_id}">\n')
        parts.append(
            f'    <rect x="10" y="{y - CHAR_H + 2}" width="0" height="{CHAR_H + 2}">\n'
        )
        parts.append(
            f'      <animate attributeName="width" '
            f'from="0" to="{COLS * CHAR_W}" '
            f'begin="{delay:.2f}s" dur="{ROW_DURATION * 8:.2f}s" '
            f'fill="freeze" />\n'
        )
        parts.append(f"    </rect>\n")
        parts.append(f"  </clipPath>\n")

        escaped = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
        parts.append(f'  <text x="10" y="{y}" clip-path="url(#{clip_id})">{escaped}</text>\n')

    # Cursor
    cursor_h = CHAR_H
    cursor_w = 3 * CHAR_W
    y_values = [str(4 + i * CHAR_H) for i in range(ROWS)] + [str(4 + (ROWS - 1) * CHAR_H)]
    parts.append(
        f'  <rect x="10" y="4" width="{cursor_w}" height="{cursor_h}" '
        f'fill="{FG_COLOR}" opacity="0.7">\n'
    )
    parts.append(
        f'    <animate attributeName="y" '
        f'values="{";".join(y_values)}" '
        f'keyTimes="{";".join([f"{i / ROWS:.4f}" for i in range(ROWS + 1)])}" '
        f'dur="{ROWS * ROW_DURATION:.2f}s" fill="freeze" />\n'
    )
    parts.append(
        f'    <animate attributeName="opacity" '
        f'from="0.7" to="0" '
        f'begin="{ROWS * ROW_DURATION:.2f}s" dur="0.3s" fill="freeze" />\n'
    )
    parts.append(f"  </rect>\n")
    parts.append("</svg>\n")
    return "".join(parts)


if __name__ == "__main__":
    svg = build_svg()
    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(f"[make_placeholder_ascii] Written {OUTPUT} ({COLS}x{ROWS} chars)")
