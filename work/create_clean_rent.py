import csv
import re
from pathlib import Path

RAW_PATH = Path(r"C:\Users\User\Desktop\Ireland Homelessness Project\Raw Data\rent_by_county.csv.csv")
PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
CLEAN_PATH = PROJECT_ROOT / "Project" / "Clean Data" / "clean_rent.csv"
OUTPUT_COPY_PATH = PROJECT_ROOT / "outputs" / "clean_rent.csv"

OUTPUT_COLUMNS = [
    "year",
    "half",
    "half_year",
    "county",
    "province",
    "property_type",
    "bedrooms",
    "bedrooms_num",
    "rent_euro",
    "is_county_aggregate",
]


def standardise_text(value: str) -> str:
    return " ".join(str(value).strip().split())


def to_int(value: str, column: str, allow_blank: bool = False):
    text = str(value).strip()
    if text == "" and allow_blank:
        return ""
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


def to_bool_text(value: str, column: str) -> str:
    text = str(value).strip()
    if text not in {"True", "False"}:
        raise ValueError(f"Invalid boolean value in {column}: {value}")
    return text


def read_and_clean():
    with RAW_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {
            "rent_euro",
            "year",
            "half",
            "half_year",
            "county",
            "province",
            "property_type",
            "bedrooms",
            "bedrooms_num",
            "is_county_aggregate",
        }
        missing = sorted(required - set(reader.fieldnames or []))
        if missing:
            raise ValueError(f"Missing raw columns: {missing}")

        cleaned_rows = []
        for row in reader:
            cleaned = {
                "year": to_int(row["year"], "year"),
                "half": to_int(row["half"], "half"),
                "half_year": standardise_text(row["half_year"]),
                "county": standardise_text(row["county"]),
                "province": standardise_text(row["province"]),
                "property_type": standardise_text(row["property_type"]),
                "bedrooms": standardise_text(row["bedrooms"]),
                "bedrooms_num": to_int(row["bedrooms_num"], "bedrooms_num", allow_blank=True),
                "rent_euro": round(to_decimal(row["rent_euro"], "rent_euro"), 2),
                "is_county_aggregate": to_bool_text(row["is_county_aggregate"], "is_county_aggregate"),
            }
            cleaned_rows.append(cleaned)

    return cleaned_rows


def validate(rows):
    if len(rows) != 286:
        raise ValueError(f"Expected 286 rent rows, found {len(rows)}")

    keys = [(row["year"], row["half_year"], row["county"], row["property_type"], row["bedrooms"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate rent logical keys found")

    counties = {row["county"] for row in rows}
    if len(counties) != 26:
        raise ValueError(f"Expected 26 counties, found {len(counties)}")

    half_years = {row["half_year"] for row in rows}
    if len(half_years) != 11:
        raise ValueError(f"Expected 11 half-year periods, found {len(half_years)}")

    for row in rows:
        if row["half"] not in {1, 2}:
            raise ValueError(f"Invalid half: {row['half']}")
        if not re.fullmatch(r"\d{4}H[12]", row["half_year"]):
            raise ValueError(f"Invalid half_year: {row['half_year']}")
        expected_half = int(row["half_year"][-1])
        expected_year = int(row["half_year"][:4])
        if row["half"] != expected_half or row["year"] != expected_year:
            raise ValueError(f"half_year mismatch: {row}")
        if row["rent_euro"] <= 0:
            raise ValueError(f"Invalid rent_euro: {row['rent_euro']}")
        if row["property_type"] != "All property types":
            raise ValueError(f"Unexpected property_type: {row['property_type']}")
        if row["bedrooms"] != "All bedrooms":
            raise ValueError(f"Unexpected bedrooms: {row['bedrooms']}")


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
    print(f"Half-years: {len({row['half_year'] for row in rows})}")


if __name__ == "__main__":
    main()
