"""Fetch the public contribution calendar fragment GitHub serves for a
username (no GraphQL API, no token) and derive stats."""
import json
import sys
import datetime
import requests
from bs4 import BeautifulSoup

USERNAME = "Pulkitarora12"
URL = f"https://github.com/users/{USERNAME}/contributions"

def fetch(username=USERNAME):
    resp = requests.get(f"https://github.com/users/{username}/contributions",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Build a map of tooltip-target-id -> tooltip text (current GitHub markup
    # puts the human-readable count in a <tool-tip for="..."> element rather
    # than a data-count attribute).
    tooltip_text_by_id = {}
    for tip in soup.select("tool-tip"):
        target = tip.get("for")
        if target:
            tooltip_text_by_id[target] = tip.get_text(strip=True)

    days = []
    cells = soup.select("td.ContributionCalendar-day")
    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        level = int(level) if level is not None else 0

        count = 0
        tip_text = tooltip_text_by_id.get(cell.get("id"), "")
        if tip_text and not tip_text.lower().startswith("no contributions"):
            # e.g. "3 contributions on August 4th." / "1 contribution on ..."
            first_tok = tip_text.split(" ", 1)[0]
            if first_tok.isdigit():
                count = int(first_tok)

        days.append({"date": date, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    return days

def derive_stats(days):
    total = sum(d["count"] for d in days)
    # current streak: consecutive days up to the latest with count > 0
    streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            streak += 1
        else:
            break
    longest = 0
    run = 0
    best_day = {"date": None, "count": -1}
    monthly = {}
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
        if d["count"] > best_day["count"]:
            best_day = {"date": d["date"], "count": d["count"]}
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["count"]

    return {
        "total": total,
        "current_streak": streak,
        "longest_streak": longest,
        "best_day": best_day,
        "monthly": monthly,
    }

def main():
    days = fetch()
    stats = derive_stats(days)
    out = {
        "username": USERNAME,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats,
    }
    with open("data/contributions.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote data/contributions.json: {len(days)} days, {stats['total']} total contributions")

if __name__ == "__main__":
    main()
