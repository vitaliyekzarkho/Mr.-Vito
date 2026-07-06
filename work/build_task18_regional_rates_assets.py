import csv
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "regional_rates_ranked.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "regional_rates_ranked.csv"
SPEC_PATH = POWER_BI_DIR / "task18_regional_rates_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task18_regional_rates_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task18_regional_rates_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task18_regional_rates_page_mockup.png"


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
    base_rows = [
        dict(row)
        for row in con.execute(
            """
            SELECT
                homelessness_region,
                population_year,
                homeless_adults,
                population,
                homeless_adults_per_10000
            FROM vw_homelessness_rate_per_10000
            """
        )
    ]
    con.close()

    by_rate = sorted(base_rows, key=lambda r: r["homeless_adults_per_10000"], reverse=True)
    by_absolute = sorted(base_rows, key=lambda r: r["homeless_adults"], reverse=True)
    rate_rank = {row["homelessness_region"]: index + 1 for index, row in enumerate(by_rate)}
    absolute_rank = {row["homelessness_region"]: index + 1 for index, row in enumerate(by_absolute)}

    rows = []
    for row in by_rate:
        region = row["homelessness_region"]
        enriched = dict(row)
        enriched["rate_rank"] = rate_rank[region]
        enriched["absolute_rank"] = absolute_rank[region]
        enriched["rank_change_after_normalisation"] = absolute_rank[region] - rate_rank[region]
        rows.append(enriched)
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rate_rank",
        "absolute_rank",
        "rank_change_after_normalisation",
        "homelessness_region",
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
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)


def write_spec(rows):
    highest = rows[0]
    lowest = rows[-1]
    ratio = round(highest["homeless_adults_per_10000"] / lowest["homeless_adults_per_10000"], 1)

    spec = f"""# Task 18 - Regional Rates Page Build Spec

## Goal

Build the second Power BI page:

```text
Regional Rates
```

This page should not repeat the Overview page. It should answer:

```text
Which regions change their position after normalising homelessness by population?
```

## Data Source

Use SQL view:

```text
vw_homelessness_rate_per_10000
```

Power BI-ready extract:

```text
Project/Power BI/regional_rates_ranked.csv
```

## Page Grain

One row per:

```text
homelessness_region
```

Expected rows:

```text
9
```

## Required Fields

| Field | Use |
|---|---|
| `rate_rank` | Ranking table |
| `absolute_rank` | Compare raw-count rank vs rate rank |
| `rank_change_after_normalisation` | Show ranking shift |
| `homelessness_region` | Axis / slicer |
| `homeless_adults` | Absolute count |
| `population` | Denominator |
| `homeless_adults_per_10000` | Main metric |

## KPI Cards

| KPI | Expected Value |
|---|---:|
| Highest Regional Rate | {highest['homelessness_region']} - {highest['homeless_adults_per_10000']} |
| Lowest Regional Rate | {lowest['homelessness_region']} - {lowest['homeless_adults_per_10000']} |

## Insight Card

Suggested dynamic text:

```text
{highest['homelessness_region']}'s rate is approximately {ratio}x higher than {lowest['homelessness_region']} in the analysed dataset.
```

## DAX Measures

```DAX
Highest Regional Rate =
MAX(regional_rates[homeless_adults_per_10000])
```

```DAX
Lowest Regional Rate =
MIN(regional_rates[homeless_adults_per_10000])
```

```DAX
Rate Gap =
[Highest Regional Rate] - [Lowest Regional Rate]
```

```DAX
Rate Ratio =
DIVIDE([Highest Regional Rate], [Lowest Regional Rate])
```

## Visual 1 - Sorted Bar Chart

| Setting | Value |
|---|---|
| Visual type | Clustered bar chart |
| Y-axis | `homelessness_region` |
| X-axis | `homeless_adults_per_10000` |
| Sort | Descending by rate |
| Data labels | On |
| Title | `Homeless Adults per 10,000 Population` |

## Visual 2 - Ranking Table

Columns:

| Column | Display Name |
|---|---|
| `rate_rank` | Rank |
| `homelessness_region` | Region |
| `homeless_adults` | Homeless Adults |
| `population` | Population |
| `homeless_adults_per_10000` | Rate per 10,000 |
| `absolute_rank` | Raw Count Rank |
| `rank_change_after_normalisation` | Rank Change |

Sort table by:

```text
rate_rank ascending
```

## Optional Visual 3 - Insight Card

Use a text box or smart narrative card.

Text:

```text
{highest['homelessness_region']}'s rate is approximately {ratio}x higher than {lowest['homelessness_region']} in the analysed dataset.
```

## Slicer

Optional:

```text
homelessness_region
```

Do not add extra filters yet.

## Data Note

Use this note:

```text
Rates are calculated using 2022 county population aggregated to homelessness regions via the geography bridge.
```

## Validation Table

{md_table(["rate_rank", "absolute_rank", "rank_change_after_normalisation", "homelessness_region", "homeless_adults", "population", "homeless_adults_per_10000"], rows)}

## Acceptance Criteria

| Check | Expected |
|---|---|
| Page answers ranking-normalisation question | Yes |
| Regional rows | 9 |
| Highest rate | {highest['homelessness_region']} |
| Lowest rate | {lowest['homelessness_region']} |
| Bar chart sorted by rate | Yes |
| Ranking table sorted by rate rank | Yes |
| Data note visible | Yes |
"""
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 24, y1 + 18), title, fill="#52616B", font=get_font(22))
    draw.text((x1 + 24, y1 + 58), value, fill="#16324F", font=get_font(34, True))
    if subtitle:
        draw.text((x1 + 24, y2 - 34), subtitle, fill="#7A8793", font=get_font(17))


def draw_bar_chart(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 24, y1 + 18), "Homeless Adults per 10,000 Population", fill="#16324F", font=get_font(25, True))
    chart_x = x1 + 180
    chart_y = y1 + 70
    chart_w = x2 - chart_x - 92
    bar_h = 22
    gap = 14
    max_value = max(float(row["homeless_adults_per_10000"]) for row in rows)
    for i, row in enumerate(rows):
        y = chart_y + i * (bar_h + gap)
        value = float(row["homeless_adults_per_10000"])
        bar_w = int((value / max_value) * chart_w)
        draw.text((x1 + 24, y - 1), row["homelessness_region"], fill="#263238", font=get_font(18))
        draw.rounded_rectangle((chart_x, y, chart_x + chart_w, y + bar_h), radius=8, fill="#EEF3F7")
        draw.rounded_rectangle((chart_x, y, chart_x + bar_w, y + bar_h), radius=8, fill="#0F766E")
        draw.text((chart_x + bar_w + 10, y - 2), f"{value:.2f}", fill="#263238", font=get_font(17, True))


def draw_table(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 24, y1 + 18), "Ranking Table", fill="#16324F", font=get_font(25, True))
    headers = ["Rank", "Region", "Adults", "Population", "Rate", "Raw Rank", "Change"]
    xs = [x1 + 24, x1 + 84, x1 + 228, x1 + 330, x1 + 470, x1 + 560, x1 + 665]
    y = y1 + 65
    for x, header in zip(xs, headers):
        draw.text((x, y), header, fill="#52616B", font=get_font(15, True))
    y += 26
    for row in rows:
        values = [
            row["rate_rank"],
            row["homelessness_region"],
            f"{int(row['homeless_adults']):,}",
            f"{int(row['population']):,}",
            f"{float(row['homeless_adults_per_10000']):.2f}",
            row["absolute_rank"],
            f"{int(row['rank_change_after_normalisation']):+d}",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), str(value), fill="#263238", font=get_font(15))
        y += 30


def write_mockup(rows):
    highest = rows[0]
    lowest = rows[-1]
    ratio = round(highest["homeless_adults_per_10000"] / lowest["homeless_adults_per_10000"], 1)

    image = Image.new("RGB", (1600, 900), "#F5F7FA")
    draw = ImageDraw.Draw(image)
    draw.text((60, 42), "Regional Rates", fill="#102A43", font=get_font(42, True))
    draw.text((62, 94), "How regional rankings change after normalising by population", fill="#627384", font=get_font(22))

    draw_card(
        draw,
        (60, 145, 520, 275),
        "Highest Regional Rate",
        f"{highest['homelessness_region']}",
        f"{highest['homeless_adults_per_10000']:.2f} per 10,000",
    )
    draw_card(
        draw,
        (560, 145, 1020, 275),
        "Lowest Regional Rate",
        f"{lowest['homelessness_region']}",
        f"{lowest['homeless_adults_per_10000']:.2f} per 10,000",
    )
    draw_card(
        draw,
        (1060, 145, 1540, 275),
        "Insight",
        f"{ratio}x higher",
        f"{highest['homelessness_region']} vs {lowest['homelessness_region']}",
    )

    draw_bar_chart(draw, (60, 320, 770, 770), rows)
    draw_table(draw, (830, 320, 1540, 770), rows)

    draw.rounded_rectangle((60, 815, 1540, 865), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 829),
        "Data note: Rates are calculated using 2022 county population aggregated to homelessness regions via the geography bridge.",
        fill="#52616B",
        font=get_font(20),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    rows = fetch_rows()
    if len(rows) != 9:
        raise ValueError(f"Expected 9 regional rows, found {len(rows)}")
    write_csv(CSV_PATH, rows)
    write_csv(OUTPUT_CSV_PATH, rows)
    write_spec(rows)
    write_mockup(rows)
    print(f"Created {CSV_PATH}")
    print(f"Created {OUTPUT_CSV_PATH}")
    print(f"Created {SPEC_PATH}")
    print(f"Created {OUTPUT_SPEC_PATH}")
    print(f"Created {MOCKUP_PATH}")
    print(f"Created {OUTPUT_MOCKUP_PATH}")


if __name__ == "__main__":
    main()
