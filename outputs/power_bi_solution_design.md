# Task 16 - Power BI Solution Design

## Purpose

Design the Power BI solution before building visuals.

The goal is to keep Power BI clean:

- SQL prepares the analytical datasets.
- Power BI models relationships and interactivity.
- DAX handles report-level measures, formatting, and selected-context calculations.
- Visuals communicate the analysis from the SQL layer.

This is not a dashboard build yet. It is the implementation design.

## Data Source

Primary source:

```text
Project/SQL/ireland_homelessness.db
```

Power BI should connect to the SQLite database through an ODBC connector or by importing exported SQL view outputs if direct SQLite connection is unavailable.

Preferred import mode:

```text
Import
```

Reason: the dataset is small, stable, and portfolio-friendly.

## SQL Views To Import

Import analytical views first, not raw clean tables.

| SQL View | Power BI Table Name | Purpose |
|---|---|---|
| `vw_homelessness_rate_per_10000` | `homelessness_rate` | Main regional outcome table |
| `vw_demographic_profile` | `demographic_profile` | Age and gender composition |
| `vw_accommodation_profile` | `accommodation_profile` | Accommodation type composition |
| `vw_rent_pressure` | `rent_pressure` | Rent context by region and half-year |
| `vw_housing_affordability` | `housing_affordability` | House prices, supply, affordability |
| `vw_unemployment_context` | `unemployment_context` | NUTS2 unemployment context |

Optional supporting tables:

| Table | Use |
|---|---|
| `dim_geography_bridge` | Use only if a geography drill-through or county mapping page is needed |
| `clean_population` | Use only if extra population detail is needed |

## Model Design

The Power BI model should be view-led.

Recommended central table:

```text
homelessness_rate
```

This table has one row per `homelessness_region` and contains:

- homeless adults
- population
- homeless adults per 10,000 population

## Relationships

Use simple one-to-many relationships from `homelessness_rate` to the analytical views where possible.

| From | To | Relationship | Cross-filter Direction |
|---|---|---|---|
| `homelessness_rate[homelessness_region]` | `demographic_profile[homelessness_region]` | One-to-many | Single |
| `homelessness_rate[homelessness_region]` | `accommodation_profile[homelessness_region]` | One-to-many | Single |
| `homelessness_rate[homelessness_region]` | `rent_pressure[homelessness_region]` | One-to-many | Single |
| `homelessness_rate[homelessness_region]` | `housing_affordability[homelessness_region]` | One-to-many | Single |
| `homelessness_rate[homelessness_region]` | `unemployment_context[homelessness_region]` | One-to-many | Single |

Avoid many-to-many relationships.

Avoid bidirectional filtering unless a specific visual requires it and the behaviour is tested.

## Date / Time Handling

Current datasets do not share one clean common date grain:

- homelessness is current / region-level
- population is 2022
- rent is half-year
- housing is yearly
- unemployment is yearly

Do not create a universal Date table yet unless it becomes necessary.

Instead:

| Table | Time Field |
|---|---|
| `rent_pressure` | `half_year`, `year`, `half` |
| `housing_affordability` | `year` |
| `unemployment_context` | `year` |
| `homelessness_rate` | `population_year` |

If a Date table is added later, it should be added only after deciding how to align homelessness data with time-based context.

## SQL vs DAX Responsibilities

### Keep In SQL

These calculations should stay in SQL views:

| Calculation | Reason |
|---|---|
| Homeless adults per 10,000 population | Core analytical measure, already validated |
| County-to-region population aggregation | Grain-sensitive logic |
| Population-weighted rent | Requires bridge + population weighting |
| Population-weighted housing price | Requires bridge + population weighting |
| Price-to-income ratio | Derived from housing view |
| Dwellings built per 10,000 population | Derived from housing + population |
| North-East unemployment caution logic | Geography modelling caveat |

### Use DAX For

Use DAX for report-level measures:

| DAX Measure | Purpose |
|---|---|
| `Selected Homeless Rate` | Display selected-region rate |
| `Selected Homeless Adults` | Card visual |
| `Average Rent` | Visual aggregation from `rent_pressure` |
| `Average House Price` | Visual aggregation from `housing_affordability` |
| `Average Unemployment Rate` | Visual aggregation with filter context |
| `Region Rank` | Ranking regions in visuals |
| `Tooltip Text` | Dynamic notes and caveats |

## Suggested DAX Measures

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
AVERAGE(homelessness_rate[homeless_adults_per_10000])
```

```DAX
Average Rent =
AVERAGE(rent_pressure[population_weighted_avg_rent_euro])
```

```DAX
Average House Price =
AVERAGE(housing_affordability[population_weighted_mean_sale_price])
```

```DAX
Price-to-Income Ratio =
AVERAGE(housing_affordability[price_to_income_ratio])
```

```DAX
Unemployment Rate =
AVERAGE(unemployment_context[unemployment_rate])
```

## Global Slicers

Use slicers that make sense across report pages.

| Slicer | Source Table | Applies To |
|---|---|---|
| Homelessness Region | `homelessness_rate` | All pages |
| Rent Half-Year | `rent_pressure` | Rent page |
| Housing Year | `housing_affordability` | Housing page |
| Unemployment Year | `unemployment_context` | Economic context page |
| Demographic Profile Type | `demographic_profile` | Demographics page |

Do not force one universal year slicer yet, because the time grains do not fully align.

## Page Navigation

Recommended report pages:

| Page | Purpose |
|---|---|
| 1. Overview | Overall homelessness count and rate by region |
| 2. Regional Rates | Ranking and comparison of homeless adults per 10,000 |
| 3. Demographics | Age and gender composition |
| 4. Accommodation | Accommodation type profile |
| 5. Rent Pressure | Rent level vs homelessness rate |
| 6. Housing Affordability | House prices, supply, affordability |
| 7. Economic Context | Unemployment context and caveats |
| 8. Data Notes | Data quality, bridge logic, and limitations |

Navigation design:

- Use page buttons or tabs at the top.
- Keep page order aligned with the analytical story.
- Use a consistent region slicer where possible.
- Include a Data Notes page so caveats do not clutter every visual.

## Page-Level Design

### 1. Overview

Primary visuals:

- KPI card: Homeless Adults
- KPI card: Homeless Adults per 10,000
- Bar chart: Homeless Adults by Region
- Bar chart: Homeless Adults per 10,000 by Region

Main table:

```text
homelessness_rate
```

### 2. Regional Rates

Primary visuals:

- Sorted bar chart by `homeless_adults_per_10000`
- Table with region, population, homeless adults, rate

Purpose:

Show how rankings change when normalising by population.

### 3. Demographics

Primary visuals:

- 100% stacked bar: gender share by region
- 100% stacked bar: age share by region
- clustered bar: absolute age counts

Main table:

```text
demographic_profile
```

### 4. Accommodation

Primary visuals:

- stacked bar: accommodation adults by type and region
- heatmap: region vs accommodation type

Main table:

```text
accommodation_profile
```

Caveat:

Task 3 found accommodation totals do not fully match total adults, so this page should include a small data note.

### 5. Rent Pressure

Primary visuals:

- scatter plot: population-weighted rent vs homeless adults per 10,000
- line chart: rent over half-year by selected region
- table: region, half-year, rent, homelessness rate

Main table:

```text
rent_pressure
```

Default filter:

Use latest available `half_year`, currently `2025H1`, unless the user selects another period.

### 6. Housing Affordability

Primary visuals:

- scatter plot: price-to-income ratio vs homeless adults per 10,000
- bar chart: dwellings built per 10,000 by region
- line chart: weighted mean sale price by year

Main table:

```text
housing_affordability
```

Caveat:

`price_to_income_ratio` is unavailable where earnings are missing, including 2024.

### 7. Economic Context

Primary visuals:

- scatter plot: unemployment rate vs homeless adults per 10,000
- table with unemployment join note
- highlighted note for North-East

Main table:

```text
unemployment_context
```

Caveat:

North-East crosses NUTS2 boundaries, so unemployment context must be interpreted with caution.

### 8. Data Notes

Content:

- data source summary
- validation findings
- geography bridge explanation
- accommodation discrepancy
- unemployment missing values
- North-East NUTS2 caveat
- time-grain limitations

This page supports transparency and portfolio credibility.

## Visual Style Guidance

Use a restrained analytical style:

- clean white or very light background
- consistent region colors
- no heavy decorative visuals
- avoid 3D charts
- use clear chart titles
- use data labels only where helpful
- keep caveats visible but not overwhelming

Recommended color logic:

| Meaning | Visual Treatment |
|---|---|
| Homelessness outcome | Strong primary color |
| Context variables | Neutral secondary colors |
| Warnings / caveats | Amber or muted red |
| Notes | Light grey panels |

## Implementation Order

1. Connect to SQLite database or imported view outputs.
2. Import the six SQL views.
3. Rename Power BI tables to clean report names.
4. Create relationships from `homelessness_rate`.
5. Add core DAX measures.
6. Build Overview page first.
7. Build one page per analytical theme.
8. Add Data Notes page.
9. Test slicers and cross-filtering.
10. Review all visuals against the Analysis Blueprint.

## Quality Checks Before Final Dashboard

| Check | Expected Result |
|---|---|
| `homelessness_rate` rows | 9 |
| Region slicer values | 9 |
| Demographics rows | 54 |
| Accommodation rows | 36 |
| Rent pressure rows | 99 |
| Housing affordability rows | 135 |
| Unemployment context rows | 60 |
| North-East unemployment caveat visible | Yes |
| 2024 price-to-income blank handled | Yes |
| No accidental many-to-many relationships | Yes |

## Final Design Decision

Power BI should be a presentation and interaction layer.

The analytical logic should remain mostly in SQL views.

This keeps the final report easier to explain, easier to debug, and more credible as an end-to-end analytics project.
