"""
Generates the animated whoami info card SVG (Now/Edu/Stack/Highlights)
from a JSON config.

Usage: python make_info_card.py <profile_json> <output_svg>
"""
import sys
import json
import html

BORDER = "#30363d"
TITLE_GRAY = "#7d8590"
LABEL_ORANGE = "#ffa657"
VALUE_WHITE = "#c9d1d9"
SECTION_BLUE = "#58a6ff"
GREEN = "#3fb950"
CYAN = "#22d3ee"

ROW_H = 20.5
SECTION_GAP = 30.5
W, H = 480, 376


def esc(s):
    return html.escape(s)


def fade_group(inner_svg, delay):
    return (
        f'<g opacity="0" transform="translate(0,5)">{inner_svg}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
        f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>'
    )


def build_svg(profile):
    username = profile["username"]
    host = profile["host"]

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    parts.append(
        '<defs><linearGradient id="ibg2" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>'
    )
    parts.append(f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg2)"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{BORDER}"/>')
    parts.append(f'<line x1="0" y1="30" x2="{W}" y2="30" stroke="{BORDER}"/>')
    parts.append('<circle cx="20" cy="15" r="5" fill="#ff5f56"/>')
    parts.append('<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>')
    parts.append('<circle cx="52" cy="15" r="5" fill="#27c93f"/>')
    parts.append(f'<text x="{W / 2}" y="19" fill="{TITLE_GRAY}" font-size="12" text-anchor="middle">{esc(username)}@{esc(host)}: ~$ whoami</text>')

    t = 0.15
    y = 55.0
    header_svg = (
        f'<text x="20" y="{y}" font-size="14" font-weight="700">'
        f'<tspan fill="{GREEN}">{esc(username)}</tspan><tspan fill="{TITLE_GRAY}">@</tspan>'
        f'<tspan fill="{CYAN}">{esc(host)}</tspan></text>'
        f'<line x1="128" y1="{y - 4}" x2="460" y2="{y - 4}" stroke="{BORDER}" stroke-opacity="0.8"/>'
    )
    parts.append(fade_group(header_svg, t)); t += 0.06

    y += 25.5
    for f in profile["fields"]:
        field_svg = (
            f'<text x="20" y="{y}" fill="{LABEL_ORANGE}" font-size="12.5" font-weight="700">{esc(f["label"])}</text>'
            f'<text x="112" y="{y}" fill="{VALUE_WHITE}" font-size="12.5">{esc(f["value"])}</text>'
        )
        parts.append(fade_group(field_svg, t)); t += 0.06
        y += ROW_H

    y += SECTION_GAP - ROW_H
    stack_header_svg = (
        f'<text x="20" y="{y}" fill="{SECTION_BLUE}" font-size="12.5" font-weight="700">&#8212; Stack</text>'
        f'<line x1="72" y1="{y - 4}" x2="460" y2="{y - 4}" stroke="{BORDER}" stroke-opacity="0.8"/>'
    )
    parts.append(fade_group(stack_header_svg, t)); t += 0.06

    y += ROW_H
    for f in profile["stack"]:
        field_svg = (
            f'<text x="20" y="{y}" fill="{LABEL_ORANGE}" font-size="12.5" font-weight="700">{esc(f["label"])}</text>'
            f'<text x="112" y="{y}" fill="{VALUE_WHITE}" font-size="12.5">{esc(f["value"])}</text>'
        )
        parts.append(fade_group(field_svg, t)); t += 0.06
        y += ROW_H

    y += SECTION_GAP - ROW_H
    hl_header_svg = (
        f'<text x="20" y="{y}" fill="{SECTION_BLUE}" font-size="12.5" font-weight="700">&#8212; Highlights</text>'
        f'<line x1="112" y1="{y - 4}" x2="460" y2="{y - 4}" stroke="{BORDER}" stroke-opacity="0.8"/>'
    )
    parts.append(fade_group(hl_header_svg, t)); t += 0.06

    y += 16.5
    for hl in profile["highlights"]:
        hl_svg = (
            f'<circle cx="23" cy="{y - 4}" r="2.5" fill="{GREEN}"/>'
            f'<text x="34" y="{y}" fill="{VALUE_WHITE}" font-size="12.5">{esc(hl)}</text>'
        )
        parts.append(fade_group(hl_svg, t)); t += 0.06
        y += ROW_H

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 3:
        print("Usage: python make_info_card.py <profile_json> <output_svg>")
        sys.exit(1)

    profile_path, output_svg = sys.argv[1], sys.argv[2]
    with open(profile_path) as f:
        profile = json.load(f)

    svg = build_svg(profile)
    with open(output_svg, "w") as f:
        f.write(svg)
    print(f"Wrote {output_svg}")


if __name__ == "__main__":
    main()
