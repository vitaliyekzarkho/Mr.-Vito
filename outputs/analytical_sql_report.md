# Task 15 - Analytical SQL Report

## Views Created

| View | Row Count | Grain |
|---|---:|---|
| `vw_homelessness_rate_per_10000` | 9 | `homelessness_region` |
| `vw_demographic_profile` | 54 | `homelessness_region + profile_type + category` |
| `vw_accommodation_profile` | 36 | `homelessness_region + accommodation_type` |
| `vw_rent_pressure` | 99 | `homelessness_region + half_year` |
| `vw_housing_affordability` | 135 | `homelessness_region + year` |
| `vw_unemployment_context` | 60 | `homelessness_region + nuts2_region + year` |

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
| View row count | 9 |
| Duplicate homelessness regions | 0 |
| Missing or invalid population | 0 |
| Missing calculated rate | 0 |
| Homelessness-to-bridge expansion rows | 26 |
| Demographic duplicate keys | 0 |
| Accommodation duplicate keys | 0 |
| Rent pressure duplicate keys | 0 |
| Housing affordability duplicate keys | 0 |
| North-East unemployment context rows | 12 |
| Mixed NUTS2 unemployment rows | 12 |

Interpretation: the source join expands from 9 homelessness regions to 26 bridge rows, then the view aggregates population back to 9 homelessness regions.

## View Output

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

## Rent Pressure Sample - 2025H1

| homelessness_region | half_year | population_weighted_avg_rent_euro | homeless_adults_per_10000 |
| --- | --- | --- | --- |
| Dublin | 2025H1 | 2147.3 | 57.26 |
| Mid-West | 2025H1 | 1279.93 | 14.44 |
| South-West | 2025H1 | 1428.38 | 12.11 |
| Mid-East | 2025H1 | 1636.7 | 10.18 |
| West | 2025H1 | 1383.75 | 8.64 |
| South-East | 2025H1 | 1186.58 | 7.78 |
| Midlands | 2025H1 | 1202.02 | 7.01 |
| North-East | 2025H1 | 1233.92 | 6.0 |
| North-West | 2025H1 | 1013.58 | 5.91 |

## Housing Affordability Sample - 2024

| homelessness_region | year | population_weighted_mean_sale_price | population_weighted_median_annual_earnings | price_to_income_ratio | dwellings_built_per_10000 | homeless_adults_per_10000 |
| --- | --- | --- | --- | --- | --- | --- |
| Dublin | 2024 | 579098.5 |  |  | 74.9 | 57.26 |
| Mid-West | 2024 | 319810.88 |  |  | 41.93 | 14.44 |
| South-West | 2024 | 375005.65 |  |  | 54.4 | 12.11 |
| Mid-East | 2024 | 428877.35 |  |  | 69.71 | 10.18 |
| West | 2024 | 346259.09 |  |  | 41.53 | 8.64 |
| South-East | 2024 | 318765.27 |  |  | 56.65 | 7.78 |
| Midlands | 2024 | 298570.41 |  |  | 52.17 | 7.01 |
| North-East | 2024 | 296600.7 |  |  | 58.32 | 6.0 |
| North-West | 2024 | 269581.87 |  |  | 35.23 | 5.91 |

## SQL Script

Stored at:

`C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report\Project\SQL\15_create_analytical_views.sql`
