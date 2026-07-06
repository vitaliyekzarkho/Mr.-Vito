# Task 8 - Data Standardisation Framework

## Purpose

Define the project standard once.

Apply it everywhere.

This framework will guide all future clean datasets:

- `clean_homelessness.csv`
- `clean_population.csv`
- `clean_rent.csv`
- `clean_housing.csv`
- `clean_unemployment.csv`

The goal is consistency before cleaning starts.

## 1. Table Naming Standard

Use lowercase `snake_case`.

| Dataset | Clean Table / File Name |
|---|---|
| Homelessness | `clean_homelessness.csv` |
| Population | `clean_population.csv` |
| Rent | `clean_rent.csv` |
| Housing | `clean_housing.csv` |
| Unemployment | `clean_unemployment.csv` |
| Geography Bridge | `dim_geography_bridge.xlsx` |

## 2. Column Naming Standard

Use lowercase `snake_case`.

Rules:

- no spaces
- no special characters
- no brackets
- no `%` symbols
- no `/`
- short but descriptive names
- units should be included only when needed

Examples:

| Raw Name | Standard Name |
|---|---|
| `Total Adults` | `total_adults` |
| `Male Adults` | `male_adults` |
| `Adults Aged 18-24` | `adults_18_24` |
| `Mean Sale Price` | `mean_sale_price` |
| `Price per sqm` | `price_per_sqm` |
| `NUTS 2 Region` | `nuts2_region` |
| `VALUE` | dataset-specific name, e.g. `population`, `unemployment_rate` |

## 3. Geography Naming Standard

Geography fields should use consistent names across all datasets.

| Concept | Standard Column |
|---|---|
| Homelessness region | `homelessness_region` |
| County | `county` |
| NUTS3 region | `nuts3_region` |
| NUTS2 region | `nuts2_region` |

Geography value rules:

- use title case for region and county names
- remove prefixes like `Co.` from county names
- use `Dublin`, not `Co. Dublin`
- use `Eastern and Midland`, `Southern`, `Northern and Western` for NUTS2
- preserve hyphenated homelessness regions such as `Mid-East`, `Mid-West`, `North-East`, `North-West`, `South-East`, `South-West`

## 4. Time Naming Standard

| Concept | Standard Column |
|---|---|
| Year | `year` |
| Half-year label | `half_year` |
| Half-year number | `half` |
| Date | descriptive date field, e.g. `date_of_sale` |

Rules:

- `year` must be a whole number
- `half` must be `1` or `2`
- `half_year` should follow the format `YYYYH1` or `YYYYH2`
- dates should be stored as date values where possible, or ISO-style text `YYYY-MM-DD` when exported to CSV

## 5. Data Type Standard

| Data Type | Use For | Examples |
|---|---|---|
| Integer | Counts and years | `year`, `total_adults`, `population`, `dwellings_built` |
| Decimal | Rates, prices, rents, ratios | `rent_euro`, `mean_sale_price`, `price_per_sqm`, `unemployment_rate` |
| Text | Categories and geography | `county`, `homelessness_region`, `nuts2_region` |
| Date | Transaction dates | `date_of_sale` |
| Boolean | True / false fields only if retained | `is_dublin`, `is_city` |

Missing values:

- use blank / null values
- do not use `"N/A"`, `"Unknown"`, `"-"`, or `"."` as placeholders in clean numeric fields
- if a value is unknown but analytically important, document it rather than inventing a value

## 6. Measure Naming Standard

Use clear business-friendly names in reports and Power BI.

Use lowercase `snake_case` in SQL or clean data files.

| Measure Concept | Technical Name | Report Label |
|---|---|---|
| Total homeless adults | `total_adults` | Homeless Adults |
| Homelessness rate | `homeless_rate_per_10000` | Homeless Adults per 10,000 |
| Average rent | `avg_rent_euro` | Average Rent |
| Population | `population` | Population |
| House price | `mean_sale_price` | Mean Sale Price |
| Price-to-income ratio | `price_to_income_ratio` | Price-to-Income Ratio |
| Housing supply rate | `dwellings_per_10000` | Dwellings Built per 10,000 |
| Unemployment rate | `unemployment_rate` | Unemployment Rate |

## 7. Target Schema - clean_homelessness.csv

| Column | Type | Notes |
|---|---|---|
| `homelessness_region` | Text | Standard region name |
| `total_adults` | Integer | Main outcome measure |
| `male_adults` | Integer | Gender count |
| `female_adults` | Integer | Gender count |
| `adults_18_24` | Integer | Age group |
| `adults_25_44` | Integer | Age group |
| `adults_45_64` | Integer | Age group |
| `adults_65_plus` | Integer | Age group |
| `private_emergency_accommodation` | Integer | Accommodation type |
| `supported_temporary_accommodation` | Integer | Accommodation type |
| `temporary_emergency_accommodation` | Integer | Accommodation type |
| `other_accommodation` | Integer | Accommodation type |
| `citizenship_irish` | Integer | Citizenship group |
| `citizenship_eea_uk` | Integer | Citizenship group |
| `citizenship_non_eea` | Integer | Citizenship group |
| `number_of_families` | Integer | Family metric |
| `adults_in_families` | Integer | Family metric |
| `single_parent_families` | Integer | Family metric |
| `dependants_in_families` | Integer | Family metric |

## 8. Target Schema - clean_population.csv

| Column | Type | Notes |
|---|---|---|
| `year` | Integer | Census year |
| `county` | Text | County without `Co.` prefix |
| `population` | Integer | Use rows where unit is Number |
| `population_share_pct` | Decimal | Optional; use rows where unit is `%` |

## 9. Target Schema - clean_rent.csv

| Column | Type | Notes |
|---|---|---|
| `year` | Integer | Year |
| `half` | Integer | 1 or 2 |
| `half_year` | Text | `YYYYH1` / `YYYYH2` |
| `county` | Text | County |
| `province` | Text | Province |
| `property_type` | Text | Property category |
| `bedrooms` | Text | Bedroom category |
| `bedrooms_num` | Integer | Blank for all-bedroom aggregate rows |
| `rent_euro` | Decimal | Rent value |
| `is_county_aggregate` | Boolean | Retain if useful for filtering |

## 10. Target Schema - clean_housing.csv

| Column | Type | Notes |
|---|---|---|
| `year` | Integer | Year |
| `county` | Text | County |
| `mean_sale_price` | Decimal | Housing price |
| `median_annual_earnings` | Decimal | Income context |
| `total_dwellings_built` | Integer | Supply count |
| `estimated_total_floor_area_sqm` | Decimal | Floor area |
| `weighted_avg_dwelling_size_sqm` | Decimal | Average size |
| `price_per_sqm` | Decimal | Price ratio |

## 11. Target Schema - clean_unemployment.csv

| Column | Type | Notes |
|---|---|---|
| `year` | Integer | Year |
| `age_group` | Text | Age category |
| `sex` | Text | Sex category |
| `education_attainment_level` | Text | Education category |
| `nuts2_region` | Text | Region |
| `unemployment_rate` | Decimal | Rename from `VALUE` |

## 12. Standardisation Rules Before Export

Before each clean file is exported:

1. Rename columns to `snake_case`.
2. Standardise geography values.
3. Convert numeric fields to numeric types.
4. Convert date/year fields consistently.
5. Keep only analytically useful columns.
6. Do not overwrite raw data.
7. Save outputs to `Project/Clean Data`.
8. Record assumptions or caveats in `Project/Documentation`.

## 13. Phase 2 Artifact Rule

Every document should lead to a build artifact.

| Document | Build Artifact |
|---|---|
| Geography Bridge Design | `dim_geography_bridge.xlsx` |
| Data Standardisation Framework | `clean_*.csv` files |
| Analysis Blueprint | SQL views and Power BI measures |
| Data Model Design | Power BI relationships |

## Final Decision

All future clean datasets will use:

- lowercase `snake_case` table and column names
- standard geography fields
- consistent numeric and date types
- project-ready file names
- no changes to raw data

This standard should be applied before creating `clean_homelessness.csv`.
