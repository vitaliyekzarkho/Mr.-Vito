import csv
import math
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "rent_pressure.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "rent_pressure.csv"
LATEST_CSV_PATH = POWER_BI_DIR / "rent_pressure_latest.csv"
OUTPUT_LATEST_CSV_PATH = OUTPUT_DIR / "rent_pressure_latest.csv"
SPEC_PATH = POWER_BI_DIR / "task21_rent_pressure_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task21_rent_pressure_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task21_rent_pressure_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task21_rent_pressure_page_mockup.png"


def get_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def fetch_rows():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = [
        dict(row)
        for row in con.execute(
            """
            SELECT
                homelessness_region,
                year,
                half,
                half_year,
                avg_rent_euro,
                population_weighted_avg_rent_euro,
                county_count,
                population_year,
                homeless_adults,
                population,
                homeless_adults_per_10000
            FROM vw_rent_pressure
            ORDER BY year, half, homelessness_region
            """
        )
    ]
    con.close()
    return rows


def latest_period(rows):
    return max((row["year"], row["half"], row["half_year"]) for row in rows)


def latest_rows(rows):
    year, half, _ = latest_period(rows)
    return sorted(
        [row for row in rows if row["year"] == year and row["half"] == half],
        key=lambda row: row["population_weighted_avg_rent_euro"],
        reverse=True,
    )


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "homelessness_region",
        "year",
        "half",
        "half_year",
        "avg_rent_euro",
        "population_weighted_avg_rent_euro",
        "county_count",
        "population_year",
        "homeless_adults",
        "population",
        "homeless_adults_per_10000",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def pearson(rows):
    xs = [row["population_weighted_avg_rent_euro"] for row in rows]
    ys = [row["homeless_adults_per_10000"] for row in rows]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return round(numerator / denominator, 3) if denominator else 0


def linear_fit(rows):
    xs = [row["population_weighted_avg_rent_euro"] for row in rows]
    ys = [row["homeless_adults_per_10000"] for row in rows]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    intercept = mean_y - slope * mean_x
    return slope, intercept


def national_rent_trend(rows):
    by_period = {}
    for row in rows:
        key = (row["year"], row["half"], row["half_year"])
        item = by_period.setdefault(key, {"rent_weighted_population": 0, "population": 0})
        item["rent_weighted_population"] += row["population_weighted_avg_rent_euro"] * row["population"]
        item["population"] += row["population"]
    trend = []
    for (year, half, half_year), value in sorted(by_period.items()):
        trend.append(
            {
                "year": year,
                "half": half,
                "half_year": half_year,
                "national_weighted_avg_rent_euro": round(value["rent_weighted_population"] / value["population"], 2),
            }
        )
    return trend


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_spec(rows):
    latest = latest_rows(rows)
    year, half, half_year = latest_period(rows)
    corr = pearson(latest)
    highest_rate = max(latest, key=lambda row: row["homeless_adults_per_10000"])
    highest_rent = max(latest, key=lambda row: row["population_weighted_avg_rent_euro"])
    lowest_rent = min(latest, key=lambda row: row["population_weighted_avg_rent_euro"])
    trend = national_rent_trend(rows)
    rent_growth = round(
        (trend[-1]["national_weighted_avg_rent_euro"] - trend[0]["national_weighted_avg_rent_euro"])
        / trend[0]["national_weighted_avg_rent_euro"]
        * 100,
        1,
    )
    sample_rows = [
        [
            row["homelessness_region"],
            row["half_year"],
            row["population_weighted_avg_rent_euro"],
            row["homeless_adults_per_10000"],
            row["county_count"],
        ]
        for row in latest
    ]

    spec = f"""# Task 21 - Rent Pressure Page Build Spec

## Page Intent

After this page, the user should understand whether regions with higher rents also show higher homelessness rates in the analysed dataset, while treating this as association rather than causation.

## Data Source

Use SQL view:

```text
vw_rent_pressure
```

Power BI-ready extracts:

```text
Project/Power BI/rent_pressure.csv
Project/Power BI/rent_pressure_latest.csv
```

## Page Grain

Main extract:

```text
homelessness_region + half_year
```

Latest-period extract:

```text
homelessness_region
```

Expected rows:

```text
rent_pressure.csv = 99
rent_pressure_latest.csv = 9
```

## Analytical Scope

The scatter plot should use one selected rent period at a time. The default period is:

```text
{half_year}
```

Homelessness rate is not time-series in this dataset; it is repeated across rent periods for comparison only.

## Required Fields

{md_table(["Field", "Use"], [
    ["`homelessness_region`", "Point / axis / slicer"],
    ["`half_year`", "Period slicer"],
    ["`population_weighted_avg_rent_euro`", "Rent pressure measure"],
    ["`homeless_adults_per_10000`", "Homelessness rate"],
    ["`county_count`", "Coverage check"],
    ["`population`", "Weighting / tooltip"],
])}

## KPI / Insight Cards

{md_table(["Card", "Expected Value"], [
    ["Default rent period", half_year],
    ["Pearson correlation", corr],
    ["Highest rent region", f"{highest_rent['homelessness_region']} (EUR {highest_rent['population_weighted_avg_rent_euro']:,.0f})"],
    ["Highest homelessness rate", f"{highest_rate['homelessness_region']} ({highest_rate['homeless_adults_per_10000']})"],
    ["National weighted rent growth", f"{rent_growth}% from {trend[0]['half_year']} to {trend[-1]['half_year']}"],
])}

## Visual 1 - Rent vs Homelessness Rate

{md_table(["Setting", "Value"], [
    ["Visual type", "Scatter chart"],
    ["X-axis", "`population_weighted_avg_rent_euro`"],
    ["Y-axis", "`homeless_adults_per_10000`"],
    ["Details", "`homelessness_region`"],
    ["Tooltip", "`homeless_adults`, `population`, `county_count`, `half_year`"],
    ["Default filter", f"`half_year = {half_year}`"],
    ["Title", "`Rent vs Homelessness Rate`"],
])}

## Visual 2 - Rent Trend

{md_table(["Setting", "Value"], [
    ["Visual type", "Line chart"],
    ["X-axis", "`half_year`"],
    ["Y-axis", "`population_weighted_avg_rent_euro`"],
    ["Legend", "`homelessness_region` or national weighted trend"],
    ["Title", "`Rent Trend by Region`"],
])}

## Visual 3 - Regional Comparison Table

Columns:

{md_table(["Column", "Display Name"], [
    ["`homelessness_region`", "Region"],
    ["`population_weighted_avg_rent_euro`", "Weighted Avg Rent"],
    ["`homeless_adults_per_10000`", "Rate per 10,000"],
    ["`homeless_adults`", "Homeless Adults"],
    ["`county_count`", "Counties"],
])}

## Interpretation Guidance

Use neutral wording:

```text
In {half_year}, regions with higher weighted average rents show a positive association with homelessness rates in this dataset.
```

Avoid causal wording:

```text
High rent causes homelessness.
```

## Data Note

Use this note:

```text
This page shows association, not causation. Rent is time-series by half-year, while homelessness is a regional snapshot repeated across rent periods.
```

## Latest Period Validation Sample

{md_table(["Region", "Half-Year", "Weighted Avg Rent", "Rate per 10,000", "County Count"], sample_rows)}

## Acceptance Criteria

- `rent_pressure.csv` contains 99 rows.
- `rent_pressure_latest.csv` contains 9 rows.
- Scatter chart is filtered to one half-year by default.
- Page includes a visible caution that the relationship is associative, not causal.
- Dublin is visible as both highest rent and highest homelessness-rate region in the default period.
"""
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 22, y1 + 18), title, fill="#52616B", font=get_font(20))
    draw.text((x1 + 22, y1 + 58), value, fill="#17324D", font=get_font(31, bold=True))
    if subtitle:
        draw.text((x1 + 22, y1 + 96), subtitle, fill="#7A8A99", font=get_font(15))


def draw_scatter(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Rent vs Homelessness Rate", fill="#17324D", font=get_font(25, bold=True))
    draw.text((x1 + 24, y1 + 55), "Latest half-year; observed association only", fill="#627386", font=get_font(16))

    plot = (x1 + 82, y1 + 95, x2 - 42, y2 - 55)
    px1, py1, px2, py2 = plot
    draw.line((px1, py2, px2, py2), fill="#9AA8B5", width=1)
    draw.line((px1, py1, px1, py2), fill="#9AA8B5", width=1)
    min_x = min(row["population_weighted_avg_rent_euro"] for row in rows) * 0.95
    max_x = max(row["population_weighted_avg_rent_euro"] for row in rows) * 1.04
    min_y = 0
    max_y = max(row["homeless_adults_per_10000"] for row in rows) * 1.12
    slope, intercept = linear_fit(rows)

    def map_x(value):
        return px1 + (value - min_x) / (max_x - min_x) * (px2 - px1)

    def map_y(value):
        return py2 - (value - min_y) / (max_y - min_y) * (py2 - py1)

    start_x, end_x = min_x, max_x
    draw.line(
        (map_x(start_x), map_y(slope * start_x + intercept), map_x(end_x), map_y(slope * end_x + intercept)),
        fill="#D95F59",
        width=3,
    )
    for row in rows:
        cx = map_x(row["population_weighted_avg_rent_euro"])
        cy = map_y(row["homeless_adults_per_10000"])
        radius = 8 if row["homelessness_region"] != "Dublin" else 11
        fill = "#2F6AA8" if row["homelessness_region"] != "Dublin" else "#D95F59"
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill, outline="#FFFFFF", width=2)
        label = row["homelessness_region"]
        offsets = {
            "Dublin": (10, -8),
            "Mid-East": (10, 20),
            "South-West": (-20, 14),
            "West": (10, -2),
            "Mid-West": (10, -14),
            "North-East": (10, 8),
            "Midlands": (-18, -18),
            "South-East": (8, -2),
            "North-West": (10, -2),
        }
        dx, dy = offsets.get(label, (10, -8))
        draw.text((cx + dx, cy + dy), label, fill="#17324D", font=get_font(14, bold=label == "Dublin"))
    draw.text((px1, py2 + 22), "Weighted average rent (EUR)", fill="#52616B", font=get_font(15))
    draw.text((px1 - 50, py1 - 22), "Rate per 10,000", fill="#52616B", font=get_font(15))


def draw_trend(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Weighted Rent Trend", fill="#17324D", font=get_font(25, bold=True))
    trend = national_rent_trend(rows)
    plot = (x1 + 70, y1 + 80, x2 - 34, y2 - 50)
    px1, py1, px2, py2 = plot
    min_y = min(row["national_weighted_avg_rent_euro"] for row in trend) * 0.95
    max_y = max(row["national_weighted_avg_rent_euro"] for row in trend) * 1.04

    def map_x(index):
        return px1 + index / (len(trend) - 1) * (px2 - px1)

    def map_y(value):
        return py2 - (value - min_y) / (max_y - min_y) * (py2 - py1)

    draw.line((px1, py2, px2, py2), fill="#9AA8B5", width=1)
    draw.line((px1, py1, px1, py2), fill="#9AA8B5", width=1)
    points = [(map_x(i), map_y(row["national_weighted_avg_rent_euro"])) for i, row in enumerate(trend)]
    draw.line(points, fill="#2A9D8F", width=4)
    for i, point in enumerate(points):
        x, y = point
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill="#2A9D8F")
        if i in {0, len(points) - 1}:
            draw.text((x - 28, y - 26), f"EUR {trend[i]['national_weighted_avg_rent_euro']:,.0f}", fill="#17324D", font=get_font(14, bold=True))
    for i, row in enumerate(trend):
        if i % 2 == 0 or i == len(trend) - 1:
            draw.text((map_x(i) - 20, py2 + 16), row["half_year"], fill="#52616B", font=get_font(12))
    draw.text((px1, y2 - 28), "National weighted average across homelessness regions", fill="#627386", font=get_font(14))


def draw_table(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Latest Period Comparison", fill="#17324D", font=get_font(25, bold=True))
    headers = ["Region", "Rent", "Rate", "Adults"]
    xs = [x1 + 24, x1 + 250, x1 + 390, x1 + 510]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 96
    for row in rows:
        values = [
            row["homelessness_region"],
            f"EUR {row['population_weighted_avg_rent_euro']:,.0f}",
            f"{row['homeless_adults_per_10000']:.2f}",
            f"{row['homeless_adults']:,}",
        ]
        bold = row["homelessness_region"] == "Dublin"
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill="#17324D" if bold else "#2F3A44", font=get_font(15, bold=bold))
        y += 23


def write_mockup(rows):
    width, height = 1600, 1160
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)
    latest = latest_rows(rows)
    _, _, half_year = latest_period(rows)
    corr = pearson(latest)
    highest_rent = max(latest, key=lambda row: row["population_weighted_avg_rent_euro"])
    highest_rate = max(latest, key=lambda row: row["homeless_adults_per_10000"])
    trend = national_rent_trend(rows)
    rent_growth = round(
        (trend[-1]["national_weighted_avg_rent_euro"] - trend[0]["national_weighted_avg_rent_euro"])
        / trend[0]["national_weighted_avg_rent_euro"]
        * 100,
        1,
    )

    draw.text((60, 50), "Rent Pressure", fill="#17324D", font=get_font(42, bold=True))
    draw.text((62, 102), "Observed relationship between rent levels and homelessness rates", fill="#627386", font=get_font(23))

    draw_card(draw, (60, 146, 405, 270), "Default Period", half_year, "Scatter filtered to one period")
    draw_card(draw, (435, 146, 780, 270), "Correlation", f"{corr:.3f}", "Association, not causation")
    draw_card(
        draw,
        (810, 146, 1165, 270),
        "Highest Rent",
        highest_rent["homelessness_region"],
        f"EUR {highest_rent['population_weighted_avg_rent_euro']:,.0f} weighted avg",
    )
    draw_card(
        draw,
        (1195, 146, 1540, 270),
        "Highest Rate",
        highest_rate["homelessness_region"],
        f"{highest_rate['homeless_adults_per_10000']:.2f} per 10,000",
    )

    draw_scatter(draw, (60, 320, 1010, 720), latest)
    draw_trend(draw, (1040, 320, 1540, 720), rows)
    draw_table(draw, (60, 755, 790, 1070), latest)
    draw_card(draw, (830, 755, 1540, 1070), "National Weighted Rent Growth", f"{rent_growth}%", f"{trend[0]['half_year']} to {trend[-1]['half_year']}")

    draw.rounded_rectangle((60, 1100, 1540, 1140), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1110),
        "Data note: This page shows association, not causation. Rent is time-series by half-year, while homelessness is a regional snapshot repeated across rent periods.",
        fill="#52616B",
        font=get_font(17),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    rows = fetch_rows()
    latest = latest_rows(rows)
    if len(rows) != 99:
        raise ValueError(f"Expected 99 rent pressure rows, found {len(rows)}")
    if len(latest) != 9:
        raise ValueError(f"Expected 9 latest rent pressure rows, found {len(latest)}")
    write_csv(CSV_PATH, rows)
    write_csv(OUTPUT_CSV_PATH, rows)
    write_csv(LATEST_CSV_PATH, latest)
    write_csv(OUTPUT_LATEST_CSV_PATH, latest)
    write_spec(rows)
    write_mockup(rows)
    print(f"Created {CSV_PATH}")
    print(f"Created {OUTPUT_CSV_PATH}")
    print(f"Created {LATEST_CSV_PATH}")
    print(f"Created {OUTPUT_LATEST_CSV_PATH}")
    print(f"Created {SPEC_PATH}")
    print(f"Created {OUTPUT_SPEC_PATH}")
    print(f"Created {MOCKUP_PATH}")
    print(f"Created {OUTPUT_MOCKUP_PATH}")


if __name__ == "__main__":
    main()
