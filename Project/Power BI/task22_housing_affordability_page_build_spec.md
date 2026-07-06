# Task 22 - Housing Affordability Page Build Spec

## Page Intent

After this page, the user should understand how housing prices, income, and new housing supply relate to homelessness rates across regions, while treating the comparison as contextual association rather than causation.

## Data Source

Use SQL view:

```text
vw_housing_affordability
```

Power BI-ready extracts:

```text
Project/Power BI/housing_affordability.csv
Project/Power BI/housing_affordability_latest_ratio.csv
```

## Page Grain

Main extract:

```text
homelessness_region + year
```

Latest complete affordability extract:

```text
homelessness_region
```

Expected rows:

```text
housing_affordability.csv = 135
housing_affordability_latest_ratio.csv = 9
```

## Analytical Scope

The default affordability year is:

```text
2023
```

The latest housing year is `2024`, but `price_to_income_ratio` is unavailable for that year because earnings are missing. Do not use `2024` as the default ratio year.

## Required Fields

| Field | Use |
| --- | --- |
| `homelessness_region` | Point / axis / slicer |
| `year` | Year slicer |
| `population_weighted_mean_sale_price` | Price measure |
| `population_weighted_median_annual_earnings` | Income measure |
| `price_to_income_ratio` | Affordability measure |
| `dwellings_built_per_10000` | Supply context |
| `homeless_adults_per_10000` | Homelessness rate |

## KPI / Insight Cards

| Card | Expected Value |
| --- | --- |
| Default affordability year | 2023 |
| Correlation: ratio vs rate | 0.913 |
| Highest price-to-income ratio | Dublin (11.76) |
| Highest supply per 10,000 | Mid-East (90.85) |
| Highest homelessness rate | Dublin (57.26) |
| National weighted sale price growth | 64.6% from 2010 to 2024 |

## Visual 1 - Affordability vs Homelessness Rate

| Setting | Value |
| --- | --- |
| Visual type | Scatter chart |
| X-axis | `price_to_income_ratio` |
| Y-axis | `homeless_adults_per_10000` |
| Details | `homelessness_region` |
| Tooltip | `population_weighted_mean_sale_price`, `population_weighted_median_annual_earnings`, `dwellings_built_per_10000` |
| Default filter | `year = 2023` |
| Title | `Affordability vs Homelessness Rate` |

## Visual 2 - Housing Supply Context

| Setting | Value |
| --- | --- |
| Visual type | Sorted bar chart |
| Y-axis | `homelessness_region` |
| X-axis | `dwellings_built_per_10000` |
| Default filter | `year = 2023` |
| Title | `Dwellings Built per 10,000 Population` |

## Visual 3 - Sale Price Trend

| Setting | Value |
| --- | --- |
| Visual type | Line chart |
| X-axis | `year` |
| Y-axis | `population_weighted_mean_sale_price` |
| Legend | `homelessness_region` or national weighted trend |
| Title | `Weighted Mean Sale Price Trend` |

## Data Note

Use this note:

```text
This page shows contextual association, not causation. Price-to-income ratio uses 2023 because 2024 earnings are unavailable in the clean housing dataset.
```

## Missing Value Summary

| Field | Missing rows |
| --- | --- |
| population_weighted_mean_sale_price | 0 |
| population_weighted_median_annual_earnings | 18 |
| price_to_income_ratio | 18 |
| total_dwellings_built | 18 |
| dwellings_built_per_10000 | 18 |
| population_weighted_price_per_sqm | 18 |

## Latest Complete Ratio Validation Sample

| Region | Year | Price-to-Income | Mean Sale Price | Median Earnings | Dwellings per 10,000 | Rate per 10,000 |
| --- | --- | --- | --- | --- | --- | --- |
| Dublin | 2023 | 11.76 | 562970.0 | 47873.0 | 86.31 | 57.26 |
| Mid-East | 2023 | 8.95 | 408485.12 | 45624.7 | 90.85 | 10.18 |
| South-West | 2023 | 8.19 | 350853.36 | 42827.6 | 50.15 | 12.11 |
| South-East | 2023 | 7.86 | 310389.89 | 39511.19 | 50.61 | 7.78 |
| West | 2023 | 7.72 | 316014.0 | 40917.02 | 41.75 | 8.64 |
| Mid-West | 2023 | 7.31 | 301674.61 | 41264.52 | 35.97 | 14.44 |
| North-East | 2023 | 7.25 | 280256.72 | 38659.98 | 55.08 | 6.0 |
| Midlands | 2023 | 6.88 | 279415.27 | 40638.17 | 60.28 | 7.01 |
| North-West | 2023 | 6.6 | 243797.88 | 36954.47 | 36.77 | 5.91 |

## Acceptance Criteria

- `housing_affordability.csv` contains 135 rows.
- `housing_affordability_latest_ratio.csv` contains 9 rows.
- Main affordability scatter defaults to 2023, not 2024.
- Page includes a visible note explaining missing 2024 earnings.
- Page avoids causal language and frames housing metrics as context.
