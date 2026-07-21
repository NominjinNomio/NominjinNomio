"""
Optional: computes current/longest contribution streaks from the JSON
data produced by fetch_contributions.py and renders a small streak-stats.svg.
Not wired into the default workflow -- run manually if you want it.

Usage: python generate_streak_svg.py <data_json> <output_svg>
"""
import sys
import json
from datetime import date


def compute_streaks(cells):
    days = sorted(cells, key=lambda c: c["date"])
    active = {d["date"] for d in days if d["level"] > 0}

    longest = current = 0
    prev_date = None
    today = date.today().isoformat()
    running_from_today = True

    for d in days:
        if d["date"] in active:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    # current streak counting back from most recent active day
    streak = 0
    for d in reversed(days):
        if d["date"] > today:
            continue
        if d["date"] in active:
            streak += 1
        else:
            break

    return streak, longest


def build_svg(current_streak, longest_streak, total):
    W, H = 300, 100
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<text x="20" y="35" fill="#ffa657" font-size="13" font-weight="700">Current streak</text>
<text x="220" y="35" fill="#c9d1d9" font-size="13" text-anchor="end">{current_streak} days</text>
<text x="20" y="60" fill="#ffa657" font-size="13" font-weight="700">Longest streak</text>
<text x="220" y="60" fill="#c9d1d9" font-size="13" text-anchor="end">{longest_streak} days</text>
<text x="20" y="85" fill="#ffa657" font-size="13" font-weight="700">Total</text>
<text x="220" y="85" fill="#c9d1d9" font-size="13" text-anchor="end">{total}</text>
</svg>'''


def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_streak_svg.py <data_json> <output_svg>")
        sys.exit(1)

    data_path, output_svg = sys.argv[1], sys.argv[2]
    with open(data_path) as f:
        data = json.load(f)

    current, longest = compute_streaks(data["cells"])
    svg = build_svg(current, longest, data["total"])

    with open(output_svg, "w") as f:
        f.write(svg)
    print(f"Wrote {output_svg} (current={current}, longest={longest})")


if __name__ == "__main__":
    main()
