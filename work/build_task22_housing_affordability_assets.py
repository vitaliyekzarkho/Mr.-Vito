import csv
import math
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "housing_affordability.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "housing_affordability.csv"
LATEST_RATIO_CSV_PATH = POWER_BI_DIR / "housing_affordability_latest_ratio.csv"
OUTPUT_LATEST_RATIO_CSV_PATH = OUTPUT_DIR / "housing_affordability_latest_ratio.csv"
SPEC_PATH = POWER_BI_DIR / "task22_housing_affordability_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task22_housing_affordability_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task22_housing_affordability_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task22_housing_affordability_page_mockup.png"


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
                population_weighted_mean_sale_price,
                population_weighted_median_annual_earnings,
                price_to_income_ratio,
                total_dwellings_built,
                dwellings_built_per_10000,
                estimated_total_floor_area_sqm,
                population_weighted_price_per_sqm,
                county_count,
                population_year,
                homeless_adults,
                population,
                homeless_adults_per_10000
            FROM vw_housing_affordability
            ORDER BY year, homelessness_region
            """
        )
    ]
    con.close()
    return rows


def latest_complete_ratio_year(rows):
    years = sorted({row["year"] for row in rows}, reverse=True)
    for year in years:
        year_rows = [row for row in rows if row["year"] == year]
        if len(year_rows) == 9 and all(row["price_to_income_ratio"] is not None for row in year_rows):
            return year
    raise ValueError("No complete price-to-income year found")


def latest_price_supply_year(rows):
    return max(row["year"] for row in rows)


def ratio_rows(rows):
    year = latest_complete_ratio_year(rows)
    return sorted([row for row in rows if row["year"] == year], key=lambda row: row["price_to_income_ratio"], reverse=True)


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "homelessness_region",
        "year",
        "population_weighted_mean_sale_price",
        "population_weighted_median_annual_earnings",
        "price_to_income_ratio",
        "total_dwellings_built",
        "dwellings_built_per_10000",
        "estimated_total_floor_area_sqm",
        "population_weighted_price_per_sqm",
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


def pearson(rows, x_field, y_field):
    xs = [row[x_field] for row in rows]
    ys = [row[y_field] for row in rows]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - mean_x) ** 2 for x in xs) * sum((y - mean_y) ** 2 for y in ys))
    return round(numerator / denominator, 3) if denominator else 0


def linear_fit(rows, x_field, y_field):
    xs = [row[x_field] for row in rows]
    ys = [row[y_field] for row in rows]
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator
    intercept = mean_y - slope * mean_x
    return slope, intercept


def national_trend(rows, field):
    by_year = {}
    for row in rows:
        if row[field] is None:
            continue
        item = by_year.setdefault(row["year"], {"weighted": 0, "population": 0})
        item["weighted"] += row[field] * row["population"]
        item["population"] += row["population"]
    return [
        {"year": year, field: round(value["weighted"] / value["population"], 2)}
        for year, value in sorted(by_year.items())
    ]


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def missing_summary(rows):
    fields = [
        "population_weighted_mean_sale_price",
        "population_weighted_median_annual_earnings",
        "price_to_income_ratio",
        "total_dwellings_built",
        "dwellings_built_per_10000",
        "population_weighted_price_per_sqm",
    ]
    return [[field, sum(1 for row in rows if row[field] is None)] for field in fields]


def write_spec(rows):
    default_year = latest_complete_ratio_year(rows)
    latest_year = latest_price_supply_year(rows)
    latest_rows = ratio_rows(rows)
    corr = pearson(latest_rows, "price_to_income_ratio", "homeless_adults_per_10000")
    highest_ratio = max(latest_rows, key=lambda row: row["price_to_income_ratio"])
    highest_supply = max(latest_rows, key=lambda row: row["dwellings_built_per_10000"])
    highest_rate = max(latest_rows, key=lambda row: row["homeless_adults_per_10000"])
    price_trend = national_trend(rows, "population_weighted_mean_sale_price")
    price_growth = round(
        (price_trend[-1]["population_weighted_mean_sale_price"] - price_trend[0]["population_weighted_mean_sale_price"])
        / price_trend[0]["population_weighted_mean_sale_price"]
        * 100,
        1,
    )
    sample_rows = [
        [
            row["homelessness_region"],
            row["year"],
            row["price_to_income_ratio"],
            row["population_weighted_mean_sale_price"],
            row["population_weighted_median_annual_earnings"],
            row["dwellings_built_per_10000"],
            row["homeless_adults_per_10000"],
        ]
        for row in latest_rows
    ]

    spec = f"""# Task 22 - Housing Affordability Page Build Spec

## Page Intent

After this page, the user should understand how housing prices, income, and new housing supply relate to homelessness rates across regions, while treating the comparison as contextual association rather than causation.

## Data Source

Use SQL view:

```text
vw_housing_affordability
```

Power BI-ready extracts:

```text
Project/Power BI/housing_affordability.csv
Project/Power BI/housing_affordability_latest_ratio.csv
```

## Page Grain

Main extract:

```text
homelessness_region + year
```

Latest complete affordability extract:

```text
homelessness_region
```

Expected rows:

```text
housing_affordability.csv = 135
housing_affordability_latest_ratio.csv = 9
```

## Analytical Scope

The default affordability year is:

```text
{default_year}
```

The latest housing year is `{latest_year}`, but `price_to_income_ratio` is unavailable for that year because earnings are missing. Do not use `{latest_year}` as the default ratio year.

## Required Fields

{md_table(["Field", "Use"], [
    ["`homelessness_region`", "Point / axis / slicer"],
    ["`year`", "Year slicer"],
    ["`population_weighted_mean_sale_price`", "Price measure"],
    ["`population_weighted_median_annual_earnings`", "Income measure"],
    ["`price_to_income_ratio`", "Affordability measure"],
    ["`dwellings_built_per_10000`", "Supply context"],
    ["`homeless_adults_per_10000`", "Homelessness rate"],
])}

## KPI / Insight Cards

{md_table(["Card", "Expected Value"], [
    ["Default affordability year", default_year],
    ["Correlation: ratio vs rate", corr],
    ["Highest price-to-income ratio", f"{highest_ratio['homelessness_region']} ({highest_ratio['price_to_income_ratio']})"],
    ["Highest supply per 10,000", f"{highest_supply['homelessness_region']} ({highest_supply['dwellings_built_per_10000']})"],
    ["Highest homelessness rate", f"{highest_rate['homelessness_region']} ({highest_rate['homeless_adults_per_10000']})"],
    ["National weighted sale price growth", f"{price_growth}% from {price_trend[0]['year']} to {price_trend[-1]['year']}"],
])}

## Visual 1 - Affordability vs Homelessness Rate

{md_table(["Setting", "Value"], [
    ["Visual type", "Scatter chart"],
    ["X-axis", "`price_to_income_ratio`"],
    ["Y-axis", "`homeless_adults_per_10000`"],
    ["Details", "`homelessness_region`"],
    ["Tooltip", "`population_weighted_mean_sale_price`, `population_weighted_median_annual_earnings`, `dwellings_built_per_10000`"],
    ["Default filter", f"`year = {default_year}`"],
    ["Title", "`Affordability vs Homelessness Rate`"],
])}

## Visual 2 - Housing Supply Context

{md_table(["Setting", "Value"], [
    ["Visual type", "Sorted bar chart"],
    ["Y-axis", "`homelessness_region`"],
    ["X-axis", "`dwellings_built_per_10000`"],
    ["Default filter", f"`year = {default_year}`"],
    ["Title", "`Dwellings Built per 10,000 Population`"],
])}

## Visual 3 - Sale Price Trend

{md_table(["Setting", "Value"], [
    ["Visual type", "Line chart"],
    ["X-axis", "`year`"],
    ["Y-axis", "`population_weighted_mean_sale_price`"],
    ["Legend", "`homelessness_region` or national weighted trend"],
    ["Title", "`Weighted Mean Sale Price Trend`"],
])}

## Data Note

Use this note:

```text
This page shows contextual association, not causation. Price-to-income ratio uses 2023 because 2024 earnings are unavailable in the clean housing dataset.
```

## Missing Value Summary

{md_table(["Field", "Missing rows"], missing_summary(rows))}

## Latest Complete Ratio Validation Sample

{md_table(["Region", "Year", "Price-to-Income", "Mean Sale Price", "Median Earnings", "Dwellings per 10,000", "Rate per 10,000"], sample_rows)}

## Acceptance Criteria

- `housing_affordability.csv` contains 135 rows.
- `housing_affordability_latest_ratio.csv` contains 9 rows.
- Main affordability scatter defaults to {default_year}, not {latest_year}.
- Page includes a visible note explaining missing 2024 earnings.
- Page avoids causal language and frames housing metrics as context.
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
    draw.text((x1 + 24, y1 + 22), "Affordability vs Homelessness Rate", fill="#17324D", font=get_font(25, bold=True))
    draw.text((x1 + 24, y1 + 55), "Price-to-income ratio; observed association only", fill="#627386", font=get_font(16))

    plot = (x1 + 82, y1 + 95, x2 - 42, y2 - 55)
    px1, py1, px2, py2 = plot
    draw.line((px1, py2, px2, py2), fill="#9AA8B5", width=1)
    draw.line((px1, py1, px1, py2), fill="#9AA8B5", width=1)
    min_x = min(row["price_to_income_ratio"] for row in rows) * 0.94
    max_x = max(row["price_to_income_ratio"] for row in rows) * 1.04
    min_y = 0
    max_y = max(row["homeless_adults_per_10000"] for row in rows) * 1.12
    slope, intercept = linear_fit(rows, "price_to_income_ratio", "homeless_adults_per_10000")

    def map_x(value):
        return px1 + (value - min_x) / (max_x - min_x) * (px2 - px1)

    def map_y(value):
        return py2 - (value - min_y) / (max_y - min_y) * (py2 - py1)

    draw.line(
        (map_x(min_x), map_y(slope * min_x + intercept), map_x(max_x), map_y(slope * max_x + intercept)),
        fill="#D95F59",
        width=3,
    )
    offsets = {
        "Dublin": (10, -8),
        "Mid-East": (10, 12),
        "South-West": (10, -16),
        "South-East": (8, 18),
        "West": (12, -2),
        "Mid-West": (10, -16),
        "North-East": (10, 18),
        "Midlands": (10, -18),
        "North-West": (10, -2),
    }
    for row in rows:
        cx = map_x(row["price_to_income_ratio"])
        cy = map_y(row["homeless_adults_per_10000"])
        label = row["homelessness_region"]
        radius = 8 if label != "Dublin" else 11
        fill = "#2F6AA8" if label != "Dublin" else "#D95F59"
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill, outline="#FFFFFF", width=2)
        dx, dy = offsets.get(label, (10, -8))
        draw.text((cx + dx, cy + dy), label, fill="#17324D", font=get_font(14, bold=label == "Dublin"))
    draw.text((px1, py2 + 22), "Price-to-income ratio", fill="#52616B", font=get_font(15))
    draw.text((px1 - 50, py1 - 22), "Rate per 10,000", fill="#52616B", font=get_font(15))


def draw_supply_chart(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Dwellings Built per 10,000", fill="#17324D", font=get_font(25, bold=True))
    ordered = sorted(rows, key=lambda row: row["dwellings_built_per_10000"], reverse=True)
    max_value = max(row["dwellings_built_per_10000"] for row in ordered)
    label_x = x1 + 24
    bar_x = x1 + 185
    bar_width = x2 - bar_x - 90
    y = y1 + 76
    for row in ordered:
        value = row["dwellings_built_per_10000"]
        width = round(bar_width * value / max_value)
        draw.text((label_x, y + 1), row["homelessness_region"], fill="#2F3A44", font=get_font(15))
        draw.rounded_rectangle((bar_x, y, bar_x + width, y + 20), radius=4, fill="#2A9D8F")
        draw.text((bar_x + width + 8, y - 1), f"{value:.1f}", fill="#17324D", font=get_font(14, bold=True))
        y += 23


def draw_price_trend(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Weighted Mean Sale Price Trend", fill="#17324D", font=get_font(25, bold=True))
    trend = national_trend(rows, "population_weighted_mean_sale_price")
    plot = (x1 + 70, y1 + 80, x2 - 34, y2 - 50)
    px1, py1, px2, py2 = plot
    min_y = min(row["population_weighted_mean_sale_price"] for row in trend) * 0.94
    max_y = max(row["population_weighted_mean_sale_price"] for row in trend) * 1.04

    def map_x(index):
        return px1 + index / (len(trend) - 1) * (px2 - px1)

    def map_y(value):
        return py2 - (value - min_y) / (max_y - min_y) * (py2 - py1)

    draw.line((px1, py2, px2, py2), fill="#9AA8B5", width=1)
    draw.line((px1, py1, px1, py2), fill="#9AA8B5", width=1)
    points = [(map_x(i), map_y(row["population_weighted_mean_sale_price"])) for i, row in enumerate(trend)]
    draw.line(points, fill="#2F6AA8", width=4)
    for i, point in enumerate(points):
        x, y = point
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill="#2F6AA8")
        if i in {0, len(points) - 1}:
            draw.text((x - 40, y - 26), f"EUR {trend[i]['population_weighted_mean_sale_price']:,.0f}", fill="#17324D", font=get_font(13, bold=True))
    for i, row in enumerate(trend):
        if i % 3 == 0 or i == len(trend) - 1:
            draw.text((map_x(i) - 14, py2 + 16), str(row["year"]), fill="#52616B", font=get_font(12))


def draw_table(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Affordability Ranking", fill="#17324D", font=get_font(25, bold=True))
    headers = ["Region", "Ratio", "Price", "Rate"]
    xs = [x1 + 24, x1 + 250, x1 + 360, x1 + 520]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 96
    for row in rows:
        values = [
            row["homelessness_region"],
            f"{row['price_to_income_ratio']:.2f}",
            f"EUR {row['population_weighted_mean_sale_price']:,.0f}",
            f"{row['homeless_adults_per_10000']:.2f}",
        ]
        bold = row["homelessness_region"] == "Dublin"
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill="#17324D" if bold else "#2F3A44", font=get_font(15, bold=bold))
        y += 23


def write_mockup(rows):
    width, height = 1600, 1160
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)
    latest_rows = ratio_rows(rows)
    default_year = latest_complete_ratio_year(rows)
    latest_year = latest_price_supply_year(rows)
    corr = pearson(latest_rows, "price_to_income_ratio", "homeless_adults_per_10000")
    highest_ratio = max(latest_rows, key=lambda row: row["price_to_income_ratio"])
    highest_supply = max(latest_rows, key=lambda row: row["dwellings_built_per_10000"])
    price_trend = national_trend(rows, "population_weighted_mean_sale_price")
    price_growth = round(
        (price_trend[-1]["population_weighted_mean_sale_price"] - price_trend[0]["population_weighted_mean_sale_price"])
        / price_trend[0]["population_weighted_mean_sale_price"]
        * 100,
        1,
    )

    draw.text((60, 50), "Housing Affordability", fill="#17324D", font=get_font(42, bold=True))
    draw.text((62, 102), "Housing prices, income and supply context by homelessness region", fill="#627386", font=get_font(23))

    draw_card(draw, (60, 146, 405, 270), "Default Ratio Year", str(default_year), f"{latest_year} earnings unavailable")
    draw_card(draw, (435, 146, 780, 270), "Correlation", f"{corr:.3f}", "Ratio vs rate; association only")
    draw_card(draw, (810, 146, 1165, 270), "Highest Ratio", highest_ratio["homelessness_region"], f"{highest_ratio['price_to_income_ratio']:.2f} price-to-income")
    draw_card(draw, (1195, 146, 1540, 270), "Highest Supply", highest_supply["homelessness_region"], f"{highest_supply['dwellings_built_per_10000']:.1f} per 10,000")

    draw_scatter(draw, (60, 320, 1010, 720), latest_rows)
    draw_price_trend(draw, (1040, 320, 1540, 720), rows)
    draw_table(draw, (60, 755, 790, 1070), latest_rows)
    draw_supply_chart(draw, (830, 755, 1540, 1070), latest_rows)

    draw.rounded_rectangle((60, 1100, 1540, 1140), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1110),
        "Data note: This page shows contextual association, not causation. Price-to-income ratio uses 2023 because 2024 earnings are unavailable.",
        fill="#52616B",
        font=get_font(17),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    rows = fetch_rows()
    latest = ratio_rows(rows)
    if len(rows) != 135:
        raise ValueError(f"Expected 135 housing affordability rows, found {len(rows)}")
    if len(latest) != 9:
        raise ValueError(f"Expected 9 latest ratio rows, found {len(latest)}")
    write_csv(CSV_PATH, rows)
    write_csv(OUTPUT_CSV_PATH, rows)
    write_csv(LATEST_RATIO_CSV_PATH, latest)
    write_csv(OUTPUT_LATEST_RATIO_CSV_PATH, latest)
    write_spec(rows)
    write_mockup(rows)
    print(f"Created {CSV_PATH}")
    print(f"Created {OUTPUT_CSV_PATH}")
    print(f"Created {LATEST_RATIO_CSV_PATH}")
    print(f"Created {OUTPUT_LATEST_RATIO_CSV_PATH}")
    print(f"Created {SPEC_PATH}")
    print(f"Created {OUTPUT_SPEC_PATH}")
    print(f"Created {MOCKUP_PATH}")
    print(f"Created {OUTPUT_MOCKUP_PATH}")


if __name__ == "__main__":
    main()
