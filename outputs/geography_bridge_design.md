# Task 5 - Geography Bridge Design

## Goal

Design the geography bridge before SQL.

The bridge must answer:

- Which counties belong to each homelessness region?
- Which NUTS2 region does each county belong to?
- Can values be aggregated safely?
- Which joins are safe?

This is a design document only. It is not SQL and it is not the final bridge table creation step.

## Why This Bridge Is Needed

The datasets do not use the same geographic grain.

| Dataset | Geographic Grain |
|---|---|
| Homelessness | Homelessness Region |
| Population | County |
| Rent | County |
| Housing | County |
| Unemployment | NUTS2 Region |

Because the grains differ, direct joins are risky.

The geography bridge should become the translation layer between:

```text
Homelessness Region
    -> County
        -> NUTS3
            -> NUTS2
```

## Proposed Bridge Grain

The bridge should have one row per:

```text
Homelessness Region + County
```

This is the safest grain because:

- homelessness data starts at region level
- population, rent, and housing are county-level datasets
- unemployment is broader NUTS2-level data
- county is the middle layer that can connect both directions

## Conceptual Bridge Fields

| Column | Purpose |
|---|---|
| `homelessness_region` | Region name from homelessness dataset |
| `county` | County name used by county-level datasets |
| `nuts3_region` | NUTS3 / strategic planning region |
| `nuts2_region` | NUTS2 region |
| `notes` | Any geography caveat that affects interpretation |

The safety fields used below, such as whether aggregation is safe or whether NUTS2 matching is direct, are design notes. They do not necessarily need to become stored fields in the final data model.

## Proposed County Mapping

| Homelessness Region | Counties | NUTS2 Result | Can Aggregate County Data? | Direct NUTS2 Join Safe? |
|---|---|---|---|---|
| Dublin | Dublin | Eastern and Midland | Yes | Yes |
| Mid-East | Kildare, Meath, Wicklow | Eastern and Midland | Yes | Yes |
| Midlands | Laois, Longford, Offaly, Westmeath | Eastern and Midland | Yes | Yes |
| Mid-West | Clare, Limerick, Tipperary | Southern | Yes | Yes |
| North-East | Cavan, Louth, Monaghan | Mixed: Northern and Western + Eastern and Midland | Yes for county data; No for simple NUTS2 | No |
| North-West | Donegal, Leitrim, Sligo | Northern and Western | Yes | Yes |
| South-East | Carlow, Kilkenny, Waterford, Wexford | Southern | Yes | Yes |
| South-West | Cork, Kerry | Southern | Yes | Yes |
| West | Galway, Mayo, Roscommon | Northern and Western | Yes | Yes |

## Full Proposed Bridge Rows

| homelessness_region | county | nuts3_region | nuts2_region | notes |
|---|---|---|---|---|
| Dublin | Dublin | Dublin | Eastern and Midland | County-level Dublin is treated as one aggregate county unit |
| Mid-East | Kildare | Mid-East | Eastern and Midland | Homelessness Mid-East excludes Louth if Louth is assigned to North-East |
| Mid-East | Meath | Mid-East | Eastern and Midland | Homelessness Mid-East excludes Louth if Louth is assigned to North-East |
| Mid-East | Wicklow | Mid-East | Eastern and Midland | Homelessness Mid-East excludes Louth if Louth is assigned to North-East |
| Midlands | Laois | Midland | Eastern and Midland | Full NUTS3 match |
| Midlands | Longford | Midland | Eastern and Midland | Full NUTS3 match |
| Midlands | Offaly | Midland | Eastern and Midland | Full NUTS3 match |
| Midlands | Westmeath | Midland | Eastern and Midland | Full NUTS3 match |
| Mid-West | Clare | Mid-West | Southern | Full NUTS3 match |
| Mid-West | Limerick | Mid-West | Southern | Full NUTS3 match |
| Mid-West | Tipperary | Mid-West | Southern | Full NUTS3 match |
| North-East | Cavan | Border | Northern and Western | Region crosses NUTS2 boundary |
| North-East | Louth | Mid-East | Eastern and Midland | Region crosses NUTS2 boundary |
| North-East | Monaghan | Border | Northern and Western | Region crosses NUTS2 boundary |
| North-West | Donegal | Border | Northern and Western | Border NUTS3 is split across North-East and North-West |
| North-West | Leitrim | Border | Northern and Western | Border NUTS3 is split across North-East and North-West |
| North-West | Sligo | Border | Northern and Western | Border NUTS3 is split across North-East and North-West |
| South-East | Carlow | South-East | Southern | Full NUTS3 match |
| South-East | Kilkenny | South-East | Southern | Full NUTS3 match |
| South-East | Waterford | South-East | Southern | Full NUTS3 match |
| South-East | Wexford | South-East | Southern | Full NUTS3 match |
| South-West | Cork | South-West | Southern | Full NUTS3 match |
| South-West | Kerry | South-West | Southern | Full NUTS3 match |
| West | Galway | West | Northern and Western | Full NUTS3 match |
| West | Mayo | West | Northern and Western | Full NUTS3 match |
| West | Roscommon | West | Northern and Western | Full NUTS3 match |

## Aggregation Rules

### County-Level Datasets

Population, rent, and housing can be aggregated from county to homelessness region using the bridge.

Safe direction:

```text
County -> Homelessness Region
```

Unsafe direction:

```text
Homelessness Region -> County
```

Reason: homelessness values are already regional totals. They cannot be split into counties without an allocation rule.

## Safe Aggregation by Metric Type

| Metric Type | Example | Aggregation Rule |
|---|---|---|
| Count | Population, dwellings built | Sum |
| Price / rent level | Mean sale price, rent_euro | Weighted average preferred |
| Rate / percentage | Unemployment rate | Weighted average preferred |
| Ratio | Price per sqm | Weighted average or recompute from numerator / denominator |

## Join Safety Rules

### Safe Joins

| Join | Safe? | Reason |
|---|---|---|
| Homelessness -> Bridge on `homelessness_region` | Yes | Bridge grain is region-county |
| Bridge -> Population on `county` | Yes | Population is county-level |
| Bridge -> Rent on `county + year` | Yes | Rent is county-year |
| Bridge -> Housing on `county + year` | Yes | Housing is county-year |
| Bridge -> Unemployment on `nuts2_region + year` | Conditionally | Safe only when homelessness region belongs to one NUTS2 |

### Unsafe Joins

| Join | Safe? | Why Not |
|---|---|---|
| Homelessness directly to Population | No | Region and county grains do not match |
| Homelessness directly to Rent | No | Region vs county-year mismatch |
| Homelessness directly to Housing | No | Region vs county-year mismatch |
| Homelessness directly to Unemployment | No | Region vs NUTS2 mismatch |
| North-East homelessness directly to NUTS2 unemployment | No | North-East crosses NUTS2 boundaries |

## Special Risk: North-East

`North-East` is the major modelling risk.

If the homelessness North-East region includes:

```text
Cavan + Louth + Monaghan
```

then it crosses NUTS2 boundaries:

| County | NUTS2 |
|---|---|
| Cavan | Northern and Western |
| Monaghan | Northern and Western |
| Louth | Eastern and Midland |

This means a single unemployment rate cannot be joined directly to North-East homelessness without a modelling decision.

## Recommended Rule for Unemployment

For unemployment, use this hierarchy:

1. If a homelessness region maps to exactly one NUTS2 region, join directly through the bridge.
2. If a homelessness region maps to multiple NUTS2 regions, do not direct join.
3. For mixed regions, create a weighted unemployment estimate only if a valid weight is chosen.

Possible weights:

| Weight | Use Case |
|---|---|
| County population | Best general option |
| Labour force population | Best unemployment-specific option, if available |
| Equal county weight | Simple but weak; use only as fallback |

## Future Implementation Guidance

The implementation should not start with joins between raw datasets.

It should start with geography normalization:

```text
geography bridge
```

Conceptual grain:

```text
one row per homelessness_region + county
```

Conceptual relationship pattern:

```text
homelessness_fact
    -> geography bridge
        -> county-level dimensions
        -> nuts2-level dimensions
```

## Final Design Decision

Use the bridge table as the only approved route between homelessness regions and external context datasets.

Do not allow direct joins from homelessness to county-level or NUTS2-level tables.

This protects the project from:

- duplicate rows
- incorrect totals
- false correlations
- hidden many-to-many joins
- incorrect unemployment assignment for mixed regions

## Source Notes

The NUTS2/NUTS3 mapping follows the Irish NUTS statistical region structure, where Ireland has three NUTS2 regions and eight NUTS3 regions. The 2018 NUTS structure places Louth in the Mid-East NUTS3 region under Eastern and Midland, while Cavan and Monaghan are in the Border NUTS3 region under Northern and Western.

Reference used for NUTS mapping:

- https://en.wikipedia.org/wiki/NUTS_statistical_regions_of_Ireland
