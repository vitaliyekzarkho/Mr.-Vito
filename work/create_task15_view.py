import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DB_PATH = PROJECT_ROOT / "Project" / "SQL" / "ireland_homelessness.db"
SQL_PATH = PROJECT_ROOT / "Project" / "SQL" / "15_create_analytical_views.sql"
REPORT_PATH = PROJECT_ROOT / "Project" / "SQL" / "task15_analytical_sql_report.md"
OUTPUT_REPORT_PATH = PROJECT_ROOT / "outputs" / "task15_analytical_sql_report.md"

VIEWS = [
    "vw_homelessness_rate_per_10000",
    "vw_demographic_profile",
    "vw_accommodation_profile",
    "vw_rent_pressure",
    "vw_housing_affordability",
    "vw_unemployment_context",
]


def rows_as_markdown(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join("" if value is None else str(value) for value in row) + " |")
    return "\n".join(lines)


def main():
    sql = SQL_PATH.read_text(encoding="utf-8")
    con = sqlite3.connect(DB_PATH)
    con.executescript(sql)
    con.commit()

    view_counts = {
        view: con.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
        for view in VIEWS
    }
    row_count = view_counts["vw_homelessness_rate_per_10000"]
    duplicate_regions = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT homelessness_region
            FROM vw_homelessness_rate_per_10000
            GROUP BY homelessness_region
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    missing_population = con.execute("""
        SELECT COUNT(*)
        FROM vw_homelessness_rate_per_10000
        WHERE population IS NULL OR population <= 0
    """).fetchone()[0]
    missing_rate = con.execute("""
        SELECT COUNT(*)
        FROM vw_homelessness_rate_per_10000
        WHERE homeless_adults_per_10000 IS NULL
    """).fetchone()[0]
    source_expansion = con.execute("""
        SELECT COUNT(*)
        FROM clean_homelessness h
        JOIN dim_geography_bridge b
          ON h.homelessness_region = b.homelessness_region
    """).fetchone()[0]

    demographic_duplicate_keys = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT homelessness_region, profile_type, category
            FROM vw_demographic_profile
            GROUP BY homelessness_region, profile_type, category
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    accommodation_duplicate_keys = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT homelessness_region, accommodation_type
            FROM vw_accommodation_profile
            GROUP BY homelessness_region, accommodation_type
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    rent_duplicate_keys = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT homelessness_region, half_year
            FROM vw_rent_pressure
            GROUP BY homelessness_region, half_year
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    housing_duplicate_keys = con.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT homelessness_region, year
            FROM vw_housing_affordability
            GROUP BY homelessness_region, year
            HAVING COUNT(*) > 1
        )
    """).fetchone()[0]
    unemployment_northeast_rows = con.execute("""
        SELECT COUNT(*)
        FROM vw_unemployment_context
        WHERE homelessness_region = 'North-East'
    """).fetchone()[0]
    unemployment_mixed_rows = con.execute("""
        SELECT COUNT(*)
        FROM vw_unemployment_context
        WHERE unemployment_join_note = 'Mixed NUTS2 region - interpret with caution'
    """).fetchone()[0]

    rows = con.execute("""
        SELECT
            homelessness_region,
            population_year,
            homeless_adults,
            population,
            homeless_adults_per_10000
        FROM vw_homelessness_rate_per_10000
        ORDER BY homeless_adults_per_10000 DESC
    """).fetchall()

    view_sample_rows = con.execute("""
        SELECT
            homelessness_region,
            half_year,
            population_weighted_avg_rent_euro,
            homeless_adults_per_10000
        FROM vw_rent_pressure
        WHERE half_year = '2025H1'
        ORDER BY homeless_adults_per_10000 DESC
    """).fetchall()

    housing_sample_rows = con.execute("""
        SELECT
            homelessness_region,
            year,
            population_weighted_mean_sale_price,
            population_weighted_median_annual_earnings,
            price_to_income_ratio,
            dwellings_built_per_10000,
            homeless_adults_per_10000
        FROM vw_housing_affordability
        WHERE year = 2024
        ORDER BY homeless_adults_per_10000 DESC
    """).fetchall()

    con.close()

    report = f"""# Task 15 - Analytical SQL Report

## Views Created

| View | Row Count | Grain |
|---|---:|---|
| `vw_homelessness_rate_per_10000` | {view_counts['vw_homelessness_rate_per_10000']} | `homelessness_region` |
| `vw_demographic_profile` | {view_counts['vw_demographic_profile']} | `homelessness_region + profile_type + category` |
| `vw_accommodation_profile` | {view_counts['vw_accommodation_profile']} | `homelessness_region + accommodation_type` |
| `vw_rent_pressure` | {view_counts['vw_rent_pressure']} | `homelessness_region + half_year` |
| `vw_housing_affordability` | {view_counts['vw_housing_affordability']} | `homelessness_region + year` |
| `vw_unemployment_context` | {view_counts['vw_unemployment_context']} | `homelessness_region + nuts2_region + year` |

## Purpose

Create the analytical SQL layer required by the Analysis Blueprint:

- homelessness rate per 10,000 population
- demographic profile
- accommodation profile
- rent pressure
- housing affordability and supply
- unemployment context

## Core Measure

`Homeless Adults per 10,000 Population`

The base view deliberately aggregates population from county level to homelessness region before joining to homelessness. This avoids leaving the final analytical output at county-expanded grain.

## Validation Checks

| Check | Result |
|---|---:|
| View row count | {row_count} |
| Duplicate homelessness regions | {duplicate_regions} |
| Missing or invalid population | {missing_population} |
| Missing calculated rate | {missing_rate} |
| Homelessness-to-bridge expansion rows | {source_expansion} |
| Demographic duplicate keys | {demographic_duplicate_keys} |
| Accommodation duplicate keys | {accommodation_duplicate_keys} |
| Rent pressure duplicate keys | {rent_duplicate_keys} |
| Housing affordability duplicate keys | {housing_duplicate_keys} |
| North-East unemployment context rows | {unemployment_northeast_rows} |
| Mixed NUTS2 unemployment rows | {unemployment_mixed_rows} |

Interpretation: the source join expands from 9 homelessness regions to 26 bridge rows, then the view aggregates population back to 9 homelessness regions.

## View Output

{rows_as_markdown(["homelessness_region", "population_year", "homeless_adults", "population", "homeless_adults_per_10000"], rows)}

## Rent Pressure Sample - 2025H1

{rows_as_markdown(["homelessness_region", "half_year", "population_weighted_avg_rent_euro", "homeless_adults_per_10000"], view_sample_rows)}

## Housing Affordability Sample - 2024

{rows_as_markdown(["homelessness_region", "year", "population_weighted_mean_sale_price", "population_weighted_median_annual_earnings", "price_to_income_ratio", "dwellings_built_per_10000", "homeless_adults_per_10000"], housing_sample_rows)}

## SQL Script

Stored at:

`{SQL_PATH}`
"""

    REPORT_PATH.write_text(report, encoding="utf-8")
    OUTPUT_REPORT_PATH.write_text(report, encoding="utf-8")

    print(report)


if __name__ == "__main__":
    main()
