import csv
from pathlib import Path

RAW_PATH = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data\homelessness.csv.csv")
PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
CLEAN_PATH = PROJECT_ROOT / "Project" / "Clean Data" / "clean_homelessness.csv"
OUTPUT_COPY_PATH = PROJECT_ROOT / "outputs" / "clean_homelessness.csv"

COLUMN_MAP = {
    "Region": "homelessness_region",
    "Total Adults": "total_adults",
    "Male Adults": "male_adults",
    "Female Adults": "female_adults",
    "Adults Aged 18-24": "adults_18_24",
    "Adults Aged 25-44": "adults_25_44",
    "Adults Aged 45-64": "adults_45_64",
    "Adults Aged 65+": "adults_65_plus",
    "Number of people who accessed Private Emergency Accommodation": "private_emergency_accommodation",
    "Number of people who accessed Supported Temporary Accommodation": "supported_temporary_accommodation",
    "Number of people who accessed Temporary Emergency Accommodation": "temporary_emergency_accommodation",
    "Number of people who accessed Other Accommodation": "other_accommodation",
    "Number of people with citizenship Irish": "citizenship_irish",
    "Number of people with citizenship EEA/Uk": "citizenship_eea_uk",
    "Number of people with citizenship Non-EEA": "citizenship_non_eea",
    "Number of Families": "number_of_families",
    "Number of Adults in Families": "adults_in_families",
    "Number of Single-Parent families": "single_parent_families",
    "Number of Dependants in Families": "dependants_in_families",
}

OUTPUT_COLUMNS = list(COLUMN_MAP.values())
INTEGER_COLUMNS = [column for column in OUTPUT_COLUMNS if column != "homelessness_region"]


def to_int(value: str, column: str) -> int:
    text = str(value).strip()
    if text == "":
        raise ValueError(f"Missing integer value in {column}")
    number = float(text)
    if number % 1 != 0:
        raise ValueError(f"Non-integer value in {column}: {value}")
    return int(number)


def standardise_region(value: str) -> str:
    return " ".join(str(value).strip().split())


def read_and_clean():
    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing_columns = [column for column in COLUMN_MAP if column not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing raw columns: {missing_columns}")

        cleaned_rows = []
        for row in reader:
            cleaned = {}
            for raw_col, clean_col in COLUMN_MAP.items():
                if clean_col == "homelessness_region":
                    cleaned[clean_col] = standardise_region(row[raw_col])
                else:
                    cleaned[clean_col] = to_int(row[raw_col], clean_col)
            cleaned_rows.append(cleaned)

    return cleaned_rows


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def validate(rows):
    if len(rows) != 9:
        raise ValueError(f"Expected 9 homelessness regions, found {len(rows)}")

    regions = [row["homelessness_region"] for row in rows]
    if len(regions) != len(set(regions)):
        raise ValueError("Duplicate homelessness_region values found")

    for row in rows:
        for column in INTEGER_COLUMNS:
            value = row[column]
            if not isinstance(value, int):
                raise TypeError(f"{column} is not int: {value}")
            if value < 0:
                raise ValueError(f"{column} has negative value: {value}")

    expected_regions = {
        "Dublin",
        "Mid-East",
        "Midlands",
        "Mid-West",
        "North-East",
        "North-West",
        "South-East",
        "South-West",
        "West",
    }
    if set(regions) != expected_regions:
        raise ValueError(f"Unexpected regions: {sorted(set(regions) ^ expected_regions)}")


def main():
    rows = read_and_clean()
    validate(rows)
    write_csv(CLEAN_PATH, rows)
    write_csv(OUTPUT_COPY_PATH, rows)
    print(f"Created {CLEAN_PATH}")
    print(f"Created {OUTPUT_COPY_PATH}")
    print(f"Rows: {len(rows)}")
    print(f"Columns: {len(OUTPUT_COLUMNS)}")


if __name__ == "__main__":
    main()
