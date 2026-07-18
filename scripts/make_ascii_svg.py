"""Convert source-prepped.png into a monochrome, self-typing ASCII SVG.
Each row wipes left-to-right, staggered top-to-bottom, then freezes.
"""
import sys
import numpy as np
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense); leading space = blank
COLS = 100
ROWS = 55
CELL_W = 7.2
CELL_H = 13.2
FONT_SIZE = 12
FILL = "#c9d1d9"          # single monochrome fill (no rainbow)
BG = "transparent"
ROW_DURATION = 0.11       # seconds per row wipe
ROW_STAGGER = 0.045       # delay between successive rows starting

def image_to_ascii_grid(path, cols=COLS, rows=ROWS):
    im = Image.open(path).convert("L")
    im = im.resize((cols, rows), Image.LANCZOS)
    arr = np.array(im).astype(np.float32)

    grid = []
    ramp_len = len(RAMP) - 1
    for r in range(rows):
        line = []
        for c in range(cols):
            brightness = arr[r, c] / 255.0     # 0=dark 1=bright
            idx = int(round((1 - brightness) * ramp_len))
            idx = max(0, min(ramp_len, idx))
            ch = RAMP[idx]
            line.append(ch)
        grid.append(line)
    return grid

def esc(ch):
    return {"&": "&amp;", "<": "&lt;", ">": "&gt;"}.get(ch, ch)

def build_svg(grid, out_path):
    rows = len(grid)
    cols = len(grid[0])
    width = cols * CELL_W
    height = rows * CELL_H + 20

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width:.1f} {height:.1f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, Monaco, \'Courier New\', monospace" font-size="{FONT_SIZE}">'
    )
    parts.append("<style>")
    parts.append(f"text{{fill:{FILL};white-space:pre;}}")
    parts.append("rect.cursor{fill:#39d353;}")
    parts.append("</style>")
    parts.append(f'<rect x="0" y="0" width="{width:.1f}" height="{height:.1f}" fill="{BG}"/>')

    for r, row in enumerate(grid):
        # skip fully-blank rows quickly (still animate lightly to keep timing simple)
        line = "".join(row)
        stripped = line.rstrip()
        if stripped == "":
            continue
        y = 14 + r * CELL_H
        row_width = len(stripped) * CELL_W
        start_time = r * ROW_STAGGER

        clip_id = f"clip{r}"
        g_id = f"row{r}"

        # clip rect that wipes from 0 width to full row_width
        parts.append(f'<clipPath id="{clip_id}">')
        parts.append(
            f'  <rect x="0" y="{y - FONT_SIZE:.1f}" width="0" height="{FONT_SIZE + 4}">'
            f'<animate attributeName="width" from="0" to="{row_width:.1f}" '
            f'begin="{start_time:.3f}s" dur="{ROW_DURATION}s" fill="freeze" calcMode="linear"/></rect>'
        )
        parts.append('</clipPath>')

        text_escaped = "".join(esc(ch) for ch in stripped)
        parts.append(
            f'<g clip-path="url(#{clip_id})">'
            f'<text x="0" y="{y:.1f}" xml:space="preserve">{text_escaped}</text>'
            f'</g>'
        )

        # small cursor block riding the wipe edge
        parts.append(
            f'<rect class="cursor" x="0" y="{y - FONT_SIZE + 2:.1f}" width="{CELL_W*0.8:.1f}" height="{FONT_SIZE-1}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{max(row_width-CELL_W,0):.1f}" '
            f'begin="{start_time:.3f}s" dur="{ROW_DURATION}s" fill="freeze" calcMode="linear"/>'
            f'<set attributeName="opacity" to="1" begin="{start_time:.3f}s" dur="{ROW_DURATION}s"/>'
            f'<set attributeName="opacity" to="0" begin="{start_time + ROW_DURATION:.3f}s" fill="freeze"/>'
            f'</rect>'
        )

    parts.append("</svg>")
    with open(out_path, "w") as f:
        f.write("\n".join(parts))
    print(f"wrote {out_path} ({cols}x{rows} grid, {width:.0f}x{height:.0f}px)")

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"
    grid = image_to_ascii_grid(src)
    build_svg(grid, out)
