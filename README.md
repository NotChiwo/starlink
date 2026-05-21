# Starlink Daily Data Usage Scraper

A Python web scraping script that extracts daily data usage from saved Starlink account HTML pages and exports the results to a `.csv` file.

## Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd starlink-webscraper
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

1. Place the following Starlink HTML files in the **same folder** as `scraper.py`:
   - `Nov-Dec.html`
   - `Dec-Jan.html`
   - `Jan-Feb.html`
   - `Feb-Mar.html`
   - `Mar-Apr.html`

2. Run the script:
   ```bash
   python scraper.py
   ```

3. The script will:
   - Display a formatted table of all extracted daily data usage in the terminal
   - Save the results to `starlink_daily_data_usage.csv` in the same folder

## Sample Terminal Output

```
================================================
  Starlink Daily Data Usage Scraper
================================================

Scanning for HTML files...

  ✓ Nov-Dec.html: 30 days parsed (starting 2025-11-17)
  ✓ Dec-Jan.html: 31 days parsed (starting 2025-12-17)
  ✓ Jan-Feb.html: 31 days parsed (starting 2026-01-17)
  ✓ Feb-Mar.html: 28 days parsed (starting 2026-02-17)
  ✓ Mar-Apr.html: 31 days parsed (starting 2026-03-17)

================================================
  Extracted Daily Data Usage
================================================

+--------------+-----------------+
| Date         | Data Usage (GB) |
+--------------+-----------------+
| 2025-11-17   |         17.54 GB |
| 2025-11-18   |         13.24 GB |
| ...          |           ...    |
+--------------+-----------------+
| TOTAL        |       1788.07 GB |
+--------------+-----------------+

Total rows: 151

✓ CSV saved to 'starlink_daily_data_usage.csv'
```

## Output File

The script generates `starlink_daily_data_usage.csv` with the following columns:

| Column | Example | Description |
|--------|---------|-------------|
| `Date` | `2025-11-17` | Calendar date (UTC) |
| `Data_Usage_GB` | `17.54` | Residential data used that day (GB) |

## How It Works

The Starlink account page renders usage data as an SVG bar chart. The scraper:
1. Parses the HTML file using **BeautifulSoup**
2. Locates the SVG bar chart inside the page
3. Reads the y-axis tick labels (e.g. `0 GB`, `20 GB`) and their pixel positions to compute a **GB-per-pixel scale**
4. Measures each bar's height in pixels and converts it to GB
5. Assigns sequential calendar dates starting from the known billing cycle start date
6. Prints the results as a table and saves them to CSV

## Notes

- Data usage values are approximated from pixel heights in the SVG chart. Results are accurate to within ~1 GB per billing period when compared to Starlink's reported totals.
- The Starlink dashboard tracks usage in UTC, which may differ from your local time zone.
