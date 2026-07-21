"""
Generates an animated typewriter-reveal ASCII portrait SVG from a
background-removed PNG (RGBA, transparent background).

Usage: python make_ascii_svg.py <prepped_png> <username> <full_name> <output_svg>
"""
import sys
import html
from PIL import Image, ImageOps, ImageEnhance

CHARS = " .`,:;-~+=*#%@"
NEW_W = 140          # ascii grid resolution (columns)
ALPHA_THRESH = 60    # below this alpha, treat pixel as background (blank)

BORDER = "#30363d"
TITLE_GRAY = "#7d8590"
VALUE_WHITE = "#c9d1d9"

ROW_H = 12
FONT_SIZE = 9.5
CONTENT_W = 680
PAD_X = 80
TITLEBAR_H = 36
CONTENT_START_Y = 44


def esc(s):
    return html.escape(s)


def image_to_ascii(png_path):
    img = Image.open(png_path)
    r, g, b, a = img.split()
    gray = Image.merge("RGB", (r, g, b)).convert("L")
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = ImageEnhance.Contrast(gray).enhance(1.3)

    w, h = img.size
    aspect = h / w
    new_h = int(NEW_W * aspect * 0.48)
    gray_small = gray.resize((NEW_W, new_h))
    alpha_small = a.resize((NEW_W, new_h))

    gpix = list(gray_small.getdata())
    apix = list(alpha_small.getdata())

    lines = []
    row = []
    for i, (p, al) in enumerate(zip(gpix, apix)):
        if al < ALPHA_THRESH:
            row.append(" ")
        else:
            idx = int((1 - p / 255) * (len(CHARS) - 1))
            idx = max(0, min(idx, len(CHARS) - 1))
            row.append(CHARS[idx])
        if (i + 1) % NEW_W == 0:
            lines.append("".join(row))
            row = []

    # trim to content bounding box (both axes) so it's centered when stretched
    first_row = next(i for i, l in enumerate(lines) if l.strip())
    last_row = len(lines) - 1 - next(i for i, l in enumerate(reversed(lines)) if l.strip())
    lines = lines[first_row:last_row + 1]

    maxlen = max(len(l) for l in lines)
    min_col, max_col = maxlen, 0
    for l in lines:
        for i, ch in enumerate(l):
            if ch != " ":
                min_col = min(min_col, i)
                max_col = max(max_col, i)
    lines = [l[min_col:max_col + 1].ljust(max_col + 1 - min_col) for l in lines]
    return lines


def build_svg(ascii_lines, username, host, full_name):
    canvas_w = PAD_X * 2 + CONTENT_W
    n = len(ascii_lines)
    footer_line_y = CONTENT_START_Y + n * ROW_H
    footer_text_y = footer_line_y + 19
    canvas_h = footer_line_y + 43

    title = f"{username}@{host}: ~/portrait.sh"
    footer_prefix = f"{username}@{host}:~$ whoami "

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">'
    )
    parts.append(
        '<defs><linearGradient id="bgp" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#111722"/><stop offset="1" stop-color="#0d1117"/></linearGradient></defs>'
    )
    parts.append(f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#bgp)"/>')
    parts.append(
        f'<rect x="0.5" y="0.5" width="{canvas_w - 1}" height="{canvas_h - 1}" '
        f'rx="12" fill="none" stroke="{BORDER}" stroke-width="1"/>'
    )
    parts.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{BORDER}"/>')
    parts.append('<circle cx="22" cy="18.0" r="6" fill="#ff5f56"/>')
    parts.append('<circle cx="40" cy="18.0" r="6" fill="#ffbd2e"/>')
    parts.append('<circle cx="58" cy="18.0" r="6" fill="#27c93f"/>')
    parts.append(f'<text x="{canvas_w / 2}" y="22.5" fill="{TITLE_GRAY}" font-size="11" text-anchor="middle">{esc(title)}</text>')

    dur = 0.11
    for i, line in enumerate(ascii_lines):
        y_top = CONTENT_START_Y + i * ROW_H
        y_text = y_top + 9
        begin = i * dur
        end = (i + 1) * dur
        clip_id = f"r{i}"
        parts.append(
            f'<clipPath id="{clip_id}"><rect x="{PAD_X}" y="{y_top:.1f}" height="{ROW_H}" width="0">'
            f'<animate attributeName="width" from="0" to="{CONTENT_W}" begin="{begin:.3f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>'
        )
        parts.append(
            f'<g clip-path="url(#{clip_id})"><text xml:space="preserve" x="{PAD_X}" y="{y_text:.1f}" '
            f'fill="{VALUE_WHITE}" font-size="{FONT_SIZE}" textLength="{CONTENT_W}" lengthAdjust="spacing">{esc(line)}</text></g>'
        )
        parts.append(
            f'<rect y="{y_top + 1:.1f}" width="8" height="{ROW_H - 2}" fill="{VALUE_WHITE}" opacity="0">'
            f'<animate attributeName="x" from="{PAD_X}" to="{PAD_X + CONTENT_W}" begin="{begin:.3f}s" dur="{dur:.2f}s" fill="freeze"/>'
            f'<set attributeName="opacity" to="0.85" begin="{begin:.3f}s"/>'
            f'<set attributeName="opacity" to="0" begin="{end:.3f}s"/></rect>'
        )

    parts.append(f'<line x1="0" y1="{footer_line_y}.0" x2="{canvas_w}" y2="{footer_line_y}.0" stroke="{BORDER}"/>')
    parts.append(f'<text x="{PAD_X - 60}" y="{footer_text_y}.0" fill="{TITLE_GRAY}" font-size="10.5">{esc(footer_prefix)}<tspan fill="{VALUE_WHITE}" font-weight="700">{esc(full_name)}</tspan></text>')

    parts.append("</svg>")
    return "\n".join(parts)


def main():
    if len(sys.argv) != 5:
        print("Usage: python make_ascii_svg.py <prepped_png> <username> <full_name> <output_svg>")
        sys.exit(1)

    prepped_png, username, full_name, output_svg = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    ascii_lines = image_to_ascii(prepped_png)
    svg = build_svg(ascii_lines, username, "github", full_name)

    with open(output_svg, "w") as f:
        f.write(svg)
    print(f"Wrote {output_svg} ({len(ascii_lines)} rows)")


if __name__ == "__main__":
    main()
