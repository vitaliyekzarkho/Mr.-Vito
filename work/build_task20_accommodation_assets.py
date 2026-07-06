import csv
import sqlite3
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "accommodation_profile.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "accommodation_profile.csv"
SPEC_PATH = POWER_BI_DIR / "task20_accommodation_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task20_accommodation_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task20_accommodation_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task20_accommodation_page_mockup.png"

ACCOMMODATION_ORDER = [
    "Private Emergency Accommodation",
    "Supported Temporary Accommodation",
    "Temporary Emergency Accommodation",
    "Other Accommodation",
]

COLORS = {
    "Private Emergency Accommodation": "#2F6AA8",
    "Supported Temporary Accommodation": "#2A9D8F",
    "Temporary Emergency Accommodation": "#E9C46A",
    "Other Accommodation": "#D95F59",
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
                accommodation_type,
                adults,
                total_adults,
                share_of_total_adults_pct
            FROM vw_accommodation_profile
            ORDER BY
                homelessness_region,
                CASE accommodation_type
                    WHEN 'Private Emergency Accommodation' THEN 1
                    WHEN 'Supported Temporary Accommodation' THEN 2
                    WHEN 'Temporary Emergency Accommodation' THEN 3
                    WHEN 'Other Accommodation' THEN 4
                    ELSE 99
                END
            """
        )
    ]
    con.close()
    return rows


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "homelessness_region",
        "accommodation_type",
        "adults",
        "total_adults",
        "share_of_total_adults_pct",
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


def region_order(rows):
    totals = {}
    for row in rows:
        totals[row["homelessness_region"]] = row["total_adults"]
    return [region for region, _ in sorted(totals.items(), key=lambda item: item[1], reverse=True)]


def pivot(rows):
    data = {}
    for row in rows:
        region = row["homelessness_region"]
        data.setdefault(region, {})
        data[region][row["accommodation_type"]] = row
    return data


def validation_summary(rows):
    data = pivot(rows)
    summary = []
    for region in region_order(rows):
        entries = data[region].values()
        total_adults = next(iter(entries))["total_adults"]
        accommodation_adults = sum(row["adults"] for row in entries)
        difference = accommodation_adults - total_adults
        share_sum = round(sum(row["share_of_total_adults_pct"] for row in entries), 2)
        summary.append(
            {
                "homelessness_region": region,
                "total_adults": total_adults,
                "accommodation_adults": accommodation_adults,
                "difference": difference,
                "share_sum_pct": share_sum,
            }
        )
    return summary


def national_type_shares(rows):
    totals = {key: 0 for key in ACCOMMODATION_ORDER}
    total_adults = 0
    seen_regions = set()
    for row in rows:
        totals[row["accommodation_type"]] += row["adults"]
        region = row["homelessness_region"]
        if region not in seen_regions:
            total_adults += row["total_adults"]
            seen_regions.add(region)
    return {
        key: {
            "adults": value,
            "share": round(value / total_adults * 100, 1) if total_adults else 0,
        }
        for key, value in totals.items()
    }


def write_spec(rows):
    shares = national_type_shares(rows)
    validation = validation_summary(rows)
    largest_type = max(shares.items(), key=lambda item: item[1]["adults"])
    largest_region_private = max(
        (row for row in rows if row["accommodation_type"] == "Private Emergency Accommodation"),
        key=lambda row: row["share_of_total_adults_pct"],
    )
    strongest_difference = max(validation, key=lambda row: abs(row["difference"]))

    sample_rows = [
        [
            row["homelessness_region"],
            row["accommodation_type"],
            row["adults"],
            row["total_adults"],
            row["share_of_total_adults_pct"],
        ]
        for row in rows[:12]
    ]
    validation_rows = [
        [
            row["homelessness_region"],
            row["total_adults"],
            row["accommodation_adults"],
            row["difference"],
            row["share_sum_pct"],
        ]
        for row in validation
    ]

    spec = f"""# Task 20 - Accommodation Page Build Spec

## Page Intent

After this page, the user should understand how temporary accommodation types are distributed across homelessness regions, and where accommodation structure differs most.

## Data Source

Use SQL view:

```text
vw_accommodation_profile
```

Power BI-ready extract:

```text
Project/Power BI/accommodation_profile.csv
```

## Page Grain

One row per:

```text
homelessness_region + accommodation_type
```

Expected rows:

```text
36
```

## Required Fields

{md_table(["Field", "Use"], [
    ["`homelessness_region`", "Axis / slicer"],
    ["`accommodation_type`", "Legend/category"],
    ["`adults`", "Count"],
    ["`total_adults`", "Denominator"],
    ["`share_of_total_adults_pct`", "Composition percentage"],
])}

## KPI / Insight Cards

{md_table(["Card", "Expected Value"], [
    ["Largest accommodation type", largest_type[0]],
    ["Largest type share", f"{largest_type[1]['share']}%"],
    ["Highest private accommodation share", f"{largest_region_private['homelessness_region']} ({largest_region_private['share_of_total_adults_pct']}%)"],
    ["Largest accommodation-total difference", f"{strongest_difference['homelessness_region']} ({strongest_difference['difference']:+d})"],
])}

## Visual 1 - Accommodation Composition by Region

{md_table(["Setting", "Value"], [
    ["Visual type", "100% stacked bar chart"],
    ["Y-axis", "`homelessness_region`"],
    ["Legend", "`accommodation_type`"],
    ["Values", "`adults` or `share_of_total_adults_pct`"],
    ["Sort", "Descending by `total_adults`"],
    ["Title", "`Accommodation Composition by Region`"],
])}

## Visual 2 - Private Emergency Accommodation Share

{md_table(["Setting", "Value"], [
    ["Visual type", "Sorted bar chart"],
    ["Y-axis", "`homelessness_region`"],
    ["X-axis", "`share_of_total_adults_pct`"],
    ["Filter", "`accommodation_type = Private Emergency Accommodation`"],
    ["Sort", "Descending by share"],
    ["Title", "`Private Emergency Accommodation Share`"],
])}

## Visual 3 - Data Quality Check Table

Columns:

{md_table(["Column", "Display Name"], [
    ["`homelessness_region`", "Region"],
    ["`total_adults`", "Total Adults"],
    ["Calculated `SUM(adults)`", "Accommodation Adults"],
    ["Calculated difference", "Difference"],
    ["Calculated `SUM(share_of_total_adults_pct)`", "Share Sum %"],
])}

## Slicer

Optional:

```text
homelessness_region
```

## Data Note

Use this note:

```text
Accommodation categories are shown relative to total adults. Validation found category totals do not perfectly equal total adults in every region, especially Mid-West.
```

## Validation Summary

{md_table(["Region", "Total Adults", "Accommodation Adults", "Difference", "Share Sum %"], validation_rows)}

## Validation Sample

{md_table(["homelessness_region", "accommodation_type", "adults", "total_adults", "share_of_total_adults_pct"], sample_rows)}

## Acceptance Criteria

- CSV extract contains 36 rows.
- Page includes one composition visual and one focused private accommodation share visual.
- Data note is visible because accommodation totals have known validation differences.
- Mid-West difference is not hidden or corrected manually.
- Page does not replace the original validation finding; it carries the caveat into the report layer.
"""
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 22, y1 + 18), title, fill="#52616B", font=get_font(20))
    draw.text((x1 + 22, y1 + 58), value, fill="#17324D", font=get_font(32, bold=True))
    if subtitle:
        draw.text((x1 + 22, y1 + 96), subtitle, fill="#7A8A99", font=get_font(15))


def draw_legend(draw, x, y, items):
    pos_x = x
    for item in items:
        draw.rounded_rectangle((pos_x, y, pos_x + 18, y + 18), radius=4, fill=COLORS[item])
        draw.text((pos_x + 26, y - 1), item.replace(" Accommodation", ""), fill="#52616B", font=get_font(15))
        pos_x += 260


def draw_stacked_chart(draw, box, title, order, data):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), title, fill="#17324D", font=get_font(25, bold=True))
    draw_legend(draw, x1 + 24, y1 + 64, ACCOMMODATION_ORDER)

    label_x = x1 + 24
    bar_x = x1 + 190
    bar_width = x2 - bar_x - 40
    y = y1 + 112
    row_height = 34
    for region in order:
        draw.text((label_x, y + 2), region, fill="#2F3A44", font=get_font(17))
        total_share = sum(data[region].get(kind, {}).get("share_of_total_adults_pct", 0) for kind in ACCOMMODATION_ORDER)
        scale = max(total_share, 100)
        current_x = bar_x
        for kind in ACCOMMODATION_ORDER:
            value = data[region].get(kind, {}).get("share_of_total_adults_pct", 0)
            segment = round(bar_width * value / scale)
            if segment <= 0:
                continue
            draw.rectangle((current_x, y, current_x + segment, y + 22), fill=COLORS[kind])
            if segment > 55:
                draw.text((current_x + 5, y + 2), f"{round(value)}%", fill="#FFFFFF", font=get_font(14, bold=True))
            current_x += segment
        if total_share > 101:
            draw.text((bar_x + bar_width + 8, y + 1), f"{total_share:.0f}%", fill="#9A3412", font=get_font(14, bold=True))
        y += row_height


def draw_private_share_chart(draw, box, rows):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Private Emergency Accommodation Share", fill="#17324D", font=get_font(25, bold=True))
    private_rows = sorted(
        [row for row in rows if row["accommodation_type"] == "Private Emergency Accommodation"],
        key=lambda row: row["share_of_total_adults_pct"],
        reverse=True,
    )
    max_value = max(row["share_of_total_adults_pct"] for row in private_rows)
    label_x = x1 + 24
    bar_x = x1 + 190
    bar_width = x2 - bar_x - 95
    y = y1 + 72
    for row in private_rows:
        region = row["homelessness_region"]
        value = row["share_of_total_adults_pct"]
        width = round(bar_width * value / max_value)
        draw.text((label_x, y + 1), region, fill="#2F3A44", font=get_font(15))
        draw.rounded_rectangle((bar_x, y, bar_x + width, y + 22), radius=4, fill=COLORS["Private Emergency Accommodation"])
        draw.text((bar_x + width + 10, y), f"{value:.1f}%", fill="#17324D", font=get_font(15, bold=True))
        y += 22


def draw_quality_table(draw, box, validation):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Accommodation Total Check", fill="#17324D", font=get_font(25, bold=True))
    headers = ["Region", "Total", "Accommodation", "Diff"]
    xs = [x1 + 24, x1 + 220, x1 + 325, x1 + 490]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 65), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 92
    for row in validation:
        diff = row["difference"]
        color = "#9A3412" if abs(diff) > 5 else "#52616B"
        values = [
            row["homelessness_region"],
            f"{row['total_adults']:,}",
            f"{row['accommodation_adults']:,}",
            f"{diff:+d}",
        ]
        for x, value in zip(xs, values):
            draw.text((x, y), value, fill=color if value == values[-1] else "#2F3A44", font=get_font(15, bold=value == values[-1]))
        y += 22


def write_mockup(rows):
    width, height = 1600, 1100
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)

    order = region_order(rows)
    data = pivot(rows)
    shares = national_type_shares(rows)
    validation = validation_summary(rows)
    largest_type = max(shares.items(), key=lambda item: item[1]["adults"])
    highest_private = max(
        (row for row in rows if row["accommodation_type"] == "Private Emergency Accommodation"),
        key=lambda row: row["share_of_total_adults_pct"],
    )
    largest_difference = max(validation, key=lambda row: abs(row["difference"]))

    draw.text((60, 50), "Accommodation", fill="#17324D", font=get_font(42, bold=True))
    draw.text((62, 102), "Temporary accommodation profile by homelessness region", fill="#627386", font=get_font(23))

    draw_card(
        draw,
        (60, 146, 405, 270),
        "Largest Type",
        "Private",
        f"{largest_type[1]['share']}% of adults",
    )
    draw_card(
        draw,
        (435, 146, 780, 270),
        "Highest Private Share",
        highest_private["homelessness_region"],
        f"{highest_private['share_of_total_adults_pct']}% of total adults",
    )
    draw_card(
        draw,
        (810, 146, 1165, 270),
        "Known Validation Gap",
        largest_difference["homelessness_region"],
        f"Accommodation total {largest_difference['difference']:+d}",
    )
    draw_card(draw, (1195, 146, 1540, 270), "Total Adults", "11,944", "Across 9 regions")

    draw_stacked_chart(draw, (60, 320, 1540, 720), "Accommodation Composition by Region", order, data)
    draw_private_share_chart(draw, (60, 755, 790, 1015), rows)
    draw_quality_table(draw, (830, 755, 1540, 1015), validation)

    draw.rounded_rectangle((60, 1040, 1540, 1080), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1051),
        "Data note: Accommodation categories are shown relative to total adults; validation found category totals do not perfectly equal total adults in every region.",
        fill="#52616B",
        font=get_font(18),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    rows = fetch_rows()
    if len(rows) != 36:
        raise ValueError(f"Expected 36 accommodation rows, found {len(rows)}")
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
