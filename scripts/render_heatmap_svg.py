"""
Renders contrib-heatmap.svg from the JSON data produced by fetch_contributions.py.

Usage: python render_heatmap_svg.py <data_json> <output_svg>
"""
import sys
import json

LEVEL_COLORS = ["#0e4429", "#006d32", "#26a641", "#39d353", "#39d353"]
CELL_SIZE = 13
GAP = 3
STEP = CELL_SIZE + GAP
LEFT_OFFSET = 34
TOP_OFFSET = 24
W, H = 888, 158

STYLE = """<style>
  text.lbl { fill:#7d8590; font-size:13px; font-weight:600; }
  text.total { fill:#e6edf3; font-size:15px; font-weight:700; }
  .c { transform-box:fill-box; transform-origin:center; opacity:0; animation:pop 0.55s ease-out both; }
  .g { animation:pop 0.55s ease-out both, flash 0.7s ease-out both; }
  @keyframes pop { 0%{opacity:0;transform:scale(.2)} 60%{opacity:1;transform:scale(1.1)} 100%{opacity:1;transform:scale(1)} }
  @keyframes flash { 0%{filter:brightness(2.4)} 45%{filter:brightness(2.4)} 100%{filter:brightness(1)} }
  @media (prefers-reduced-motion: reduce) { .c { opacity:1 !important; animation:none !important; } }
</style>"""


def build_svg(data):
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">'
    )
    parts.append(STYLE)
    parts.append(f'<rect width="{W}" height="{H}" fill="none"/>')

    col = 0
    for m in data["months"]:
        x = LEFT_OFFSET + col * STEP
        parts.append(f'<text class="lbl" x="{x}" y="16">{m["name"]}</text>')
        col += m["span"]

    parts.append(f'<text class="lbl" x="2" y="{TOP_OFFSET + 2 * STEP - 2}">Mon</text>')
    parts.append(f'<text class="lbl" x="2" y="{TOP_OFFSET + 4 * STEP - 2}">Wed</text>')
    parts.append(f'<text class="lbl" x="2" y="{TOP_OFFSET + 6 * STEP - 2}">Fri</text>')

    cells_sorted = sorted(data["cells"], key=lambda c: (c["col"], c["row"]))
    delay = 0.0
    for c in cells_sorted:
        x = LEFT_OFFSET + c["col"] * STEP
        y = TOP_OFFSET + c["row"] * STEP
        color = LEVEL_COLORS[c["level"]]
        parts.append(
            f'<rect class="c g" x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="2.5" fill="{color}" style="animation-delay:{delay:.3f}s"/>'
        )
        delay += 0.0057

    parts.append(f'<text class="total" x="{LEFT_OFFSET}" y="{H - 6}">{data["total"]} contributions in the last year</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 3:
        print("Usage: python render_heatmap_svg.py <data_json> <output_svg>")
        sys.exit(1)

    data_path, output_svg = sys.argv[1], sys.argv[2]
    with open(data_path) as f:
        data = json.load(f)

    svg = build_svg(data)
    with open(output_svg, "w") as f:
        f.write(svg)
    print(f"Wrote {output_svg}")


if __name__ == "__main__":
    main()
