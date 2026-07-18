"""Render data/contributions.json as an animated 53-week x 7-day heatmap SVG."""
import json
import datetime

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL = 11
GAP = 4
LEFT_PAD = 30
TOP_PAD = 20
MONTH_ROW_H = 16

def load():
    with open("data/contributions.json") as f:
        return json.load(f)

def to_weeks(days):
    # days already span exactly 53*7 = 371 entries starting on a Sunday
    weeks = []
    for i in range(0, len(days), 7):
        weeks.append(days[i:i+7])
    return weeks

def month_labels(weeks):
    labels = []
    last_month = None
    for wi, week in enumerate(weeks):
        first_valid = next((d for d in week if d["date"]), None)
        if not first_valid:
            continue
        month = first_valid["date"][:7]
        if month != last_month:
            dt = datetime.date.fromisoformat(first_valid["date"])
            labels.append((wi, dt.strftime("%b")))
            last_month = month
    return labels

def build(data, out_path="contrib-heatmap.svg"):
    days = data["days"]
    stats = data["stats"]
    weeks = to_weeks(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * (CELL + GAP)
    height = TOP_PAD + MONTH_ROW_H + 7 * (CELL + GAP) + 46  # + legend/footer

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, Monaco, \'Courier New\', monospace">'
    )
    parts.append("<style>")
    parts.append(".box{opacity:0;}")
    parts.append(
        "@keyframes slideIn{from{opacity:0;transform:translateY(-6px);}"
        "to{opacity:1;transform:translateY(0);}}"
    )
    parts.append(".box{animation:slideIn .28s ease-out forwards;}")
    parts.append(".mlabel{fill:#8b949e;font-size:10px;}")
    parts.append(".footer{fill:#c9d1d9;font-size:12px;}")
    parts.append(".legend{fill:#8b949e;font-size:10px;}")
    parts.append("</style>")
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="transparent"/>')

    # month labels
    for wi, label in month_labels(weeks):
        x = LEFT_PAD + wi * (CELL + GAP)
        parts.append(f'<text x="{x}" y="{TOP_PAD}" class="mlabel">{label}</text>')

    grid_top = TOP_PAD + MONTH_ROW_H

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week):
            if not day.get("date"):
                continue
            level = min(max(day.get("level", 0), 0), len(PALETTE) - 1)
            color = PALETTE[level]
            x = LEFT_PAD + wi * (CELL + GAP)
            y = grid_top + di * (CELL + GAP)
            delay = (wi + di) * 0.012  # diagonal stagger
            title = f"{day['count']} contributions on {day['date']}" if day['count'] else f"No contributions on {day['date']}"
            parts.append(
                f'<rect class="box" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    footer_y = grid_top + 7 * (CELL + GAP) + 18

    # Less -> More legend, right-aligned
    legend_box = CELL - 2
    legend_x = width - LEFT_PAD - (len(PALETTE) * (legend_box + 3)) - 34
    parts.append(f'<text x="{legend_x}" y="{footer_y+8}" class="legend">Less</text>')
    lx = legend_x + 34
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + i*(legend_box+3)}" y="{footer_y}" width="{legend_box}" '
            f'height="{legend_box}" rx="2" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{lx + len(PALETTE)*(legend_box+3) + 6}" y="{footer_y+8}" class="legend">More</text>'
    )

    # stats footer line
    total = stats["total"]
    streak = stats["current_streak"]
    longest = stats["longest_streak"]
    stats_text = f"{total} contributions in the last year  ·  current streak {streak}d  ·  longest streak {longest}d"
    parts.append(f'<text x="{LEFT_PAD}" y="{footer_y+8}" class="footer">{stats_text}</text>')

    parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {out_path} ({width}x{height}px), {total} contributions")

if __name__ == "__main__":
    data = load()
    build(data)
