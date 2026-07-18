"""Hand-authored neofetch-style info card SVG.
Lines fade + slide in on a stagger. STATIC=1 emits a frozen frame.
"""
import os

WIDTH = 490
LINE_H = 30
FONT = "Consolas, Menlo, Monaco, 'Courier New', monospace"

# ---- content -----------------------------------------------------------
TITLE = "pulkit@github"
FIELDS = [
    ("OS",        "Final-year B.Tech CSE @ BPIT Delhi"),
    ("Role",      "Java / Spring Boot Backend Developer"),
    ("Stack",     "Java, Spring Boot, React, MySQL, Redis, RabbitMQ, Docker"),
    ("Now",       "CodeWar - real-time competitive programming platform"),
    ("Prev",      "MIS + Field Sales CRM (freelance/intern builds)"),
    ("Side",      "GrindLog - daily-target study & progress tracker"),
    ("Goal",      "SDE / backend internship -> PPO, 2027"),
]
ACCENT = "#39d353"
LABEL_COLOR = "#39d353"
VALUE_COLOR = "#c9d1d9"
DIM = "#8b949e"
BG = "#0d1117"
BORDER = "#30363d"

STATIC = os.environ.get("STATIC") == "1"

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build():
    header_h = 42
    height = header_h + len(FIELDS) * LINE_H + 26

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}">'
    )
    parts.append("<style>")
    parts.append(f'.label{{fill:{LABEL_COLOR};font-weight:bold;font-size:13px;}}')
    parts.append(f'.value{{fill:{VALUE_COLOR};font-size:13px;}}')
    parts.append(f'.dim{{fill:{DIM};font-size:12px;}}')
    parts.append('.line{opacity:0;}')
    if not STATIC:
        parts.append(
            '@keyframes fadeSlide{from{opacity:0;transform:translateX(-6px);}'
            'to{opacity:1;transform:translateX(0);}}'
        )
        parts.append('.line{animation:fadeSlide .35s ease-out forwards;}')
    else:
        parts.append('.line{opacity:1;}')
    parts.append("</style>")

    # panel background
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH-1}" height="{height-1}" rx="8" '
        f'fill="{BG}" stroke="{BORDER}"/>'
    )
    # title bar dots (macOS-terminal flavor)
    parts.append('<circle cx="20" cy="18" r="5" fill="#ff5f56"/>')
    parts.append('<circle cx="38" cy="18" r="5" fill="#ffbd2e"/>')
    parts.append('<circle cx="56" cy="18" r="5" fill="#27c93f"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="23" text-anchor="middle" class="dim">{esc(TITLE)}</text>'
    )
    parts.append(f'<line x1="0" y1="34" x2="{WIDTH}" y2="34" stroke="{BORDER}"/>')

    y = 34 + 26
    label_x = 24
    value_x = 100
    delay = 0.15
    for label, value in FIELDS:
        style = "" if STATIC else f'style="animation-delay:{delay:.2f}s"'
        parts.append(f'<g class="line" {style}>')
        parts.append(f'<text x="{label_x}" y="{y}" class="label">{esc(label)}</text>')
        parts.append(f'<text x="{value_x}" y="{y}" class="value">{esc(value)}</text>')
        parts.append('</g>')
        y += LINE_H
        delay += 0.09

    # bottom accent rule
    parts.append(
        f'<rect x="24" y="{height-14}" width="{WIDTH-48}" height="3" rx="1.5" fill="{ACCENT}" opacity="0.7"/>'
    )
    parts.append("</svg>")
    return "\n".join(parts)

if __name__ == "__main__":
    svg = build()
    out = "info-card-static.svg" if STATIC else "info-card.svg"
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out}")
