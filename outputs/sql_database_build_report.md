# Task 14 - SQL Database Build Report

## Database

SQLite database created at: `C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report\Project\SQL\ireland_homelessness.db`

## Row Count Checks

| Table | Expected Rows | Actual Rows | Result |
|---|---:|---:|---|
| `clean_homelessness` | 9 | 9 | Pass |
| `clean_population` | 26 | 26 | Pass |
| `clean_rent` | 286 | 286 | Pass |
| `clean_housing` | 390 | 390 | Pass |
| `clean_unemployment` | 1296 | 1296 | Pass |
| `dim_geography_bridge` | 26 | 26 | Pass |

## Duplicate Key Checks

| Table | Duplicate Key Groups | Result |
|---|---:|---|
| `clean_homelessness` | 0 | Pass |
| `clean_population` | 0 | Pass |
| `clean_rent` | 0 | Pass |
| `clean_housing` | 0 | Pass |
| `clean_unemployment` | 0 | Pass |
| `dim_geography_bridge` | 0 | Pass |

## Join Coverage Checks

| Check | Result Value | Interpretation |
|---|---:|---|
| Homelessness joined to bridge rows | 26 | Expected 26 because bridge grain is `homelessness_region + county` |
| Homelessness regions missing bridge | 0 | Expected 0 |
| Bridge counties missing population | 0 | Expected 0 |
| Bridge counties missing rent | 0 | Expected 0 |
| Bridge counties missing housing | 0 | Expected 0 |
| Bridge NUTS2 regions missing unemployment | 0 | Expected 0 |

## Grain Notes

- 9 homelessness regions expand to 26 rows after bridge join because bridge grain is homelessness_region + county.
- Population, rent, and housing should join through county. Rent and housing also include time grain.
- Unemployment joins through nuts2_region + year and is not county-level.

## Task 14 Conclusion

The SQL database build is structurally valid. All six tables loaded with expected row counts, duplicate key checks passed, and geography coverage checks passed.

Important: the homelessness-to-bridge join expands from 9 rows to 26 rows. This is expected and correct because the bridge translates each homelessness region into one or more counties. Analysis queries must aggregate carefully after this join.
