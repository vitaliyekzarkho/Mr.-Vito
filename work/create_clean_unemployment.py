import csv
from pathlib import Path

RAW_PATH = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data\unemployment.csv.csv")
PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
CLEAN_PATH = PROJECT_ROOT / "Project" / "Clean Data" / "clean_unemployment.csv"
OUTPUT_COPY_PATH = PROJECT_ROOT / "outputs" / "clean_unemployment.csv"

OUTPUT_COLUMNS = [
    "year",
    "age_group",
    "sex",
    "education_attainment_level",
    "nuts2_region",
    "unemployment_rate",
]


def standardise_text(value: str) -> str:
    return " ".join(str(value).strip().split())


def to_int(value: str, column: str) -> int:
    text = str(value).strip()
    if text == "":
        raise ValueError(f"Missing integer value in {column}")
    number = float(text)
    if number % 1 != 0:
        raise ValueError(f"Non-integer value in {column}: {value}")
    return int(number)


def to_decimal_or_blank(value: str):
    text = str(value).strip()
    if text == "":
        return ""
    return round(float(text), 3)


def read_and_clean():
    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "Year",
            "Age Group",
            "Sex",
            "Education Attainment Level",
            "NUTS 2 Region",
            "UNIT",
            "VALUE",
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing raw columns: {missing}")

        rows = []
        for row in reader:
            nuts2_region = standardise_text(row["NUTS 2 Region"])
            if nuts2_region == "Ireland":
                continue

            unit = standardise_text(row["UNIT"])
            if unit != "%":
                raise ValueError(f"Unexpected UNIT: {unit}")

            cleaned = {
                "year": to_int(row["Year"], "year"),
                "age_group": standardise_text(row["Age Group"]),
                "sex": standardise_text(row["Sex"]),
                "education_attainment_level": standardise_text(row["Education Attainment Level"]),
                "nuts2_region": nuts2_region,
                "unemployment_rate": to_decimal_or_blank(row["VALUE"]),
            }
            rows.append(cleaned)

    return rows


def validate(rows):
    if len(rows) != 1296:
        raise ValueError(f"Expected 1296 NUTS2 unemployment rows, found {len(rows)}")

    key_columns = ["year", "age_group", "sex", "education_attainment_level", "nuts2_region"]
    keys = [tuple(row[column] for column in key_columns) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate unemployment logical keys found")

    years = {row["year"] for row in rows}
    if years != set(range(2019, 2025)):
        raise ValueError(f"Unexpected years: {sorted(years)}")

    nuts2_regions = {row["nuts2_region"] for row in rows}
    expected_nuts2 = {"Eastern and Midland", "Northern and Western", "Southern"}
    if nuts2_regions != expected_nuts2:
        raise ValueError(f"Unexpected NUTS2 regions: {sorted(nuts2_regions ^ expected_nuts2)}")

    for row in rows:
        rate = row["unemployment_rate"]
        if rate == "":
            continue
        if not isinstance(rate, float):
            raise TypeError(f"unemployment_rate must be decimal or blank: {rate}")
        if rate < 0 or rate > 100:
            raise ValueError(f"Invalid unemployment_rate: {rate}")


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
    missing_rates = sum(1 for row in rows if row["unemployment_rate"] == "")
    print(f"Created {CLEAN_PATH}")
    print(f"Created {OUTPUT_COPY_PATH}")
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(OUTPUT_COLUMNS)}")
    print(f"Missing unemployment_rate: {missing_rates}")
    print(f"NUTS2 regions: {len({row['nuts2_region'] for row in rows})}")


if __name__ == "__main__":
    main()
