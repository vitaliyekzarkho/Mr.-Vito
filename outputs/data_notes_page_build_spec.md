# Task 24 - Data Notes Page Build Spec

## Page Intent

After this page, the user should understand the main data limitations, grain differences, geography assumptions and interpretation rules behind the report.

## Data Source

Power BI-ready extract:

```text
Project/Power BI/data_notes.csv
```

This page is explanatory. It does not introduce a new analytical measure.

## Required Fields

| Field | Use |
| --- | --- |
| `area` | Limitation category |
| `note` | What the user needs to know |
| `impact` | How it affects interpretation |
| `severity` | Visual priority |

## Visual 1 - Key Data Notes

| Setting | Value |
| --- | --- |
| Visual type | Table or multi-row card |
| Columns | `area`, `severity`, `note`, `impact` |
| Sort | High severity first |
| Title | `Key Data Notes` |

## Visual 2 - Dataset Grain Summary

| Dataset | Grain | Rows |
| --- | --- | --- |
| Homelessness | homelessness_region | 9 |
| Population | county | 26 |
| Bridge | homelessness_region + county | 26 |
| Rent Pressure | homelessness_region + half_year | 99 |
| Housing Affordability | homelessness_region + year | 135 |
| Economic Context | region + nuts2 + year | 60 |

## Visual 3 - Interpretation Rules

Use three short rule cards:

| Rule | Meaning |
| --- | --- |
| Compare rates, not only counts | Regional population size changes interpretation. |
| Association, not causation | Rent, housing and unemployment explain context, not proof. |
| Respect geography grain | County, homelessness region and NUTS2 joins have different precision. |

## Data Notes Catalogue

| Area | Severity | Note | Impact |
| --- | --- | --- | --- |
| Geography | Medium | Homelessness data is reported by homelessness region; population, rent and housing data are county-based and are aggregated via the geography bridge. | Regional comparisons depend on the bridge assumptions. |
| Accommodation | High | Accommodation category totals do not perfectly equal total adults in every region; Mid-West has the largest gap. | Accommodation page shows category shares relative to total adults and keeps the validation caveat visible. |
| Rent | High | Rent is a half-year time series, while homelessness is a regional snapshot repeated across rent periods. | Rent pressure visuals show association only, not a time-aligned causal analysis. |
| Housing | High | 2024 housing prices and supply are available, but 2024 earnings are unavailable. | Price-to-income ratio defaults to 2023, the latest complete affordability year. |
| Unemployment | Medium | Unemployment is NUTS2-level, not county or homelessness-region level. | Economic context should be read as broad regional context. |
| North-East | High | North-East spans two NUTS2 regions: Eastern and Midland, and Northern and Western. | North-East unemployment context is mixed geography and should not be collapsed silently. |
| Causality | High | Rent, housing affordability and unemployment pages show observed association, not causation. | Interpretations should use careful wording and avoid claims that one metric causes homelessness. |
| Population | Low | Homelessness rates use 2022 county population aggregated to homelessness regions. | Rates are suitable for regional comparison but depend on the chosen population year. |

## Acceptance Criteria

- `data_notes.csv` contains 8 rows.
- Page includes geography, accommodation, rent, housing, unemployment and causality limitations.
- Page clearly says association is not causation.
- Page explains why North-East is special for unemployment.
- Page gives the user confidence that limitations were handled intentionally, not discovered accidentally.
