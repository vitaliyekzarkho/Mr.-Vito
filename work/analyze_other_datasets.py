import json
import math
import re
from pathlib import Path

import pandas as pd

BASE = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data")
OUT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report\work\other_datasets_validation.json")

DATASETS = {
    "Unemployment": {
        "path": BASE / "unemployment.csv.csv",
        "type": "csv",
        "critical": ["Year", "Age Group", "Sex", "Education Attainment Level", "NUTS 2 Region", "VALUE"],
        "numeric": ["Year", "VALUE"],
        "integer": ["Year"],
        "key": ["Year", "Age Group", "Sex", "Education Attainment Level", "NUTS 2 Region"],
        "text": ["Age Group", "Sex", "Education Attainment Level", "NUTS 2 Region", "UNIT"],
    },
    "Housing Prices": {
        "path": BASE / "housing_prices.xlsx",
        "type": "xlsx",
        "critical": ["Year", "County", "Mean Sale Price"],
        "numeric": [
            "Year",
            "Mean Sale Price",
            "Median Annual Earnings",
            "Total Dwellings Built",
            "Estd. Total Floor Area (sqm)",
            "Weighted Avg Dwelling Size (sqm)",
            "Price per sqm",
        ],
        "integer": ["Year", "Total Dwellings Built"],
        "key": ["Year", "County"],
        "text": ["County"],
    },
    "Housing Supply / Sales": {
        "path": BASE / "housing_supply.xlsx.csv",
        "type": "csv",
        "critical": ["Date of Sale", "Address", "County", "Price"],
        "numeric": ["Price", "Not Full Market Price", "VAT Exclusive"],
        "integer": ["Not Full Market Price", "VAT Exclusive"],
        "key": ["Date of Sale", "Address", "County", "Price"],
        "text": ["Postal Code", "County", "Description of Property", "Property Size Description"],
    },
    "Population by County": {
        "path": BASE / "population_by_county.csv.csv",
        "type": "csv",
        "critical": ["Year", "County", "VALUE"],
        "numeric": ["Year", "VALUE"],
        "integer": ["Year"],
        "key": ["Year", "County", "UNIT"],
        "text": ["County", "UNIT"],
    },
    "Rent by County": {
        "path": BASE / "rent_by_county.csv.csv",
        "type": "csv",
        "critical": ["rent_euro", "year", "half", "half_year", "county"],
        "numeric": ["rent_euro", "year", "half", "time_period", "bedrooms_num"],
        "integer": ["year", "half", "time_period", "bedrooms_num"],
        "key": ["year", "half_year", "county", "property_type", "bedrooms"],
        "text": ["county", "province", "area", "location", "property_type", "bedrooms", "is_dublin", "is_city", "is_county_aggregate"],
    },
}


def read_dataset(config):
    if config["type"] == "xlsx":
        return pd.read_excel(config["path"], sheet_name=0)
    return pd.read_csv(config["path"], dtype=str, keep_default_na=False)


def is_blank(value):
    if pd.isna(value):
        return True
    return str(value).strip() == ""


def normalize_text(value):
    return re.sub(r"\s+", " ", str(value).strip().lower())


def number_series(df, column):
    if column not in df.columns:
        return pd.Series([math.nan] * len(df))
    return pd.to_numeric(df[column].replace("", pd.NA), errors="coerce")


def sample_rows(df, mask, columns, limit=10):
    if not mask.any():
        return []
    cols = [c for c in columns if c in df.columns]
    out = df.loc[mask, cols].head(limit).copy()
    return out.astype(object).where(pd.notnull(out), "").to_dict(orient="records")


def text_variant_issues(df, columns):
    issues = []
    for col in columns:
        if col not in df.columns:
            continue
        variants = {}
        for val in df[col].dropna().astype(str):
            if val.strip() == "":
                continue
            variants.setdefault(normalize_text(val), set()).add(val)
        for norm, vals in variants.items():
            if len(vals) > 1:
                issues.append({"Column": col, "Normalized": norm, "Variants": " | ".join(sorted(vals))})
    return issues[:25]


def summarize_dataset(name, config):
    df = read_dataset(config)
    rows, cols = df.shape
    all_missing = int(df.map(is_blank).to_numpy().sum())

    critical_cols = [c for c in config["critical"] if c in df.columns]
    critical_missing = int(df[critical_cols].map(is_blank).to_numpy().sum()) if critical_cols else 0

    numeric_issues = []
    negative_count = 0
    non_integer_count = 0
    non_numeric_count = 0
    for col in config["numeric"]:
        if col not in df.columns:
            continue
        raw = df[col]
        blank = raw.apply(is_blank)
        nums = pd.to_numeric(raw.replace("", pd.NA), errors="coerce")
        bad_numeric = (~blank) & nums.isna()
        bad_negative = nums < 0
        non_numeric_count += int(bad_numeric.sum())
        negative_count += int(bad_negative.sum())
        if int(bad_numeric.sum()):
            numeric_issues.extend(sample_rows(df, bad_numeric, config["key"] + [col], 5))
        if col in config["integer"]:
            nonint = nums.notna() & ((nums % 1).abs() > 1e-9)
            non_integer_count += int(nonint.sum())
        if name == "Population by County" and col == "VALUE" and "UNIT" in df.columns:
            nonint = (df["UNIT"].astype(str).str.strip() == "Number") & nums.notna() & ((nums % 1).abs() > 1e-9)
            non_integer_count += int(nonint.sum())

    key_cols = [c for c in config["key"] if c in df.columns]
    duplicate_count = int(df.duplicated(subset=key_cols, keep=False).sum()) if key_cols else 0
    duplicate_samples = sample_rows(df, df.duplicated(subset=key_cols, keep=False), key_cols, 10) if key_cols else []

    text_issues = text_variant_issues(df, config["text"])

    date_issues = []
    if "Date of Sale" in df.columns:
        dates = pd.to_datetime(df["Date of Sale"], format="%d/%m/%y", errors="coerce")
        mask = dates.isna()
        date_issues = sample_rows(df, mask, ["Date of Sale", "Address", "County", "Price"], 10)
    if "half_year" in df.columns:
        hy_mask = ~df["half_year"].astype(str).str.match(r"^\d{4}H[12]$")
        date_issues.extend(sample_rows(df, hy_mask, ["year", "half", "half_year", "county"], 10))

    range_issues = []
    if name == "Unemployment":
        value = number_series(df, "VALUE")
        mask = (value < 0) | (value > 100)
        range_issues = sample_rows(df, mask, config["key"] + ["VALUE"], 10)
    if name == "Housing Supply / Sales":
        price = number_series(df, "Price")
        flag_mask = pd.Series([False] * len(df))
        for flag in ["Not Full Market Price", "VAT Exclusive"]:
            vals = df[flag].astype(str).str.strip() if flag in df.columns else pd.Series([], dtype=str)
            if len(vals):
                flag_mask = flag_mask | ~vals.isin(["0", "1"])
        price_mask = price.isna() | (price <= 0)
        range_issues = sample_rows(df, price_mask | flag_mask, ["Date of Sale", "Address", "County", "Price", "Not Full Market Price", "VAT Exclusive"], 10)
    if name == "Rent by County":
        rent = number_series(df, "rent_euro")
        half = number_series(df, "half")
        range_issues = sample_rows(df, (rent <= 0) | (~half.isin([1, 2])), ["rent_euro", "year", "half", "half_year", "county"], 10)
    if name == "Population by County":
        pop = number_series(df, "VALUE")
        range_issues = sample_rows(df, pop <= 0, ["Year", "County", "VALUE"], 10)

    arithmetic = []
    if name == "Housing Prices":
        dwellings = number_series(df, "Total Dwellings Built")
        floor_area = number_series(df, "Estd. Total Floor Area (sqm)")
        avg_size = number_series(df, "Weighted Avg Dwelling Size (sqm)")
        mean_price = number_series(df, "Mean Sale Price")
        price_sqm = number_series(df, "Price per sqm")

        avg_expected = floor_area / dwellings
        avg_mask = dwellings.notna() & floor_area.notna() & avg_size.notna() & (dwellings != 0) & ((avg_expected - avg_size).abs() > 0.05)
        arithmetic.append({
            "Check": "Estd. Total Floor Area / Total Dwellings Built = Weighted Avg Dwelling Size",
            "Result": "Pass" if int(avg_mask.sum()) == 0 else "Fail",
            "Issues": int(avg_mask.sum()),
            "Samples": sample_rows(df, avg_mask, ["Year", "County", "Total Dwellings Built", "Estd. Total Floor Area (sqm)", "Weighted Avg Dwelling Size (sqm)"], 10),
        })

        sqm_expected = mean_price / avg_size
        sqm_mask = mean_price.notna() & avg_size.notna() & price_sqm.notna() & (avg_size != 0) & ((sqm_expected - price_sqm).abs() > 0.05)
        arithmetic.append({
            "Check": "Mean Sale Price / Weighted Avg Dwelling Size = Price per sqm",
            "Result": "Pass" if int(sqm_mask.sum()) == 0 else "Fail",
            "Issues": int(sqm_mask.sum()),
            "Samples": sample_rows(df, sqm_mask, ["Year", "County", "Mean Sale Price", "Weighted Avg Dwelling Size (sqm)", "Price per sqm"], 10),
        })

    unique_counts = {}
    for col in ["Year", "year", "County", "county", "NUTS 2 Region", "half_year"]:
        if col in df.columns:
            unique_counts[col] = int(df[col].nunique(dropna=True))

    checks = [
        {"Validation Check": "Missing values - all columns", "Result": "None" if all_missing == 0 else "Found", "Details": str(all_missing)},
        {"Validation Check": "Missing values - critical columns", "Result": "None" if critical_missing == 0 else "Found", "Details": str(critical_missing)},
        {"Validation Check": "Negative numeric values", "Result": "None" if negative_count == 0 else "Found", "Details": str(negative_count)},
        {"Validation Check": "Non-numeric values in numeric columns", "Result": "None" if non_numeric_count == 0 else "Found", "Details": str(non_numeric_count)},
        {"Validation Check": "Integer fields", "Result": "Pass" if non_integer_count == 0 else "Fail", "Details": str(non_integer_count)},
        {"Validation Check": "Duplicate logical keys", "Result": "None" if duplicate_count == 0 else "Found", "Details": str(duplicate_count)},
        {"Validation Check": "Text consistency", "Result": "Pass" if len(text_issues) == 0 else "Review", "Details": str(len(text_issues))},
        {"Validation Check": "Date / period validity", "Result": "Pass" if len(date_issues) == 0 else "Fail", "Details": str(len(date_issues))},
        {"Validation Check": "Domain range checks", "Result": "Pass" if len(range_issues) == 0 else "Fail", "Details": str(len(range_issues))},
    ]
    for item in arithmetic:
        checks.append({"Validation Check": item["Check"], "Result": item["Result"], "Details": str(item["Issues"])})

    status = "Pass"
    for check in checks:
        if check["Result"] in {"Fail", "Found", "Review"}:
            if check["Validation Check"] == "Missing values - all columns" and name in {"Housing Prices", "Rent by County"}:
                continue
            status = "Review required"
            break

    return {
        "dataset": name,
        "file": str(config["path"]),
        "rows": rows,
        "columns": cols,
        "headers": list(df.columns),
        "critical_columns": critical_cols,
        "logical_key": key_cols,
        "unique_counts": unique_counts,
        "checks": checks,
        "overall": status,
        "duplicate_samples": duplicate_samples,
        "text_issues": text_issues,
        "date_issues": date_issues,
        "range_issues": range_issues,
        "numeric_issues": numeric_issues[:10],
        "arithmetic": arithmetic,
    }


def main():
    results = [summarize_dataset(name, config) for name, config in DATASETS.items()]
    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    for result in results:
        print(result["dataset"], result["rows"], "rows", result["overall"])
        for check in result["checks"]:
            print("  ", check["Validation Check"], check["Result"], check["Details"])


if __name__ == "__main__":
    main()
