# Task 17 - Power BI Overview Page Build Spec

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
| Homeless Adults | 11,944 |
| Population | 5,149,139 |
| Homeless Adults per 10,000 | 23.2 |
| Highest region by rate | Dublin |
| Highest regional rate | 57.26 |

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
| Expected value | `11,944` |

## Visual 2 - KPI Card: Homeless Adults per 10,000

| Setting | Value |
|---|---|
| Visual type | Card |
| Field | `Homeless Adults per 10,000` |
| Format | Decimal, 2 places |
| Title | `Per 10,000 Population` |
| Expected value | `23.2` |

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

| homelessness_region | population_year | homeless_adults | population | homeless_adults_per_10000 |
| --- | --- | --- | --- | --- |
| Dublin | 2022 | 8349 | 1458154 | 57.26 |
| Mid-West | 2022 | 730 | 505369 | 14.44 |
| South-West | 2022 | 897 | 740614 | 12.11 |
| Mid-East | 2022 | 636 | 624451 | 10.18 |
| West | 2022 | 420 | 485966 | 8.64 |
| South-East | 2022 | 356 | 457410 | 7.78 |
| Midlands | 2022 | 223 | 317999 | 7.01 |
| North-East | 2022 | 172 | 286695 | 6.0 |
| North-West | 2022 | 161 | 272481 | 5.91 |

## Acceptance Criteria

| Check | Expected |
|---|---|
| Region rows visible | 9 |
| KPI homeless adults | 11,944 |
| KPI rate | 23.2 |
| Highest rate region | Dublin |
| Bar charts sorted descending | Yes |
| Data note visible | Yes |

## Build Status

Ready to build in Power BI.
