"""
render_heatmap_svg.py — Render contribution data as an animated heatmap SVG.

Reads data/contributions.json and produces contrib-heatmap.svg with:
- 53-week × 7-day grid of rounded colored boxes
- Diagonal slide-in reveal animation (CSS keyframes, plays once)
- GitHub-ish green palette
- Legend (Less → More) and stats footer

Usage:
    python scripts/render_heatmap_svg.py
"""

import json
from datetime import datetime
from pathlib import Path

INPUT = "data/contributions.json"
OUTPUT = "contrib-heatmap.svg"

# GitHub-ish green palette (level 0-5)
PALETTE = [
    "#161b22",  # none
    "#0e4429",  # level 1
    "#006d32",  # level 2
    "#26a641",  # level 3
    "#39d353",  # level 4
    "#69f0a0",  # level 5 (neon top)
]

# Layout
BOX_SIZE = 12
BOX_GAP = 3
BOX_RADIUS = 2
WEEKS = 53
DAYS = 7
PADDING_X = 36
PADDING_Y = 30
FOOTER_HEIGHT = 50
LEGEND_Y_OFFSET = 20

# Animation
REVEAL_DURATION = 2.5  # total animation time in seconds

# Colors
BG_COLOR = "#0d1117"
TEXT_COLOR = "#8b949e"
LABEL_COLOR = "#c9d1d9"

DAY_LABELS = ["Mon", "", "Wed", "", "Fri", "", ""]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data() -> dict:
    """Load contributions JSON."""
    return json.loads(Path(INPUT).read_text(encoding="utf-8"))


def build_grid(days: list[dict]) -> list[list[int]]:
    """Organize days into a 53×7 grid of levels (week-major)."""
    # Fill a 53×7 grid; days should be ~365-371 entries
    grid = [[0] * DAYS for _ in range(WEEKS)]

    if not days:
        return grid

    # Find the first Sunday to align the grid
    from datetime import date as dt_date

    first = dt_date.fromisoformat(days[0]["date"])
    # Align to start of week (Sunday = 0 for GitHub)
    start_weekday = first.weekday()  # Monday=0 ... Sunday=6
    # GitHub weeks start on Sunday, Python weekday: Sun=6
    # Convert to GitHub-style: Sun=0, Mon=1, ..., Sat=6
    gh_weekday = (start_weekday + 1) % 7

    for i, day in enumerate(days):
        d = dt_date.fromisoformat(day["date"])
        weekday = (d.weekday() + 1) % 7  # GitHub-style: Sun=0
        # Calculate week index from start
        delta_days = (d - first).days
        week_idx = (delta_days + gh_weekday) // 7

        if 0 <= week_idx < WEEKS and 0 <= weekday < DAYS:
            level = min(day.get("level", 0), len(PALETTE) - 1)
            grid[week_idx][weekday] = level

    return grid


def get_month_positions(days: list[dict]) -> list[tuple[int, str]]:
    """Get (week_index, month_label) for month boundaries."""
    if not days:
        return []

    from datetime import date as dt_date

    first = dt_date.fromisoformat(days[0]["date"])
    gh_weekday = (first.weekday() + 1) % 7
    positions = []
    seen_months = set()

    for day in days:
        d = dt_date.fromisoformat(day["date"])
        month_key = (d.year, d.month)
        if month_key not in seen_months and d.day <= 7:
            seen_months.add(month_key)
            delta_days = (d - first).days
            week_idx = (delta_days + gh_weekday) // 7
            if 0 <= week_idx < WEEKS:
                positions.append((week_idx, MONTH_LABELS[d.month - 1]))

    return positions


def build_svg(grid: list[list[int]], stats: dict, days: list[dict]) -> str:
    """Build the complete heatmap SVG."""
    grid_width = WEEKS * (BOX_SIZE + BOX_GAP)
    grid_height = DAYS * (BOX_SIZE + BOX_GAP)
    total_width = grid_width + PADDING_X * 2
    total_height = grid_height + PADDING_Y * 2 + FOOTER_HEIGHT

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {total_width} {total_height}" '
        f'width="{total_width}" height="{total_height}">\n'
    )

    # Background
    parts.append(
        f'  <rect width="{total_width}" height="{total_height}" '
        f'fill="{BG_COLOR}" rx="6" />\n'
    )

    # Animation styles — diagonal reveal
    parts.append("  <style>\n")
    parts.append(
        "    @keyframes boxReveal {\n"
        "      from { opacity: 0; transform: scale(0.5) translateY(4px); }\n"
        "      to { opacity: 1; transform: scale(1) translateY(0); }\n"
        "    }\n"
    )
    parts.append(
        "    .day-box {\n"
        "      opacity: 0;\n"
        "      animation: boxReveal 0.15s ease forwards;\n"
        "    }\n"
    )
    parts.append(
        "    .label { font-family: 'Courier New', monospace; "
        f"font-size: 10px; fill: {TEXT_COLOR}; }}\n"
    )
    parts.append(
        "    .stats-text { font-family: 'Courier New', monospace; "
        f"font-size: 11px; fill: {LABEL_COLOR}; }}\n"
    )
    parts.append("  </style>\n")

    # Month labels
    month_positions = get_month_positions(days)
    for week_idx, label in month_positions:
        x = PADDING_X + week_idx * (BOX_SIZE + BOX_GAP)
        y = PADDING_Y - 8
        parts.append(
            f'  <text x="{x}" y="{y}" class="label">{label}</text>\n'
        )

    # Day labels (Mon, Wed, Fri)
    for day_idx, label in enumerate(DAY_LABELS):
        if label:
            x = PADDING_X - 30
            y = PADDING_Y + day_idx * (BOX_SIZE + BOX_GAP) + BOX_SIZE - 1
            parts.append(
                f'  <text x="{x}" y="{y}" class="label">{label}</text>\n'
            )

    # Grid boxes with staggered animation
    for week in range(WEEKS):
        for day in range(DAYS):
            level = grid[week][day]
            color = PALETTE[level]
            x = PADDING_X + week * (BOX_SIZE + BOX_GAP)
            y = PADDING_Y + day * (BOX_SIZE + BOX_GAP)

            # Diagonal delay: based on (week + day)
            diag = week + day
            max_diag = WEEKS + DAYS - 2
            delay = (diag / max_diag) * REVEAL_DURATION

            parts.append(
                f'  <rect class="day-box" x="{x}" y="{y}" '
                f'width="{BOX_SIZE}" height="{BOX_SIZE}" '
                f'rx="{BOX_RADIUS}" ry="{BOX_RADIUS}" '
                f'fill="{color}" '
                f'style="animation-delay: {delay:.3f}s;" />\n'
            )

    # Footer: Legend
    legend_y = PADDING_Y + grid_height + LEGEND_Y_OFFSET
    legend_x = PADDING_X

    parts.append(
        f'  <text x="{legend_x}" y="{legend_y + 9}" class="label">Less</text>\n'
    )
    lx = legend_x + 32
    for i, color in enumerate(PALETTE):
        parts.append(
            f'  <rect x="{lx}" y="{legend_y}" '
            f'width="{BOX_SIZE}" height="{BOX_SIZE}" '
            f'rx="{BOX_RADIUS}" fill="{color}" />\n'
        )
        lx += BOX_SIZE + 3
    parts.append(
        f'  <text x="{lx + 4}" y="{legend_y + 9}" class="label">More</text>\n'
    )

    # Stats text
    total = stats.get("total", 0)
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)

    stats_text = (
        f"{total:,} contributions in the last year"
        f"  ·  Current streak: {streak} days"
        f"  ·  Longest: {longest} days"
    )
    stats_x = PADDING_X
    stats_y = legend_y + 30
    parts.append(
        f'  <text x="{stats_x}" y="{stats_y}" class="stats-text">'
        f"{stats_text}</text>\n"
    )

    parts.append("</svg>\n")
    return "".join(parts)


def main():
    data = load_data()
    days = data.get("days", [])
    stats = data.get("stats", {})

    grid = build_grid(days)
    svg = build_svg(grid, stats, days)

    Path(OUTPUT).write_text(svg, encoding="utf-8")
    print(
        f"[render_heatmap_svg] Written {OUTPUT} "
        f"({stats.get('total', 0)} contributions, {len(days)} days)"
    )


if __name__ == "__main__":
    main()
