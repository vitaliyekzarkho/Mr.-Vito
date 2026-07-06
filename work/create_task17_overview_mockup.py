import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
DATA_PATH = PROJECT_ROOT / "outputs" / "overview_homelessness_rate.csv"
POWER_BI_PATH = PROJECT_ROOT / "Project" / "Power BI" / "task17_overview_page_mockup.png"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "task17_overview_page_mockup.png"


def font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def draw_card(draw, box, title, value, subtitle=None):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=18, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 28, y1 + 22), title, fill="#52616B", font=font(24))
    draw.text((x1 + 28, y1 + 62), value, fill="#16324F", font=font(46, bold=True))
    if subtitle:
        draw.text((x1 + 28, y2 - 38), subtitle, fill="#7A8793", font=font(18))


def draw_bar_chart(draw, box, title, rows, value_key, value_format, color):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#D9E2EA", width=2)
    draw.text((x1 + 24, y1 + 18), title, fill="#16324F", font=font(25, bold=True))

    chart_x = x1 + 170
    chart_y = y1 + 68
    chart_w = x2 - chart_x - 96
    bar_h = 22
    gap = 13
    max_value = max(float(row[value_key]) for row in rows)

    for i, row in enumerate(rows):
        y = chart_y + i * (bar_h + gap)
        label = row["homelessness_region"]
        value = float(row[value_key])
        bar_w = int((value / max_value) * chart_w)
        draw.text((x1 + 24, y - 1), label, fill="#263238", font=font(18))
        draw.rounded_rectangle((chart_x, y, chart_x + chart_w, y + bar_h), radius=8, fill="#EEF3F7")
        draw.rounded_rectangle((chart_x, y, chart_x + bar_w, y + bar_h), radius=8, fill=color)
        draw.text((chart_x + bar_w + 10, y - 2), value_format(value), fill="#263238", font=font(17, bold=True))


def main():
    with DATA_PATH.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    total_homeless = sum(int(row["homeless_adults"]) for row in rows)
    total_population = sum(int(row["population"]) for row in rows)
    national_rate = (total_homeless / total_population) * 10000

    by_count = sorted(rows, key=lambda r: int(r["homeless_adults"]), reverse=True)
    by_rate = sorted(rows, key=lambda r: float(r["homeless_adults_per_10000"]), reverse=True)

    image = Image.new("RGB", (1600, 900), "#F5F7FA")
    draw = ImageDraw.Draw(image)

    draw.text((60, 42), "Homelessness in Ireland - Overview", fill="#102A43", font=font(42, bold=True))
    draw.text((62, 94), "Population-adjusted regional view based on 2022 county population", fill="#627384", font=font(22))

    draw_card(
        draw,
        (60, 145, 510, 285),
        "Homeless Adults",
        f"{total_homeless:,}",
        "Total across 9 homelessness regions",
    )
    draw_card(
        draw,
        (550, 145, 1040, 285),
        "Per 10,000 Population",
        f"{national_rate:.2f}",
        "Population denominator: 5,149,139",
    )
    draw_card(
        draw,
        (1080, 145, 1540, 285),
        "Highest Regional Rate",
        f"{by_rate[0]['homelessness_region']}",
        f"{float(by_rate[0]['homeless_adults_per_10000']):.2f} per 10,000",
    )

    draw_bar_chart(
        draw,
        (60, 330, 770, 775),
        "Homeless Adults by Region",
        by_count,
        "homeless_adults",
        lambda v: f"{int(v):,}",
        "#2563A6",
    )
    draw_bar_chart(
        draw,
        (830, 330, 1540, 775),
        "Homeless Adults per 10,000 Population",
        by_rate,
        "homeless_adults_per_10000",
        lambda v: f"{v:.2f}",
        "#0F766E",
    )

    note_box = (60, 815, 1540, 865)
    draw.rounded_rectangle(note_box, radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 829),
        "Data note: Population denominator uses 2022 county population aggregated to homelessness regions through the geography bridge.",
        fill="#52616B",
        font=font(20),
    )

    POWER_BI_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(POWER_BI_PATH)
    image.save(OUTPUT_PATH)
    print(f"Created {POWER_BI_PATH}")
    print(f"Created {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
