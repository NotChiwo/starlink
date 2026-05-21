"""
Starlink Daily Data Usage Scraper
Extracts per-day data usage from saved Starlink account HTML pages.
"""

import csv
import re
import glob
import sys
from datetime import datetime, timedelta
from pathlib import Path

import bs4


# Map of filename keywords to their billing cycle start dates
FILE_DATE_MAP = {
    "Nov-Dec": "2025-11-17",
    "Dec-Jan": "2025-12-17",
    "Jan-Feb": "2026-01-17",
    "Feb-Mar": "2026-02-17",
    "Mar-Apr": "2026-03-17",
}


def parse_scale(svg):
    """Return GB-per-pixel scale from the y-axis tick labels."""
    y_ticks = []
    for tick in svg.find_all(
        "g", class_=lambda c: c and "MuiChartsAxis-tickContainer" in c
    ):
        text_el = tick.find("text")
        if text_el and "GB" in text_el.get_text():
            tspan = text_el.find("tspan")
            val_str = (tspan.get_text() if tspan else text_el.get_text()).strip()
            m = re.search(r"([\d.]+)", val_str)
            if not m:
                continue
            gb_val = float(m.group(1))
            transform = tick.get("transform", "")
            tm = re.search(r"translate\(0,\s*([\d.]+)\)", transform)
            if tm:
                y_ticks.append((float(tm.group(1)), gb_val))

    if len(y_ticks) < 2:
        raise ValueError("Could not find at least two y-axis ticks in SVG.")

    y_ticks.sort(key=lambda x: x[0], reverse=True)
    y_bottom, gb_bottom = y_ticks[0]
    y_top,    gb_top    = y_ticks[-1]
    return (gb_top - gb_bottom) / (y_bottom - y_top)


def parse_html(html_path: Path, start_date: datetime):
    """
    Parse a single Starlink monthly HTML page and return a list of
    {'Date': 'YYYY-MM-DD', 'Data_Usage_GB': float} dicts.
    """
    soup = bs4.BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    svg  = soup.find("svg", class_="MuiChartsSurface-root")
    if svg is None:
        raise ValueError(f"No chart SVG found in {html_path}")

    gb_per_pixel = parse_scale(svg)

    bars = sorted(
        [(float(r["x"]), float(r["height"])) for r in svg.find_all("rect", fill="#FFFFFF")],
        key=lambda b: b[0]
    )

    rows = []
    for i, (_, height) in enumerate(bars):
        rows.append({
            "Date":          (start_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "Data_Usage_GB": round(height * gb_per_pixel, 2),
        })
    return rows


def print_table(rows):
    """Print all rows as a formatted table in the terminal."""
    col_date  = "Date"
    col_usage = "Data Usage (GB)"
    sep = "+" + "-" * 14 + "+" + "-" * 17 + "+"

    print(sep)
    print(f"| {col_date:<12} | {col_usage:<15} |")
    print(sep)

    current_period = None
    for row in rows:
        # Print a divider between billing periods
        month = row["Date"][5:7]
        year  = row["Date"][:4]
        period_key = f"{year}-{month}"
        if period_key != current_period:
            if current_period is not None:
                print(sep)
            current_period = period_key

        print(f"| {row['Date']:<12} | {row['Data_Usage_GB']:>13.2f} GB |")

    print(sep)
    total = sum(r["Data_Usage_GB"] for r in rows)
    print(f"| {'TOTAL':<12} | {total:>13.2f} GB |")
    print(sep)
    print(f"\nTotal rows: {len(rows)}")


def main():
    all_rows = []

    print("=" * 48)
    print("  Starlink Daily Data Usage Scraper")
    print("=" * 48)
    print("\nScanning for HTML files...\n")

    for keyword, date_str in FILE_DATE_MAP.items():
        matches = glob.glob(f"*{keyword}*.html")
        if not matches:
            print(f"  WARNING: No file found matching '*{keyword}*.html' — skipping.")
            continue
        filepath = Path(matches[0])
        start_date = datetime.strptime(date_str, "%Y-%m-%d")
        rows = parse_html(filepath, start_date)
        all_rows.extend(rows)
        print(f"  ✓ {filepath.name}: {len(rows)} days parsed (starting {date_str})")

    if not all_rows:
        print("\nERROR: No HTML files were found.")
        print("Make sure the Starlink HTML files are in the same folder as this script.")
        sys.exit(1)

    all_rows.sort(key=lambda r: r["Date"])

    # Print table to terminal for comparison
    print(f"\n{'=' * 48}")
    print("  Extracted Daily Data Usage")
    print(f"{'=' * 48}\n")
    print_table(all_rows)

    # Save to CSV
    output_path = Path("starlink_daily_data_usage.csv")
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Date", "Data_Usage_GB"])
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n✓ CSV saved to '{output_path}'")


if __name__ == "__main__":
    main()