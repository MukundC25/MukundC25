"""
fetch_contributions.py — Scrape the public GitHub contribution calendar.

No token needed. GitHub serves the calendar HTML at:
    https://github.com/users/<username>/contributions

Parses day cells with BeautifulSoup and writes data/contributions.json
with raw days plus derived stats (streak, best day, yearly total).

Usage:
    python scripts/fetch_contributions.py [username]
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "MukundC25"
OUTPUT = "data/contributions.json"


def fetch_calendar(username: str) -> str:
    """Fetch the contribution calendar HTML fragment."""
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str) -> list[dict]:
    """Parse contribution cells into a list of {date, count, level}."""
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub uses <td> with data-date and data-level attributes
    # Count may come from data-count, tooltip text, or be estimated from level
    LEVEL_TO_ESTIMATE = {0: 0, 1: 2, 2: 5, 3: 8, 4: 12, 5: 15}

    for td in soup.find_all("td", class_="ContributionCalendar-day"):
        date = td.get("data-date")
        level = int(td.get("data-level", "0"))

        # Try to get actual count from data-count attribute
        count_text = td.get("data-count")
        if count_text is not None:
            try:
                count = int(count_text)
            except (ValueError, TypeError):
                count = LEVEL_TO_ESTIMATE.get(level, 0)
        else:
            # Try the inner tooltip/span for exact count
            tip = td.find("tool-tip") or td.find("span", class_="sr-only")
            if tip:
                text = tip.get_text(strip=True)
                if text.startswith("No"):
                    count = 0
                else:
                    try:
                        count = int(text.split(" ")[0].replace(",", ""))
                    except (ValueError, IndexError):
                        count = LEVEL_TO_ESTIMATE.get(level, 0)
            else:
                # Estimate from level (good enough for display)
                count = LEVEL_TO_ESTIMATE.get(level, 0)

        if date:
            days.append({"date": date, "count": count, "level": level})

    # Sort by date
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    """Derive streak, best day, and total from the days list."""
    total = sum(d["count"] for d in days)

    # Best day
    best = max(days, key=lambda d: d["count"]) if days else {"date": "", "count": 0}

    # Current streak (from most recent day backwards)
    current_streak = 0
    longest_streak = 0
    streak = 0

    for d in reversed(days):
        if d["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            if streak > 0 and current_streak == 0:
                current_streak = streak
            streak = 0

    # If we never hit a zero, the whole thing is a streak
    if current_streak == 0 and streak > 0:
        current_streak = streak
    longest_streak = max(longest_streak, streak)

    # Monthly totals
    monthly = {}
    for d in days:
        month = d["date"][:7]  # YYYY-MM
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "best_day": {"date": best["date"], "count": best["count"]},
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly": monthly,
    }


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else USERNAME
    print(f"[fetch_contributions] Fetching calendar for {username}...")

    html = fetch_calendar(username)
    days = parse_contributions(html)
    stats = compute_stats(days)

    output = {
        "username": username,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }

    out_path = Path(OUTPUT)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"[fetch_contributions] Written {OUTPUT} ({len(days)} days, {stats['total']} total contributions)")


if __name__ == "__main__":
    main()
