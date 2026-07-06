# Task 19 - Demographics Page Build Spec

## Page Intent

After this page, the user should understand which age and gender groups make up the adult homeless population, and how this profile differs between regions.

## Data Source

Use SQL view:

```text
vw_demographic_profile
```

Power BI-ready extract:

```text
Project/Power BI/demographic_profile.csv
```

## Page Grain

One row per:

```text
homelessness_region + profile_type + category
```

Expected rows:

```text
54
```

## Required Fields

| Field | Use |
|---|---|
| `homelessness_region` | Axis / slicer |
| `profile_type` | Split gender vs age |
| `category` | Legend/category |
| `adults` | Count |
| `total_adults` | Denominator |
| `share_pct` | 100% composition |

## KPI / Insight Cards

| Card | Expected Value |
|---|---:|
| Male share | 59.5% |
| Female share | 40.5% |
| Largest age group | 25-44 |
| Largest age group share | 52.37% |

## Visual 1 - Gender Composition

| Setting | Value |
|---|---|
| Visual type | 100% stacked bar chart |
| Y-axis | `homelessness_region` |
| Legend | `category` filtered to Male/Female |
| Values | `adults` or `share_pct` |
| Sort | Descending by `total_adults` or same order as Overview |
| Title | `Gender Composition by Region` |

## Visual 2 - Age Composition

| Setting | Value |
|---|---|
| Visual type | 100% stacked bar chart |
| Y-axis | `homelessness_region` |
| Legend | `category` filtered to age groups |
| Values | `adults` or `share_pct` |
| Sort | Descending by `total_adults` or same order as Overview |
| Title | `Age Composition by Region` |

## Visual 3 - Optional Detail Table

Columns:

| Column | Display Name |
|---|---|
| `homelessness_region` | Region |
| `profile_type` | Profile |
| `category` | Category |
| `adults` | Adults |
| `share_pct` | Share % |

## Slicer

Optional:

```text
homelessness_region
```

## Data Note

Use this note:

```text
Percentages show composition, not scale. Use alongside total adult counts from Overview.
```

## Validation Sample

| homelessness_region | profile_type | category | adults | total_adults | share_pct |
| --- | --- | --- | --- | --- | --- |
| Dublin | age | 18-24 | 1535 | 8349 | 18.39 |
| Dublin | age | 25-44 | 4393 | 8349 | 52.62 |
| Dublin | age | 45-64 | 2275 | 8349 | 27.25 |
| Dublin | age | 65+ | 146 | 8349 | 1.75 |
| South-West | age | 18-24 | 121 | 897 | 13.49 |
| South-West | age | 25-44 | 499 | 897 | 55.63 |
| South-West | age | 45-64 | 253 | 897 | 28.21 |
| South-West | age | 65+ | 24 | 897 | 2.68 |
| Mid-West | age | 18-24 | 125 | 730 | 17.12 |
| Mid-West | age | 25-44 | 389 | 730 | 53.29 |
| Mid-West | age | 45-64 | 204 | 730 | 27.95 |
| Mid-West | age | 65+ | 12 | 730 | 1.64 |

## Acceptance Criteria

| Check | Expected |
|---|---|
| Page answers demographics question | Yes |
| Rows in dataset | 54 |
| Gender categories | Male, Female |
| Age categories | 18-24, 25-44, 45-64, 65+ |
| Data note visible | Yes |
| Composition not confused with scale | Yes |
