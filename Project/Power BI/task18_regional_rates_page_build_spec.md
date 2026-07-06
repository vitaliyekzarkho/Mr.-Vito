# Task 18 - Regional Rates Page Build Spec

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
| Highest Regional Rate | Dublin - 57.26 |
| Lowest Regional Rate | North-West - 5.91 |

## Insight Card

Suggested dynamic text:

```text
Dublin's rate is approximately 9.7x higher than North-West in the analysed dataset.
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
Dublin's rate is approximately 9.7x higher than North-West in the analysed dataset.
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

| rate_rank | absolute_rank | rank_change_after_normalisation | homelessness_region | homeless_adults | population | homeless_adults_per_10000 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 0 | Dublin | 8349 | 1458154 | 57.26 |
| 2 | 3 | 1 | Mid-West | 730 | 505369 | 14.44 |
| 3 | 2 | -1 | South-West | 897 | 740614 | 12.11 |
| 4 | 4 | 0 | Mid-East | 636 | 624451 | 10.18 |
| 5 | 5 | 0 | West | 420 | 485966 | 8.64 |
| 6 | 6 | 0 | South-East | 356 | 457410 | 7.78 |
| 7 | 7 | 0 | Midlands | 223 | 317999 | 7.01 |
| 8 | 8 | 0 | North-East | 172 | 286695 | 6.0 |
| 9 | 9 | 0 | North-West | 161 | 272481 | 5.91 |

## Acceptance Criteria

| Check | Expected |
|---|---|
| Page answers ranking-normalisation question | Yes |
| Regional rows | 9 |
| Highest rate | Dublin |
| Lowest rate | North-West |
| Bar chart sorted by rate | Yes |
| Ranking table sorted by rate rank | Yes |
| Data note visible | Yes |
