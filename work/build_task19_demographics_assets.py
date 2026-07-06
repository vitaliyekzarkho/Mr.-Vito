import csv
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "demographic_profile.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "demographic_profile.csv"
SPEC_PATH = POWER_BI_DIR / "task19_demographics_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task19_demographics_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task19_demographics_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task19_demographics_page_mockup.png"


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
                profile_type,
                category,
                adults,
                total_adults,
                share_pct
            FROM vw_demographic_profile
            ORDER BY
                homelessness_region,
                profile_type,
                CASE category
                    WHEN 'Male' THEN 1
                    WHEN 'Female' THEN 2
                    WHEN '18-24' THEN 1
                    WHEN '25-44' THEN 2
                    WHEN '45-64' THEN 3
                    WHEN '65+' THEN 4
                    ELSE 99
                END
            """
        )
    ]
    con.close()
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["homelessness_region", "profile_type", "category", "adults", "total_adults", "share_pct"]
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


def region_order(rows):
    totals = {}
    for row in rows:
        totals[row["homelessness_region"]] = int(row["total_adults"])
    return [region for region, _ in sorted(totals.items(), key=lambda item: item[1], reverse=True)]


def pivot(rows, profile_type):
    result = {}
    for row in rows:
        if row["profile_type"] != profile_type:
            continue
        result.setdefault(row["homelessness_region"], {})[row["category"]] = row
    return result


def write_spec(rows):
    gender_rows = [row for row in rows if row["profile_type"] == "gender"]
    age_rows = [row for row in rows if row["profile_type"] == "age"]
    order = region_order(rows)
    male_share = round(sum(int(r["adults"]) for r in gender_rows if r["category"] == "Male") / sum(int(r["total_adults"]) for r in gender_rows if r["category"] == "Male") * 100, 2)
    female_share = round(100 - male_share, 2)
    age_totals = {}
    total_adults = sum(int(r["adults"]) for r in age_rows if r["category"] in {"18-24", "25-44", "45-64", "65+"})
    for category in ["18-24", "25-44", "45-64", "65+"]:
        age_totals[category] = sum(int(r["adults"]) for r in age_rows if r["category"] == category)
    largest_age = max(age_totals.items(), key=lambda item: item[1])
    largest_age_share = round(largest_age[1] / total_adults * 100, 2)

    sample_rows = sorted(age_rows, key=lambda r: (order.index(r["homelessness_region"]), r["category"]))[:12]

    spec = f"""# Task 19 - Demographics Page Build Spec

## Page Intent

After this page, the user should understand which age and gender groups make up the adult homeless population, and how this profile differs between regions.

## Data Source

Use SQL view:

```text
vw_demographic_profile
```

Power BI-ready extract:

```text
Project/Power BI/demographic_profile.csv
```

## Page Grain

One row per:

```text
homelessness_region + profile_type + category
```

Expected rows:

```text
54
```

## Required Fields

| Field | Use |
|---|---|
| `homelessness_region` | Axis / slicer |
| `profile_type` | Split gender vs age |
| `category` | Legend/category |
| `adults` | Count |
| `total_adults` | Denominator |
| `share_pct` | 100% composition |

## KPI / Insight Cards

| Card | Expected Value |
|---|---:|
| Male share | {male_share}% |
| Female share | {female_share}% |
| Largest age group | {largest_age[0]} |
| Largest age group share | {largest_age_share}% |

## Visual 1 - Gender Composition

| Setting | Value |
|---|---|
| Visual type | 100% stacked bar chart |
| Y-axis | `homelessness_region` |
| Legend | `category` filtered to Male/Female |
| Values | `adults` or `share_pct` |
| Sort | Descending by `total_adults` or same order as Overview |
| Title | `Gender Composition by Region` |

## Visual 2 - Age Composition

| Setting | Value |
|---|---|
| Visual type | 100% stacked bar chart |
| Y-axis | `homelessness_region` |
| Legend | `category` filtered to age groups |
| Values | `adults` or `share_pct` |
| Sort | Descending by `total_adults` or same order as Overview |
| Title | `Age Composition by Region` |

## Visual 3 - Optional Detail Table

Columns:

| Column | Display Name |
|---|---|
| `homelessness_region` | Region |
| `profile_type` | Profile |
| `category` | Category |
| `adults` | Adults |
| `share_pct` | Share % |

## Slicer

Optional:

```text
homelessness_region
```

## Data Note

Use this note:

```text
Percentages show composition, not scale. Use alongside total adult counts from Overview.
```

## Validation Sample

{md_table(["homelessness_region", "profile_type", "category", "adults", "total_adults", "share_pct"], sample_rows)}

## Acceptance Criteria

| Check | Expected |
|---|---|
| Page answers demographics question | Yes |
| Rows in dataset | 54 |
| Gender categories | Male, Female |
| Age categories | 18-24, 25-44, 45-64, 65+ |
| Data note visible | Yes |
| Composition not confused with scale | Yes |
"""
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=16, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 22, y1 + 16), title, fill="#52616B", font=get_font(21))
    draw.text((x1 + 22, y1 + 54), value, fill="#16324F", font=get_font(34, True))
    if subtitle:
        draw.text((x1 + 22, y2 - 32), subtitle, fill="#7A8793", font=get_font(16))


def draw_stacked_chart(draw, box, title, order, data, categories, colors):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 24, y1 + 18), title, fill="#16324F", font=get_font(25, True))

    legend_x = x1 + 24
    legend_y = y1 + 58
    for category in categories:
        draw.rounded_rectangle((legend_x, legend_y + 4, legend_x + 18, legend_y + 22), radius=4, fill=colors[category])
        draw.text((legend_x + 26, legend_y), category, fill="#52616B", font=get_font(16))
        legend_x += 120

    chart_x = x1 + 150
    chart_y = y1 + 100
    chart_w = x2 - chart_x - 40
    bar_h = 22
    gap = 14
    for i, region in enumerate(order):
        y = chart_y + i * (bar_h + gap)
        draw.text((x1 + 24, y - 1), region, fill="#263238", font=get_font(17))
        running_x = chart_x
        for category in categories:
            share = float(data[region][category]["share_pct"])
            segment_w = int(chart_w * share / 100)
            draw.rectangle((running_x, y, running_x + segment_w, y + bar_h), fill=colors[category])
            if share >= 12:
                draw.text((running_x + 5, y - 1), f"{share:.0f}%", fill="#FFFFFF", font=get_font(14, True))
            running_x += segment_w
        draw.rounded_rectangle((chart_x, y, chart_x + chart_w, y + bar_h), radius=7, outline="#FFFFFF", width=1)


def write_mockup(rows):
    order = region_order(rows)
    gender = pivot(rows, "gender")
    age = pivot(rows, "age")
    gender_rows = [row for row in rows if row["profile_type"] == "gender"]
    age_rows = [row for row in rows if row["profile_type"] == "age"]
    male_total = sum(int(r["adults"]) for r in gender_rows if r["category"] == "Male")
    female_total = sum(int(r["adults"]) for r in gender_rows if r["category"] == "Female")
    total = male_total + female_total
    male_share = male_total / total * 100
    female_share = female_total / total * 100
    age_totals = {
        category: sum(int(r["adults"]) for r in age_rows if r["category"] == category)
        for category in ["18-24", "25-44", "45-64", "65+"]
    }
    largest_age = max(age_totals.items(), key=lambda item: item[1])
    largest_age_share = largest_age[1] / sum(age_totals.values()) * 100

    image = Image.new("RGB", (1600, 900), "#F5F7FA")
    draw = ImageDraw.Draw(image)
    draw.text((60, 42), "Demographics", fill="#102A43", font=get_font(42, True))
    draw.text((62, 94), "Adult homelessness profile by gender and age group", fill="#627384", font=get_font(22))

    draw_card(draw, (60, 145, 405, 270), "Male Share", f"{male_share:.1f}%", f"{male_total:,} adults")
    draw_card(draw, (435, 145, 780, 270), "Female Share", f"{female_share:.1f}%", f"{female_total:,} adults")
    draw_card(draw, (810, 145, 1165, 270), "Largest Age Group", largest_age[0], f"{largest_age_share:.1f}% of adults")
    draw_card(draw, (1195, 145, 1540, 270), "Total Adults", f"{total:,}", "Across 9 regions")

    draw_stacked_chart(
        draw,
        (60, 320, 770, 770),
        "Gender Composition by Region",
        order,
        gender,
        ["Male", "Female"],
        {"Male": "#2563A6", "Female": "#D1495B"},
    )
    draw_stacked_chart(
        draw,
        (830, 320, 1540, 770),
        "Age Composition by Region",
        order,
        age,
        ["18-24", "25-44", "45-64", "65+"],
        {"18-24": "#0F766E", "25-44": "#2A9D8F", "45-64": "#E9C46A", "65+": "#F4A261"},
    )

    draw.rounded_rectangle((60, 815, 1540, 865), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 829),
        "Data note: Percentages show composition, not scale. Use alongside total adult counts from Overview.",
        fill="#52616B",
        font=get_font(20),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    rows = fetch_rows()
    if len(rows) != 54:
        raise ValueError(f"Expected 54 demographics rows, found {len(rows)}")
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
