# Task 20 - Accommodation Page Build Spec

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

| Field | Use |
| --- | --- |
| `homelessness_region` | Axis / slicer |
| `accommodation_type` | Legend/category |
| `adults` | Count |
| `total_adults` | Denominator |
| `share_of_total_adults_pct` | Composition percentage |

## KPI / Insight Cards

| Card | Expected Value |
| --- | --- |
| Largest accommodation type | Private Emergency Accommodation |
| Largest type share | 71.5% |
| Highest private accommodation share | West (83.1%) |
| Largest accommodation-total difference | Mid-West (+98) |

## Visual 1 - Accommodation Composition by Region

| Setting | Value |
| --- | --- |
| Visual type | 100% stacked bar chart |
| Y-axis | `homelessness_region` |
| Legend | `accommodation_type` |
| Values | `adults` or `share_of_total_adults_pct` |
| Sort | Descending by `total_adults` |
| Title | `Accommodation Composition by Region` |

## Visual 2 - Private Emergency Accommodation Share

| Setting | Value |
| --- | --- |
| Visual type | Sorted bar chart |
| Y-axis | `homelessness_region` |
| X-axis | `share_of_total_adults_pct` |
| Filter | `accommodation_type = Private Emergency Accommodation` |
| Sort | Descending by share |
| Title | `Private Emergency Accommodation Share` |

## Visual 3 - Data Quality Check Table

Columns:

| Column | Display Name |
| --- | --- |
| `homelessness_region` | Region |
| `total_adults` | Total Adults |
| Calculated `SUM(adults)` | Accommodation Adults |
| Calculated difference | Difference |
| Calculated `SUM(share_of_total_adults_pct)` | Share Sum % |

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

| Region | Total Adults | Accommodation Adults | Difference | Share Sum % |
| --- | --- | --- | --- | --- |
| Dublin | 8349 | 8349 | 0 | 100.0 |
| South-West | 897 | 903 | 6 | 100.67 |
| Mid-West | 730 | 828 | 98 | 113.43 |
| Mid-East | 636 | 637 | 1 | 100.16 |
| West | 420 | 420 | 0 | 100.01 |
| South-East | 356 | 357 | 1 | 100.28 |
| Midlands | 223 | 224 | 1 | 100.44 |
| North-East | 172 | 173 | 1 | 100.58 |
| North-West | 161 | 161 | 0 | 100.0 |

## Validation Sample

| homelessness_region | accommodation_type | adults | total_adults | share_of_total_adults_pct |
| --- | --- | --- | --- | --- |
| Dublin | Private Emergency Accommodation | 6114 | 8349 | 73.23 |
| Dublin | Supported Temporary Accommodation | 2200 | 8349 | 26.35 |
| Dublin | Temporary Emergency Accommodation | 35 | 8349 | 0.42 |
| Dublin | Other Accommodation | 0 | 8349 | 0.0 |
| Mid-East | Private Emergency Accommodation | 467 | 636 | 73.43 |
| Mid-East | Supported Temporary Accommodation | 169 | 636 | 26.57 |
| Mid-East | Temporary Emergency Accommodation | 1 | 636 | 0.16 |
| Mid-East | Other Accommodation | 0 | 636 | 0.0 |
| Mid-West | Private Emergency Accommodation | 415 | 730 | 56.85 |
| Mid-West | Supported Temporary Accommodation | 383 | 730 | 52.47 |
| Mid-West | Temporary Emergency Accommodation | 30 | 730 | 4.11 |
| Mid-West | Other Accommodation | 0 | 730 | 0.0 |

## Acceptance Criteria

- CSV extract contains 36 rows.
- Page includes one composition visual and one focused private accommodation share visual.
- Data note is visible because accommodation totals have known validation differences.
- Mid-West difference is not hidden or corrected manually.
- Page does not replace the original validation finding; it carries the caveat into the report layer.
