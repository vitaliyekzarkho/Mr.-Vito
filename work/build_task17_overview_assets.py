import csv
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "overview_homelessness_rate.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "overview_homelessness_rate.csv"
SPEC_PATH = POWER_BI_DIR / "task17_overview_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task17_overview_page_build_spec.md"


def fetch_overview_rows():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT
            homelessness_region,
            population_year,
            homeless_adults,
            population,
            homeless_adults_per_10000
        FROM vw_homelessness_rate_per_10000
        ORDER BY homeless_adults_per_10000 DESC
        """
    ).fetchall()
    con.close()
    return [dict(row) for row in rows]


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
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
    total_homeless = sum(int(row["homeless_adults"]) for row in rows)
    total_population = sum(int(row["population"]) for row in rows)
    national_rate = round((total_homeless / total_population) * 10000, 2)
    top_region = rows[0]["homelessness_region"]
    top_rate = rows[0]["homeless_adults_per_10000"]

    report = f"""# Task 17 - Power BI Overview Page Build Spec

## Goal

Build the first Power BI report page only:

```text
Overview
```

This page introduces the project with:

- KPI card: Homeless Adults
- KPI card: Homeless Adults per 10,000 Population
- Bar chart: Homeless Adults by Region
- Bar chart: Homeless Adults per 10,000 by Region

## Data Source

Use SQL view:

```text
vw_homelessness_rate_per_10000
```

Power BI-ready CSV extract:

```text
Project/Power BI/overview_homelessness_rate.csv
```

Preferred source remains the SQLite view. The CSV is provided as a fallback/import-friendly extract.

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
| `homelessness_region` | Axis / slicer |
| `population_year` | Data note |
| `homeless_adults` | KPI and bar chart |
| `population` | denominator for rate |
| `homeless_adults_per_10000` | KPI and bar chart |

## DAX Measures

Create these measures in Power BI:

```DAX
Homeless Adults =
SUM(homelessness_rate[homeless_adults])
```

```DAX
Population =
SUM(homelessness_rate[population])
```

```DAX
Homeless Adults per 10,000 =
DIVIDE([Homeless Adults], [Population]) * 10000
```

```DAX
Selected Region Count =
DISTINCTCOUNT(homelessness_rate[homelessness_region])
```

## Expected KPI Values

| KPI | Expected Value |
|---|---:|
| Homeless Adults | {total_homeless:,} |
| Population | {total_population:,} |
| Homeless Adults per 10,000 | {national_rate} |
| Highest region by rate | {top_region} |
| Highest regional rate | {top_rate} |

## Page Layout

Recommended canvas:

```text
16:9 landscape
```

Layout:

| Area | Visual |
|---|---|
| Top left | Page title: `Homelessness in Ireland - Overview` |
| Top row, card 1 | KPI: Homeless Adults |
| Top row, card 2 | KPI: Homeless Adults per 10,000 |
| Middle left | Bar chart: Homeless Adults by Region |
| Middle right | Bar chart: Homeless Adults per 10,000 by Region |
| Bottom | Small data note |

## Visual 1 - KPI Card: Homeless Adults

| Setting | Value |
|---|---|
| Visual type | Card |
| Field | `Homeless Adults` |
| Format | Whole number, comma separator |
| Title | `Homeless Adults` |
| Expected value | `{total_homeless:,}` |

## Visual 2 - KPI Card: Homeless Adults per 10,000

| Setting | Value |
|---|---|
| Visual type | Card |
| Field | `Homeless Adults per 10,000` |
| Format | Decimal, 2 places |
| Title | `Per 10,000 Population` |
| Expected value | `{national_rate}` |

## Visual 3 - Bar Chart: Homeless Adults by Region

| Setting | Value |
|---|---|
| Visual type | Clustered bar chart |
| Y-axis | `homelessness_region` |
| X-axis | `Homeless Adults` |
| Sort | Descending by `Homeless Adults` |
| Data labels | On |
| Title | `Homeless Adults by Region` |

## Visual 4 - Bar Chart: Homeless Adults per 10,000 by Region

| Setting | Value |
|---|---|
| Visual type | Clustered bar chart |
| Y-axis | `homelessness_region` |
| X-axis | `homeless_adults_per_10000` or DAX measure |
| Sort | Descending by rate |
| Data labels | On |
| Title | `Homeless Adults per 10,000 Population` |

## Data Note

Use this note on the page:

```text
Population denominator uses 2022 county population aggregated to homelessness regions through the geography bridge.
```

## Validation Table

{md_table(["homelessness_region", "population_year", "homeless_adults", "population", "homeless_adults_per_10000"], rows)}

## Acceptance Criteria

| Check | Expected |
|---|---|
| Region rows visible | 9 |
| KPI homeless adults | {total_homeless:,} |
| KPI rate | {national_rate} |
| Highest rate region | Dublin |
| Bar charts sorted descending | Yes |
| Data note visible | Yes |

## Build Status

Ready to build in Power BI.
"""

    SPEC_PATH.write_text(report, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(report, encoding="utf-8")


def main():
    rows = fetch_overview_rows()
    if len(rows) != 9:
        raise ValueError(f"Expected 9 overview rows, found {len(rows)}")
    write_csv(CSV_PATH, rows)
    write_csv(OUTPUT_CSV_PATH, rows)
    write_spec(rows)
    print(f"Created {CSV_PATH}")
    print(f"Created {OUTPUT_CSV_PATH}")
    print(f"Created {SPEC_PATH}")
    print(f"Created {OUTPUT_SPEC_PATH}")


if __name__ == "__main__":
    main()
