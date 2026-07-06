import csv
import math
from pathlib import Path

import pandas as pd

RAW_PATH = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data\housing_prices.xlsx")
PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
CLEAN_PATH = PROJECT_ROOT / "Project" / "Clean Data" / "clean_housing.csv"
OUTPUT_COPY_PATH = PROJECT_ROOT / "outputs" / "clean_housing.csv"

COLUMN_MAP = {
    "Year": "year",
    "County": "county",
    "Mean Sale Price": "mean_sale_price",
    "Median Annual Earnings": "median_annual_earnings",
    "Total Dwellings Built": "total_dwellings_built",
    "Estd. Total Floor Area (sqm)": "estimated_total_floor_area_sqm",
    "Weighted Avg Dwelling Size (sqm)": "weighted_avg_dwelling_size_sqm",
    "Price per sqm": "price_per_sqm",
}

OUTPUT_COLUMNS = list(COLUMN_MAP.values())
INTEGER_COLUMNS = {"year", "total_dwellings_built"}
DECIMAL_COLUMNS = {
    "mean_sale_price",
    "median_annual_earnings",
    "estimated_total_floor_area_sqm",
    "weighted_avg_dwelling_size_sqm",
    "price_per_sqm",
}


def is_blank(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip() == ""


def standardise_county(value) -> str:
    return " ".join(str(value).strip().split())


def to_int_or_blank(value, column: str):
    if is_blank(value):
        return ""
    number = float(value)
    if number % 1 != 0:
        raise ValueError(f"Non-integer value in {column}: {value}")
    return int(number)


def to_decimal_or_blank(value, column: str):
    if is_blank(value):
        return ""
    return round(float(value), 3)


def read_and_clean():
    df = pd.read_excel(RAW_PATH, sheet_name=0)
    missing = sorted(set(COLUMN_MAP) - set(df.columns))
    if missing:
        raise ValueError(f"Missing raw columns: {missing}")

    rows = []
    for _, raw in df.iterrows():
        cleaned = {}
        for raw_col, clean_col in COLUMN_MAP.items():
            value = raw[raw_col]
            if clean_col == "county":
                cleaned[clean_col] = standardise_county(value)
            elif clean_col in INTEGER_COLUMNS:
                cleaned[clean_col] = to_int_or_blank(value, clean_col)
            elif clean_col in DECIMAL_COLUMNS:
                cleaned[clean_col] = to_decimal_or_blank(value, clean_col)
            else:
                cleaned[clean_col] = value
        rows.append(cleaned)

    return rows


def validate(rows):
    if len(rows) != 390:
        raise ValueError(f"Expected 390 housing rows, found {len(rows)}")

    keys = [(row["year"], row["county"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate year + county keys found")

    counties = {row["county"] for row in rows}
    if len(counties) != 26:
        raise ValueError(f"Expected 26 counties, found {len(counties)}")

    years = {row["year"] for row in rows}
    if years != set(range(2010, 2025)):
        raise ValueError(f"Unexpected years: {sorted(years)}")

    for row in rows:
        if not isinstance(row["year"], int):
            raise TypeError(f"year must be int: {row['year']}")
        for column in INTEGER_COLUMNS - {"year"}:
            if row[column] != "" and not isinstance(row[column], int):
                raise TypeError(f"{column} must be int or blank: {row[column]}")
        for column in DECIMAL_COLUMNS:
            if row[column] != "" and not isinstance(row[column], float):
                raise TypeError(f"{column} must be decimal or blank: {row[column]}")
            if row[column] != "" and row[column] < 0:
                raise ValueError(f"{column} has negative value: {row[column]}")

    missing_counts = {column: sum(1 for row in rows if row[column] == "") for column in OUTPUT_COLUMNS}
    expected_missing = {
        "year": 0,
        "county": 0,
        "mean_sale_price": 0,
        "median_annual_earnings": 52,
        "total_dwellings_built": 52,
        "estimated_total_floor_area_sqm": 52,
        "weighted_avg_dwelling_size_sqm": 52,
        "price_per_sqm": 52,
    }
    if missing_counts != expected_missing:
        raise ValueError(f"Unexpected missing counts: {missing_counts}")


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def main():
    rows = read_and_clean()
    validate(rows)
    write_csv(CLEAN_PATH, rows)
    write_csv(OUTPUT_COPY_PATH, rows)
    print(f"Created {CLEAN_PATH}")
    print(f"Created {OUTPUT_COPY_PATH}")
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(OUTPUT_COLUMNS)}")
    print(f"Counties: {len({row['county'] for row in rows})}")
    print(f"Years: {min(row['year'] for row in rows)}-{max(row['year'] for row in rows)}")


if __name__ == "__main__":
    main()
