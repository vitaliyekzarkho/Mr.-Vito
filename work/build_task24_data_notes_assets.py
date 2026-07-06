import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

CSV_PATH = POWER_BI_DIR / "data_notes.csv"
OUTPUT_CSV_PATH = OUTPUT_DIR / "data_notes.csv"
SPEC_PATH = POWER_BI_DIR / "task24_data_notes_page_build_spec.md"
OUTPUT_SPEC_PATH = OUTPUT_DIR / "task24_data_notes_page_build_spec.md"
MOCKUP_PATH = POWER_BI_DIR / "task24_data_notes_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task24_data_notes_page_mockup.png"

NOTES = [
    {
        "area": "Geography",
        "note": "Homelessness data is reported by homelessness region; population, rent and housing data are county-based and are aggregated via the geography bridge.",
        "impact": "Regional comparisons depend on the bridge assumptions.",
        "severity": "Medium",
    },
    {
        "area": "Accommodation",
        "note": "Accommodation category totals do not perfectly equal total adults in every region; Mid-West has the largest gap.",
        "impact": "Accommodation page shows category shares relative to total adults and keeps the validation caveat visible.",
        "severity": "High",
    },
    {
        "area": "Rent",
        "note": "Rent is a half-year time series, while homelessness is a regional snapshot repeated across rent periods.",
        "impact": "Rent pressure visuals show association only, not a time-aligned causal analysis.",
        "severity": "High",
    },
    {
        "area": "Housing",
        "note": "2024 housing prices and supply are available, but 2024 earnings are unavailable.",
        "impact": "Price-to-income ratio defaults to 2023, the latest complete affordability year.",
        "severity": "High",
    },
    {
        "area": "Unemployment",
        "note": "Unemployment is NUTS2-level, not county or homelessness-region level.",
        "impact": "Economic context should be read as broad regional context.",
        "severity": "Medium",
    },
    {
        "area": "North-East",
        "note": "North-East spans two NUTS2 regions: Eastern and Midland, and Northern and Western.",
        "impact": "North-East unemployment context is mixed geography and should not be collapsed silently.",
        "severity": "High",
    },
    {
        "area": "Causality",
        "note": "Rent, housing affordability and unemployment pages show observed association, not causation.",
        "impact": "Interpretations should use careful wording and avoid claims that one metric causes homelessness.",
        "severity": "High",
    },
    {
        "area": "Population",
        "note": "Homelessness rates use 2022 county population aggregated to homelessness regions.",
        "impact": "Rates are suitable for regional comparison but depend on the chosen population year.",
        "severity": "Low",
    },
]

GRAIN = [
    ["Homelessness", "homelessness_region", "9"],
    ["Population", "county", "26"],
    ["Bridge", "homelessness_region + county", "26"],
    ["Rent Pressure", "homelessness_region + half_year", "99"],
    ["Housing Affordability", "homelessness_region + year", "135"],
    ["Economic Context", "region + nuts2 + year", "60"],
]


def get_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def write_csv(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["area", "note", "impact", "severity"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(NOTES)


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def write_spec():
    note_rows = [[n["area"], n["severity"], n["note"], n["impact"]] for n in NOTES]
    spec = f"""# Task 24 - Data Notes Page Build Spec

## Page Intent

After this page, the user should understand the main data limitations, grain differences, geography assumptions and interpretation rules behind the report.

## Data Source

Power BI-ready extract:

```text
Project/Power BI/data_notes.csv
```

This page is explanatory. It does not introduce a new analytical measure.

## Required Fields

{md_table(["Field", "Use"], [
    ["`area`", "Limitation category"],
    ["`note`", "What the user needs to know"],
    ["`impact`", "How it affects interpretation"],
    ["`severity`", "Visual priority"],
])}

## Visual 1 - Key Data Notes

{md_table(["Setting", "Value"], [
    ["Visual type", "Table or multi-row card"],
    ["Columns", "`area`, `severity`, `note`, `impact`"],
    ["Sort", "High severity first"],
    ["Title", "`Key Data Notes`"],
])}

## Visual 2 - Dataset Grain Summary

{md_table(["Dataset", "Grain", "Rows"], GRAIN)}

## Visual 3 - Interpretation Rules

Use three short rule cards:

{md_table(["Rule", "Meaning"], [
    ["Compare rates, not only counts", "Regional population size changes interpretation."],
    ["Association, not causation", "Rent, housing and unemployment explain context, not proof."],
    ["Respect geography grain", "County, homelessness region and NUTS2 joins have different precision."],
])}

## Data Notes Catalogue

{md_table(["Area", "Severity", "Note", "Impact"], note_rows)}

## Acceptance Criteria

- `data_notes.csv` contains 8 rows.
- Page includes geography, accommodation, rent, housing, unemployment and causality limitations.
- Page clearly says association is not causation.
- Page explains why North-East is special for unemployment.
- Page gives the user confidence that limitations were handled intentionally, not discovered accidentally.
"""
    SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPEC_PATH.write_text(spec, encoding="utf-8")
    OUTPUT_SPEC_PATH.write_text(spec, encoding="utf-8")


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=12, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 22, y1 + 18), title, fill="#52616B", font=get_font(20))
    draw.text((x1 + 22, y1 + 58), value, fill="#17324D", font=get_font(30, bold=True))
    if subtitle:
        draw.text((x1 + 22, y1 + 96), subtitle, fill="#7A8A99", font=get_font(15))


def severity_color(severity):
    return {"High": "#D95F59", "Medium": "#E9A93A", "Low": "#2A9D8F"}[severity]


def draw_notes_table(draw, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Key Data Notes", fill="#17324D", font=get_font(25, bold=True))
    headers = ["Area", "Severity", "Note", "Impact"]
    xs = [x1 + 24, x1 + 150, x1 + 260, x1 + 765]
    for x, header in zip(xs, headers):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(14, bold=True))
    y = y1 + 94
    ordered = sorted(NOTES, key=lambda n: {"High": 0, "Medium": 1, "Low": 2}[n["severity"]])
    for note in ordered:
        draw.text((xs[0], y), note["area"], fill="#2F3A44", font=get_font(13, bold=True))
        draw.rounded_rectangle((xs[1], y + 1, xs[1] + 66, y + 20), radius=5, fill=severity_color(note["severity"]))
        draw.text((xs[1] + 10, y + 2), note["severity"], fill="#FFFFFF", font=get_font(12, bold=True))
        note_lines = wrap_text(draw, note["note"], get_font(13), 470)[:2]
        impact_lines = wrap_text(draw, note["impact"], get_font(13), 370)[:2]
        for i, line in enumerate(note_lines):
            draw.text((xs[2], y + i * 16), line, fill="#2F3A44", font=get_font(13))
        for i, line in enumerate(impact_lines):
            draw.text((xs[3], y + i * 16), line, fill="#52616B", font=get_font(13))
        y += 50


def draw_grain_table(draw, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Dataset Grain Summary", fill="#17324D", font=get_font(25, bold=True))
    xs = [x1 + 24, x1 + 210, x1 + 480]
    for x, header in zip(xs, ["Dataset", "Grain", "Rows"]):
        draw.text((x, y1 + 66), header, fill="#52616B", font=get_font(15, bold=True))
    y = y1 + 96
    for dataset, grain, rows in GRAIN:
        draw.text((xs[0], y), dataset, fill="#2F3A44", font=get_font(14, bold=True))
        draw.text((xs[1], y), grain, fill="#2F3A44", font=get_font(14))
        draw.text((xs[2], y), rows, fill="#17324D", font=get_font(14, bold=True))
        y += 31


def draw_rules(draw, box):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)
    draw.text((x1 + 24, y1 + 22), "Interpretation Rules", fill="#17324D", font=get_font(25, bold=True))
    rules = [
        ("Rates before counts", "Use per-10,000 rates for regional comparison."),
        ("Association only", "Rent, housing and unemployment are context, not proof."),
        ("Respect geography", "County, region and NUTS2 grain are not interchangeable."),
    ]
    y = y1 + 78
    for title, body in rules:
        draw.rounded_rectangle((x1 + 24, y, x2 - 24, y + 66), radius=8, fill="#F6F8FA", outline="#D9E2EA", width=1)
        draw.text((x1 + 42, y + 12), title, fill="#17324D", font=get_font(17, bold=True))
        draw.text((x1 + 42, y + 38), body, fill="#52616B", font=get_font(14))
        y += 80


def write_mockup():
    width, height = 1600, 1240
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)

    draw.text((60, 50), "Data Notes", fill="#17324D", font=get_font(42, bold=True))
    draw.text((62, 102), "Limitations, grain and interpretation rules for the report", fill="#627386", font=get_font(23))

    high_count = sum(1 for note in NOTES if note["severity"] == "High")
    medium_count = sum(1 for note in NOTES if note["severity"] == "Medium")
    low_count = sum(1 for note in NOTES if note["severity"] == "Low")

    draw_card(draw, (60, 146, 405, 270), "Total Notes", str(len(NOTES)), "Documented limitations")
    draw_card(draw, (435, 146, 780, 270), "High Priority", str(high_count), "Must be visible")
    draw_card(draw, (810, 146, 1165, 270), "Medium Priority", str(medium_count), "Context caveats")
    draw_card(draw, (1195, 146, 1540, 270), "Low Priority", str(low_count), "Reference note")

    draw_notes_table(draw, (60, 320, 1540, 790))
    draw_grain_table(draw, (60, 825, 790, 1155))
    draw_rules(draw, (830, 825, 1540, 1155))

    draw.rounded_rectangle((60, 1185, 1540, 1220), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1195),
        "Report rule: use careful language throughout. Observed relationships are analytical context, not causal claims.",
        fill="#52616B",
        font=get_font(16),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    write_csv(CSV_PATH)
    write_csv(OUTPUT_CSV_PATH)
    write_spec()
    write_mockup()
    print(f"Created {CSV_PATH}")
    print(f"Created {OUTPUT_CSV_PATH}")
    print(f"Created {SPEC_PATH}")
    print(f"Created {OUTPUT_SPEC_PATH}")
    print(f"Created {MOCKUP_PATH}")
    print(f"Created {OUTPUT_MOCKUP_PATH}")


if __name__ == "__main__":
    main()
