import csv
from collections import defaultdict
from pathlib import Path

RAW_PATH = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data\population_by_county.csv.csv")
PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
CLEAN_PATH = PROJECT_ROOT / "Project" / "Clean Data" / "clean_population.csv"
OUTPUT_COPY_PATH = PROJECT_ROOT / "outputs" / "clean_population.csv"

OUTPUT_COLUMNS = ["year", "county", "population", "population_share_pct"]


def standardise_county(value: str) -> str:
    text = " ".join(str(value).strip().split())
    if text.startswith("Co. "):
        text = text[4:]
    return text


def to_int(value: str, column: str) -> int:
    text = str(value).strip()
    if text == "":
        raise ValueError(f"Missing integer value in {column}")
    number = float(text)
    if number % 1 != 0:
        raise ValueError(f"Non-integer value in {column}: {value}")
    return int(number)


def to_decimal(value: str, column: str) -> float:
    text = str(value).strip()
    if text == "":
        raise ValueError(f"Missing decimal value in {column}")
    return float(text)


def read_and_clean():
    grouped = defaultdict(dict)

    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"Year", "County", "UNIT", "VALUE"}
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing raw columns: {missing}")

        for row in reader:
            county = standardise_county(row["County"])
            if county == "Ireland":
                continue

            year = to_int(row["Year"], "year")
            key = (year, county)
            grouped[key]["year"] = year
            grouped[key]["county"] = county

            unit = str(row["UNIT"]).strip()
            if unit == "Number":
                grouped[key]["population"] = to_int(row["VALUE"], "population")
            elif unit == "%":
                grouped[key]["population_share_pct"] = to_decimal(row["VALUE"], "population_share_pct")
            else:
                raise ValueError(f"Unexpected UNIT: {unit}")

    cleaned_rows = []
    for key in sorted(grouped):
        row = grouped[key]
        for column in OUTPUT_COLUMNS:
            if column not in row:
                raise ValueError(f"Missing {column} for {key}")
        cleaned_rows.append(row)

    return cleaned_rows


def validate(rows):
    if len(rows) != 26:
        raise ValueError(f"Expected 26 counties, found {len(rows)}")

    keys = [(row["year"], row["county"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate year + county keys found")

    for row in rows:
        if not isinstance(row["year"], int):
            raise TypeError("year must be int")
        if not isinstance(row["population"], int):
            raise TypeError("population must be int")
        if not isinstance(row["population_share_pct"], float):
            raise TypeError("population_share_pct must be float")
        if row["population"] <= 0:
            raise ValueError(f"Invalid population for {row['county']}: {row['population']}")
        if row["population_share_pct"] <= 0:
            raise ValueError(f"Invalid population_share_pct for {row['county']}: {row['population_share_pct']}")

    total_share = sum(row["population_share_pct"] for row in rows)
    if round(total_share, 1) != 100.0:
        raise ValueError(f"County population shares do not sum to 100.0: {total_share}")


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
    print(f"Population total: {sum(row['population'] for row in rows)}")
    print(f"Population share total: {sum(row['population_share_pct'] for row in rows):.1f}")


if __name__ == "__main__":
    main()
