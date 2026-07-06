# Task 21 - Rent Pressure Page Build Spec

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
2025H1
```

Homelessness rate is not time-series in this dataset; it is repeated across rent periods for comparison only.

## Required Fields

| Field | Use |
| --- | --- |
| `homelessness_region` | Point / axis / slicer |
| `half_year` | Period slicer |
| `population_weighted_avg_rent_euro` | Rent pressure measure |
| `homeless_adults_per_10000` | Homelessness rate |
| `county_count` | Coverage check |
| `population` | Weighting / tooltip |

## KPI / Insight Cards

| Card | Expected Value |
| --- | --- |
| Default rent period | 2025H1 |
| Pearson correlation | 0.885 |
| Highest rent region | Dublin (EUR 2,147) |
| Highest homelessness rate | Dublin (57.26) |
| National weighted rent growth | 35.9% from 2020H1 to 2025H1 |

## Visual 1 - Rent vs Homelessness Rate

| Setting | Value |
| --- | --- |
| Visual type | Scatter chart |
| X-axis | `population_weighted_avg_rent_euro` |
| Y-axis | `homeless_adults_per_10000` |
| Details | `homelessness_region` |
| Tooltip | `homeless_adults`, `population`, `county_count`, `half_year` |
| Default filter | `half_year = 2025H1` |
| Title | `Rent vs Homelessness Rate` |

## Visual 2 - Rent Trend

| Setting | Value |
| --- | --- |
| Visual type | Line chart |
| X-axis | `half_year` |
| Y-axis | `population_weighted_avg_rent_euro` |
| Legend | `homelessness_region` or national weighted trend |
| Title | `Rent Trend by Region` |

## Visual 3 - Regional Comparison Table

Columns:

| Column | Display Name |
| --- | --- |
| `homelessness_region` | Region |
| `population_weighted_avg_rent_euro` | Weighted Avg Rent |
| `homeless_adults_per_10000` | Rate per 10,000 |
| `homeless_adults` | Homeless Adults |
| `county_count` | Counties |

## Interpretation Guidance

Use neutral wording:

```text
In 2025H1, regions with higher weighted average rents show a positive association with homelessness rates in this dataset.
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

| Region | Half-Year | Weighted Avg Rent | Rate per 10,000 | County Count |
| --- | --- | --- | --- | --- |
| Dublin | 2025H1 | 2147.3 | 57.26 | 1 |
| Mid-East | 2025H1 | 1636.7 | 10.18 | 3 |
| South-West | 2025H1 | 1428.38 | 12.11 | 2 |
| West | 2025H1 | 1383.75 | 8.64 | 3 |
| Mid-West | 2025H1 | 1279.93 | 14.44 | 3 |
| North-East | 2025H1 | 1233.92 | 6.0 | 3 |
| Midlands | 2025H1 | 1202.02 | 7.01 | 4 |
| South-East | 2025H1 | 1186.58 | 7.78 | 4 |
| North-West | 2025H1 | 1013.58 | 5.91 | 3 |

## Acceptance Criteria

- `rent_pressure.csv` contains 99 rows.
- `rent_pressure_latest.csv` contains 9 rows.
- Scatter chart is filtered to one half-year by default.
- Page includes a visible caution that the relationship is associative, not causal.
- Dublin is visible as both highest rent and highest homelessness-rate region in the default period.
