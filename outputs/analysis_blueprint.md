# Task 6 - Analysis Blueprint

## Purpose

This document moves the project from data engineering into data analysis.

The goal is not to write SQL yet.

The goal is to decide:

- what questions the project should answer
- which datasets are needed for each question
- which fields are required
- which calculations must be created
- which visualisations will communicate the answer best
- what type of insight we expect to produce

## Analytical Focus

The project is about homelessness in Ireland and the possible social, housing, and economic factors connected to it.

The analysis should not only show where homelessness is highest.

It should also explain:

- whether homelessness is high relative to population
- whether rent pressure may be connected to homelessness
- whether housing prices and housing supply may be connected to homelessness
- whether labour market conditions may help explain regional differences
- which demographic groups are most affected

## Business Question 1 - Where is homelessness highest relative to population?

| Item | Design |
|---|---|
| Business Question | Which regions have the highest homelessness rate after adjusting for population size? |
| Tables Needed | Homelessness, Population, Geography Bridge |
| Fields Needed | `homelessness_region`, `county`, `Total Adults`, `Population` |
| Calculation | `Homeless adults per 10,000 population = Total Adults / Population * 10,000` |
| Aggregation | Sum county population to homelessness region |
| Best Visualisation | Bar chart sorted descending |
| Secondary Visualisation | Map, if geography file becomes available |
| Expected Type of Insight | A ranked comparison of regions that controls for population size |
| Interpretation Caution | Raw homelessness counts and population-adjusted rates may tell different stories |

## Business Question 2 - What is the demographic structure of homelessness?

| Item | Design |
|---|---|
| Business Question | Which age and gender groups make up the homeless adult population? |
| Tables Needed | Homelessness |
| Fields Needed | `Region`, `Male Adults`, `Female Adults`, `Adults Aged 18-24`, `Adults Aged 25-44`, `Adults Aged 45-64`, `Adults Aged 65+` |
| Calculation | Share of total adults by gender and age group |
| Aggregation | Region-level only |
| Best Visualisation | 100% stacked bar chart |
| Secondary Visualisation | Clustered bar chart for absolute counts |
| Expected Type of Insight | Composition of homelessness by age and gender across regions |
| Interpretation Caution | Percentages show structure, not scale; pair with total counts |

## Business Question 3 - What accommodation types are most used?

| Item | Design |
|---|---|
| Business Question | What types of emergency or temporary accommodation are most common by region? |
| Tables Needed | Homelessness |
| Fields Needed | Private Emergency Accommodation, Supported Temporary Accommodation, Temporary Emergency Accommodation, Other Accommodation, `Total Adults` |
| Calculation | Accommodation type share of total adults |
| Aggregation | Region-level only |
| Best Visualisation | Stacked bar chart |
| Secondary Visualisation | Heatmap by region and accommodation type |
| Expected Type of Insight | Regional differences in service/accommodation profile |
| Interpretation Caution | Task 3 found accommodation totals do not fully match total adults, so this analysis needs a data quality note |

## Business Question 4 - Is rent pressure associated with homelessness?

| Item | Design |
|---|---|
| Business Question | Do regions with higher rent levels also show higher homelessness rates? |
| Tables Needed | Homelessness, Rent, Population, Geography Bridge |
| Fields Needed | `homelessness_region`, `county`, `year`, `rent_euro`, `Total Adults`, `Population` |
| Calculation | Homeless adults per 10,000 population; average or weighted average rent by homelessness region |
| Aggregation | County rent aggregated to homelessness region |
| Preferred Measure | Weighted average rent, ideally population-weighted |
| Fallback Measure | Simple average rent by counties in region |
| Best Visualisation | Scatter plot: rent vs homelessness rate |
| Secondary Visualisation | Dual-axis line chart if time is introduced |
| Expected Type of Insight | Whether higher rent regions tend to have higher homelessness rates |
| Interpretation Caution | Correlation is not causation; rent data has county-year grain while homelessness is currently region-level |

## Business Question 5 - Is housing affordability related to homelessness?

| Item | Design |
|---|---|
| Business Question | Are higher house prices associated with higher homelessness rates? |
| Tables Needed | Homelessness, Housing, Population, Geography Bridge |
| Fields Needed | `Mean Sale Price`, `Price per sqm`, `Median Annual Earnings`, `Total Adults`, `Population`, `County`, `Year` |
| Calculation | Homeless adults per 10,000 population; price-to-income ratio; regional average house price |
| Aggregation | County-year housing metrics aggregated to homelessness region |
| Preferred Measure | Price-to-income ratio |
| Fallback Measure | Mean sale price or price per sqm |
| Best Visualisation | Scatter plot |
| Secondary Visualisation | Bubble chart, with population or homelessness count as bubble size |
| Expected Type of Insight | Whether unaffordability appears stronger in regions with higher homelessness pressure |
| Interpretation Caution | Housing price data and homelessness data may not represent the same time period unless year alignment is handled |

## Business Question 6 - Is housing supply related to homelessness?

| Item | Design |
|---|---|
| Business Question | Do regions with lower housing supply show higher homelessness rates? |
| Tables Needed | Homelessness, Housing, Population, Geography Bridge |
| Fields Needed | `Total Dwellings Built`, `County`, `Year`, `Total Adults`, `Population` |
| Calculation | Dwellings built per 10,000 population; homeless adults per 10,000 population |
| Aggregation | Sum dwellings built by homelessness region |
| Best Visualisation | Scatter plot |
| Secondary Visualisation | Bar chart comparing supply rate and homelessness rate |
| Expected Type of Insight | Whether low housing supply appears connected with homelessness pressure |
| Interpretation Caution | Supply effects may lag; current-year comparison may be too simplistic |

## Business Question 7 - Is unemployment associated with homelessness?

| Item | Design |
|---|---|
| Business Question | Do regions with higher unemployment also show higher homelessness rates? |
| Tables Needed | Homelessness, Unemployment, Population, Geography Bridge |
| Fields Needed | `NUTS2 Region`, `Year`, `VALUE` unemployment rate, `Total Adults`, `Population` |
| Calculation | Homeless adults per 10,000 population; unemployment rate |
| Aggregation | NUTS2 unemployment assigned to homelessness regions only where safe |
| Best Visualisation | Scatter plot |
| Secondary Visualisation | Small multiples by NUTS2 region |
| Expected Type of Insight | Whether labour market stress aligns with homelessness pressure |
| Interpretation Caution | North-East crosses NUTS2 boundaries, so direct unemployment comparison is unsafe unless weighted |

## Business Question 8 - Which citizenship groups are most represented?

| Item | Design |
|---|---|
| Business Question | What is the citizenship composition of homeless adults by region? |
| Tables Needed | Homelessness |
| Fields Needed | Irish, EEA / UK, Non-EEA, `Total Adults`, `Region` |
| Calculation | Citizenship group share of total adults |
| Aggregation | Region-level only |
| Best Visualisation | 100% stacked bar chart |
| Secondary Visualisation | Treemap for national composition |
| Expected Type of Insight | Regional variation in citizenship composition |
| Interpretation Caution | This should be descriptive only; avoid causal interpretation without additional context |

## Core Measures To Create

| Measure | Formula | Purpose |
|---|---|---|
| Homeless Adults | `Total Adults` | Main outcome |
| Homeless Rate per 10,000 | `Total Adults / Population * 10,000` | Population-adjusted comparison |
| Male Share | `Male Adults / Total Adults` | Gender composition |
| Female Share | `Female Adults / Total Adults` | Gender composition |
| Age Group Share | `Age Group Count / Total Adults` | Age composition |
| Accommodation Share | `Accommodation Type Count / Total Adults` | Accommodation profile |
| Citizenship Share | `Citizenship Group Count / Total Adults` | Citizenship profile |
| Average Rent | Average or weighted average of `rent_euro` | Rent pressure |
| Price-to-Income Ratio | `Mean Sale Price / Median Annual Earnings` | Housing affordability |
| Dwellings per 10,000 | `Total Dwellings Built / Population * 10,000` | Housing supply pressure |
| Unemployment Rate | `VALUE` from unemployment dataset | Labour market context |

## Visualisation Plan

| Analytical Need | Best Visual |
|---|---|
| Rank regions | Sorted bar chart |
| Compare composition | 100% stacked bar |
| Compare absolute subgroup counts | Clustered bar |
| Explore relationship between two measures | Scatter plot |
| Show geographic differences | Map, if spatial layer is added |
| Show matrix of regions vs categories | Heatmap |
| Show national composition | Treemap |
| Show trend over time | Line chart |

## Power BI Page Structure

| Page | Purpose |
|---|---|
| Overview | National and regional homelessness summary |
| Regional Rates | Homelessness per 10,000 population |
| Demographics | Age, gender, and citizenship composition |
| Accommodation | Accommodation type profile |
| Housing Pressure | Rent, prices, affordability, and supply |
| Economic Context | Unemployment and regional context |
| Data Notes | Validation issues, modelling caveats, and geography bridge notes |

## Analysis Readiness

| Area | Status |
|---|---|
| Homelessness outcome defined | Ready |
| Population normalisation defined | Ready |
| Geography bridge concept defined | Ready |
| Rent analysis approach | Ready, but aggregation choice needed |
| Housing affordability approach | Ready, but year alignment needed |
| Housing supply approach | Ready, but lag logic may be needed |
| Unemployment approach | Partially ready; North-East needs special handling |
| SQL implementation | Not yet; should follow this blueprint |

## Final Direction

The next stage should not be SQL-first.

The next stage should be analysis-first:

1. Confirm the business questions.
2. Confirm the required measures.
3. Confirm aggregation rules.
4. Confirm visualisation plan.
5. Only then implement the model in SQL / Power BI.

This keeps the project analytical rather than purely technical.
