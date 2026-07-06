import csv
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "economic_context.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "economic_context.csv"
LATEST_CSV_PATH = POWER_BI_DIR / "economic_context_latest.csv"
OUTPUT_LATEST_CSV_PATH = OUTPUT_DIR / "economic_context_latest.csv"
SPEC_PATH = POWER_BI_DIR / "task23_economic_context_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task23_economic_context_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task23_economic_context_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task23_economic_context_page_mockup.png"

NUTS2_COLORS = {
    "Eastern and Midland": "#2F6AA8",
    "Northern and Western": "#2A9D8F",
    "Southern": "#D95F59",
}


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
                nuts2_region,
                year,
                unemployment_rate,
                county_count_in_nuts2,
                nuts2_count,
                unemployment_join_note,
                population_year,
                homeless_adults,
                population,
                homeless_adults_per_10000
            FROM vw_unemployment_context
            ORDER BY year, homelessness_region, nuts2_region
            """
        )
    ]
    con.close()
    return rows


def latest_year(rows):
    return max(row["year"] for row in rows)


def latest_rows(rows):
    year = latest_year(rows)
    return sorted(
        [row for row in rows if row["year"] == year],
        key=lambda row: (row["homelessness_region"], row["nuts2_region"]),
    )


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "homelessness_region",
        "nuts2_region",
        "year",
        "unemployment_rate",
        "county_count_in_nuts2",
        "nuts2_count",
        "unemployment_join_note",
        "population_year",
        "homeless_adults",
        "population",
        "homeless_adults_per_10000",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def nuts2_trend(rows):
    seen = {}
    for row in rows:
        key = (row["nuts2_region"], row["year"])
        seen[key] = row["unemployment_rate"]
    return [
        {"nuts2_region": nuts2, "year": year, "unemployment_rate": rate}
        for (nuts2, year), rate in sorted(seen.items(), key=lambda item: (item[0][0], item[0][1]))
    ]


def latest_nuts2_rates(rows):
    year = latest_year(rows)
    rates = {}
    for row in rows:
        if row["year"] == year:
            rates[row["nuts2_region"]] = row["unemployment_rate"]
    return rates


def write_spec(rows):
    latest = latest_rows(rows)
    year = latest_year(rows)
    rates = latest_nuts2_rates(rows)
    direct_regions = sorted({row["homelessness_region"] for row in latest if row["nuts2_count"] == 1})
    mixed_regions = sorted({row["homelessness_region"] for row in latest if row["nuts2_count"] > 1})
    highest_rate_nuts2 = max(rates.items(), key=lambda item: item[1])
    lowest_rate_nuts2 = min(rates.items(), key=lambda item: item[1])
    sample_rows = [
        [
            row["homelessness_region"],
            row["nuts2_region"],
            row["year"],
            row["unemployment_rate"],
            row["county_count_in_nuts2"],
            row["nuts2_count"],
            row["unemployment_join_note"],
        ]
        for row in latest
    ]

    spec = f"""# Task 23 - Economic Context Page Build Spec

## Page Intent

After this page, the user should understand how unemployment context can be read alongside homelessness rates, and why NUTS2 geography limits region-level interpretation.

## Data Source

Use SQL view:

```text
vw_unemployment_context
```

Power BI-ready extracts:

```text
Project/Power BI/economic_context.csv
Project/Power BI/economic_context_latest.csv
```

## Page Grain

Main extract:

```text
homelessness_region + nuts2_region + year
```

Latest extract:

```text
homelessness_region + nuts2_region
```

Expected rows:

```text
economic_context.csv = 60
economic_context_latest.csv = 10
```

The latest extract has 10 rows because North-East maps to two NUTS2 regions.

## Analytical Scope

Default year:

```text
{year}
```

Unemployment is available at NUTS2 level, not county or homelessness-region level. Do not interpret it as a precise local rate for every homelessness region.

## Required Fields

{md_table(["Field", "Use"], [
    ["`homelessness_region`", "Region label / table"],
    ["`nuts2_region`", "Line chart legend / geography context"],
    ["`year`", "Year axis / slicer"],
    ["`unemployment_rate`", "Economic context measure"],
    ["`county_count_in_nuts2`", "Bridge coverage"],
    ["`nuts2_count`", "Direct vs mixed mapping check"],
    ["`unemployment_join_note`", "Interpretation caveat"],
    ["`homeless_adults_per_10000`", "Homelessness context"],
])}

## KPI / Insight Cards

{md_table(["Card", "Expected Value"], [
    ["Default year", year],
    ["Highest NUTS2 unemployment", f"{highest_rate_nuts2[0]} ({highest_rate_nuts2[1]}%)"],
    ["Lowest NUTS2 unemployment", f"{lowest_rate_nuts2[0]} ({lowest_rate_nuts2[1]}%)"],
    ["Direct homelessness regions", len(direct_regions)],
    ["Mixed NUTS2 regions", ", ".join(mixed_regions)],
])}

## Visual 1 - NUTS2 Unemployment Trend

{md_table(["Setting", "Value"], [
    ["Visual type", "Line chart"],
    ["X-axis", "`year`"],
    ["Y-axis", "`unemployment_rate`"],
    ["Legend", "`nuts2_region`"],
    ["Title", "`NUTS2 Unemployment Trend`"],
])}

## Visual 2 - Latest Unemployment Context

{md_table(["Setting", "Value"], [
    ["Visual type", "Bar chart"],
    ["Y-axis", "`nuts2_region`"],
    ["X-axis", "`unemployment_rate`"],
    ["Default filter", f"`year = {year}`"],
    ["Title", "`Latest NUTS2 Unemployment Rate`"],
])}

## Visual 3 - Geography Interpretation Table

Columns:

{md_table(["Column", "Display Name"], [
    ["`homelessness_region`", "Homelessness Region"],
    ["`nuts2_region`", "NUTS2 Region"],
    ["`county_count_in_nuts2`", "Counties in NUTS2"],
    ["`nuts2_count`", "NUTS2 Count"],
    ["`unemployment_join_note`", "Interpretation Note"],
])}

## Data Note

Use this note:

```text
Unemployment data is NUTS2-level. North-East spans two NUTS2 regions, so its unemployment context should be read as mixed geography rather than a single direct regional rate.
```

## Latest Validation Sample

{md_table(["Region", "NUTS2", "Year", "Unemployment Rate", "County Count", "NUTS2 Count", "Join Note"], sample_rows)}

## Acceptance Criteria

- `economic_context.csv` contains 60 rows.
- `economic_context_latest.csv` contains 10 rows.
- Page clearly states that unemployment is NUTS2-level.
- North-East mixed geography is visible and not collapsed silently.
- Page avoids causal wording between unemployment and homelessness.
"""
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 22, y1 + 18), title, fill="#52616B", font=get_font(20))
    draw.text((x1 + 22, y1 + 58), value, fill="#17324D", font=get_font(30, bold=True))
    if subtitle:
        draw.text((x1 + 22, y1 + 96), subtitle, fill="#7A8A99", font=get_font(15))


def draw_line_chart(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "NUTS2 Unemployment Trend", fill="#17324D", font=get_font(25, bold=True))
    trend = nuts2_trend(rows)
    years = sorted({row["year"] for row in trend})
    nuts2s = sorted({row["nuts2_region"] for row in trend})
    min_y = min(row["unemployment_rate"] for row in trend) * 0.9
    max_y = max(row["unemployment_rate"] for row in trend) * 1.1
    plot = (x1 + 70, y1 + 85, x2 - 35, y2 - 55)
    px1, py1, px2, py2 = plot
    draw.line((px1, py2, px2, py2), fill="#9AA8B5", width=1)
    draw.line((px1, py1, px1, py2), fill="#9AA8B5", width=1)

    def map_x(year):
        return px1 + (year - years[0]) / (years[-1] - years[0]) * (px2 - px1)

    def map_y(value):
        return py2 - (value - min_y) / (max_y - min_y) * (py2 - py1)

    for nuts2 in nuts2s:
        series = [row for row in trend if row["nuts2_region"] == nuts2]
        points = [(map_x(row["year"]), map_y(row["unemployment_rate"])) for row in series]
        draw.line(points, fill=NUTS2_COLORS[nuts2], width=4)
        for point in points:
            x, y = point
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=NUTS2_COLORS[nuts2])
        last = series[-1]
        draw.text((points[-1][0] + 8, points[-1][1] - 8), f"{nuts2} {last['unemployment_rate']}%", fill=NUTS2_COLORS[nuts2], font=get_font(13, bold=True))

    for year in years:
        draw.text((map_x(year) - 13, py2 + 16), str(year), fill="#52616B", font=get_font(12))


def draw_latest_bars(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Latest NUTS2 Rate", fill="#17324D", font=get_font(25, bold=True))
    rates = latest_nuts2_rates(rows)
    ordered = sorted(rates.items(), key=lambda item: item[1], reverse=True)
    max_value = max(rates.values())
    label_x = x1 + 24
    bar_x = x1 + 210
    bar_width = x2 - bar_x - 90
    y = y1 + 82
    for nuts2, rate in ordered:
        width = round(bar_width * rate / max_value)
        draw.text((label_x, y + 1), nuts2, fill="#2F3A44", font=get_font(15))
        draw.rounded_rectangle((bar_x, y, bar_x + width, y + 22), radius=4, fill=NUTS2_COLORS[nuts2])
        draw.text((bar_x + width + 8, y), f"{rate:.1f}%", fill="#17324D", font=get_font(15, bold=True))
        y += 42


def draw_mapping_table(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Geography Interpretation", fill="#17324D", font=get_font(25, bold=True))
    headers = ["Region", "NUTS2", "Count", "Note"]
    xs = [x1 + 24, x1 + 200, x1 + 405, x1 + 475]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 96
    for row in rows:
        is_mixed = row["nuts2_count"] > 1
        note = "Mixed" if is_mixed else "Direct"
        color = "#9A3412" if is_mixed else "#2F3A44"
        values = [
            row["homelessness_region"],
            row["nuts2_region"],
            str(row["county_count_in_nuts2"]),
            note,
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=color if value == note else "#2F3A44", font=get_font(14, bold=value == note))
        y += 23


def draw_context_table(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Homelessness Rate Context", fill="#17324D", font=get_font(25, bold=True))
    unique = {}
    for row in rows:
        unique[row["homelessness_region"]] = row
    ordered = sorted(unique.values(), key=lambda row: row["homeless_adults_per_10000"], reverse=True)
    headers = ["Region", "Rate", "Adults"]
    xs = [x1 + 24, x1 + 260, x1 + 390]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 96
    for row in ordered:
        values = [row["homelessness_region"], f"{row['homeless_adults_per_10000']:.2f}", f"{row['homeless_adults']:,}"]
        bold = row["homelessness_region"] == "Dublin"
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill="#17324D" if bold else "#2F3A44", font=get_font(15, bold=bold))
        y += 23


def write_mockup(rows):
    width, height = 1600, 1160
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)
    latest = latest_rows(rows)
    year = latest_year(rows)
    rates = latest_nuts2_rates(rows)
    highest = max(rates.items(), key=lambda item: item[1])
    lowest = min(rates.items(), key=lambda item: item[1])
    mixed_regions = sorted({row["homelessness_region"] for row in latest if row["nuts2_count"] > 1})
    direct_count = len({row["homelessness_region"] for row in latest if row["nuts2_count"] == 1})

    draw.text((60, 50), "Economic Context", fill="#17324D", font=get_font(42, bold=True))
    draw.text((62, 102), "NUTS2 unemployment context and geography limitations", fill="#627386", font=get_font(23))

    draw_card(draw, (60, 146, 405, 270), "Default Year", str(year), "Latest unemployment year")
    draw_card(draw, (435, 146, 780, 270), "Highest NUTS2 Rate", highest[0].split()[0], f"{highest[1]:.1f}% unemployment")
    draw_card(draw, (810, 146, 1165, 270), "Lowest NUTS2 Rate", lowest[0].split()[0], f"{lowest[1]:.1f}% unemployment")
    draw_card(draw, (1195, 146, 1540, 270), "Mixed Geography", ", ".join(mixed_regions), f"{direct_count} direct regions")

    draw_line_chart(draw, (60, 320, 1010, 690), rows)
    draw_latest_bars(draw, (1040, 320, 1540, 690), rows)
    draw_mapping_table(draw, (60, 725, 1010, 1070), latest)
    draw_context_table(draw, (1040, 725, 1540, 1070), latest)

    draw.rounded_rectangle((60, 1100, 1540, 1140), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1110),
        "Data note: Unemployment is NUTS2-level. North-East spans two NUTS2 regions, so interpret its unemployment context as mixed geography.",
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
    if len(rows) != 60:
        raise ValueError(f"Expected 60 economic context rows, found {len(rows)}")
    if len(latest) != 10:
        raise ValueError(f"Expected 10 latest economic context rows, found {len(latest)}")
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
