# Task 23 - Economic Context Page Build Spec

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
2024
```

Unemployment is available at NUTS2 level, not county or homelessness-region level. Do not interpret it as a precise local rate for every homelessness region.

## Required Fields

| Field | Use |
| --- | --- |
| `homelessness_region` | Region label / table |
| `nuts2_region` | Line chart legend / geography context |
| `year` | Year axis / slicer |
| `unemployment_rate` | Economic context measure |
| `county_count_in_nuts2` | Bridge coverage |
| `nuts2_count` | Direct vs mixed mapping check |
| `unemployment_join_note` | Interpretation caveat |
| `homeless_adults_per_10000` | Homelessness context |

## KPI / Insight Cards

| Card | Expected Value |
| --- | --- |
| Default year | 2024 |
| Highest NUTS2 unemployment | Eastern and Midland (4.6%) |
| Lowest NUTS2 unemployment | Northern and Western (4.2%) |
| Direct homelessness regions | 8 |
| Mixed NUTS2 regions | North-East |

## Visual 1 - NUTS2 Unemployment Trend

| Setting | Value |
| --- | --- |
| Visual type | Line chart |
| X-axis | `year` |
| Y-axis | `unemployment_rate` |
| Legend | `nuts2_region` |
| Title | `NUTS2 Unemployment Trend` |

## Visual 2 - Latest Unemployment Context

| Setting | Value |
| --- | --- |
| Visual type | Bar chart |
| Y-axis | `nuts2_region` |
| X-axis | `unemployment_rate` |
| Default filter | `year = 2024` |
| Title | `Latest NUTS2 Unemployment Rate` |

## Visual 3 - Geography Interpretation Table

Columns:

| Column | Display Name |
| --- | --- |
| `homelessness_region` | Homelessness Region |
| `nuts2_region` | NUTS2 Region |
| `county_count_in_nuts2` | Counties in NUTS2 |
| `nuts2_count` | NUTS2 Count |
| `unemployment_join_note` | Interpretation Note |

## Data Note

Use this note:

```text
Unemployment data is NUTS2-level. North-East spans two NUTS2 regions, so its unemployment context should be read as mixed geography rather than a single direct regional rate.
```

## Latest Validation Sample

| Region | NUTS2 | Year | Unemployment Rate | County Count | NUTS2 Count | Join Note |
| --- | --- | --- | --- | --- | --- | --- |
| Dublin | Eastern and Midland | 2024 | 4.6 | 1 | 1 | Direct NUTS2 join safe |
| Mid-East | Eastern and Midland | 2024 | 4.6 | 3 | 1 | Direct NUTS2 join safe |
| Mid-West | Southern | 2024 | 4.6 | 3 | 1 | Direct NUTS2 join safe |
| Midlands | Eastern and Midland | 2024 | 4.6 | 4 | 1 | Direct NUTS2 join safe |
| North-East | Eastern and Midland | 2024 | 4.6 | 1 | 2 | Mixed NUTS2 region - interpret with caution |
| North-East | Northern and Western | 2024 | 4.2 | 2 | 2 | Mixed NUTS2 region - interpret with caution |
| North-West | Northern and Western | 2024 | 4.2 | 3 | 1 | Direct NUTS2 join safe |
| South-East | Southern | 2024 | 4.6 | 4 | 1 | Direct NUTS2 join safe |
| South-West | Southern | 2024 | 4.6 | 2 | 1 | Direct NUTS2 join safe |
| West | Northern and Western | 2024 | 4.2 | 3 | 1 | Direct NUTS2 join safe |

## Acceptance Criteria

- `economic_context.csv` contains 60 rows.
- `economic_context_latest.csv` contains 10 rows.
- Page clearly states that unemployment is NUTS2-level.
- North-East mixed geography is visible and not collapsed silently.
- Page avoids causal wording between unemployment and homelessness.
