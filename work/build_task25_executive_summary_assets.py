from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(r"C:\Users\User\Documents\Codex\2026-07-04\task-3-data-validation-capstone-report")
POWER_BI_DIR = PROJECT_ROOT / "Project" / "Power BI"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

SUMMARY_PATH = POWER_BI_DIR / "task25_executive_summary.md"
OUTPUT_SUMMARY_PATH = OUTPUT_DIR / "task25_executive_summary.md"
MOCKUP_PATH = POWER_BI_DIR / "task25_executive_summary_page_mockup.png"
OUTPUT_MOCKUP_PATH = OUTPUT_DIR / "task25_executive_summary_page_mockup.png"

OBJECTIVE = (
    "This project analyses regional homelessness patterns across Ireland using official public datasets on "
    "homelessness, population, rent, housing and unemployment. The purpose is to create a structured evidence base "
    "for comparing homelessness rates across regions and understanding the wider housing and economic context."
)

KEY_FINDINGS = [
    "Ireland records 11,944 homeless adults in the analysed homelessness dataset, equal to 23.2 adults per 10,000 population.",
    "Dublin has the highest homelessness rate at 57.26 adults per 10,000 population.",
    "Adults aged 25-44 form the largest demographic group, representing 52.37% of homeless adults.",
    "Private Emergency Accommodation is the dominant accommodation type, representing 71.5% of adults across regions.",
    "Rent pressure shows a strong positive association with homelessness rates in the default period, with Pearson correlation 0.885.",
    "Housing affordability also shows a strong positive association with homelessness rates in 2023, with price-to-income correlation 0.913.",
    "Unemployment data should be interpreted cautiously because it is only available at NUTS2 level; North-East spans two NUTS2 regions.",
]

BUSINESS_IMPLICATIONS = [
    "Regional comparison should prioritise population-adjusted homelessness rates rather than absolute counts alone.",
    "High-rate regions may require prioritised review of housing support capacity and temporary accommodation pressure.",
    "Housing affordability and rent pressure should be monitored alongside homelessness statistics as contextual indicators.",
    "Geography grain should be handled explicitly when combining county, homelessness-region and NUTS2 datasets.",
]

LIMITATIONS = (
    "The analysis identifies regional patterns and associations, not causal relationships. Homelessness is a regional "
    "snapshot, while rent is a half-year time series. Housing affordability uses 2023 for price-to-income ratios because "
    "2024 earnings are unavailable. Unemployment data is NUTS2-level and should not be treated as a precise local rate "
    "for every homelessness region."
)

CONCLUSION = (
    "The analysis provides a regional evidence-based overview of homelessness across Ireland using official public "
    "datasets. While the report identifies several meaningful regional patterns, the results should be interpreted "
    "within the documented data limitations and should not be used to infer direct causal relationships."
)


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


def write_markdown():
    findings = "\n".join(f"- {item}" for item in KEY_FINDINGS)
    implications = "\n".join(f"- {item}" for item in BUSINESS_IMPLICATIONS)
    content = f"""# Task 25 - Executive Summary

## Objective

{OBJECTIVE}

## Key Findings

{findings}

## Business Implications

{implications}

## Limitations

{LIMITATIONS}

## Conclusion

{CONCLUSION}
"""
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(content, encoding="utf-8")
    OUTPUT_SUMMARY_PATH.write_text(content, encoding="utf-8")


def draw_section(draw, x, y, width, title, body=None, bullets=None):
    draw.text((x, y), title, fill="#17324D", font=get_font(24, bold=True))
    y += 38
    if body:
        for line in wrap_text(draw, body, get_font(17), width):
            draw.text((x, y), line, fill="#2F3A44", font=get_font(17))
            y += 24
        y += 10
    if bullets:
        for bullet in bullets:
            lines = wrap_text(draw, bullet, get_font(16), width - 30)
            draw.text((x, y), "-", fill="#17324D", font=get_font(16, bold=True))
            for i, line in enumerate(lines):
                draw.text((x + 22, y + i * 22), line, fill="#2F3A44", font=get_font(16))
            y += max(1, len(lines)) * 22 + 8
    return y


def draw_panel(draw, box):
    draw.rounded_rectangle(box, radius=10, fill="#FFFFFF", outline="#C9D6E2", width=1)


def write_mockup():
    width, height = 1600, 1320
    image = Image.new("RGB", (width, height), "#F3F6F9")
    draw = ImageDraw.Draw(image)

    draw.text((60, 48), "Executive Summary", fill="#17324D", font=get_font(44, bold=True))
    draw.text((62, 104), "Ireland homelessness analytics project", fill="#627386", font=get_font(23))

    draw_panel(draw, (60, 150, 1540, 280))
    draw_section(draw, 84, 176, 1410, "Objective", OBJECTIVE)

    draw_panel(draw, (60, 315, 980, 850))
    draw_section(draw, 84, 344, 850, "Key Findings", bullets=KEY_FINDINGS)

    draw_panel(draw, (1010, 315, 1540, 660))
    draw_section(draw, 1034, 344, 460, "Business Implications", bullets=BUSINESS_IMPLICATIONS)

    draw_panel(draw, (1010, 695, 1540, 990))
    draw_section(draw, 1034, 704, 460, "Limitations", LIMITATIONS)

    draw_panel(draw, (60, 1030, 1540, 1195))
    draw_section(draw, 84, 1058, 1410, "Conclusion", CONCLUSION)

    draw.rounded_rectangle((60, 1235, 1540, 1275), radius=10, fill="#FFFFFF", outline="#D9E2EA", width=1)
    draw.text(
        (80, 1245),
        "Summary rule: findings are evidence-based patterns from the prepared dataset, not causal policy claims.",
        fill="#52616B",
        font=get_font(17),
    )

    MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MOCKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(MOCKUP_PATH)
    image.save(OUTPUT_MOCKUP_PATH)


def main():
    write_markdown()
    write_mockup()
    print(f"Created {SUMMARY_PATH}")
    print(f"Created {OUTPUT_SUMMARY_PATH}")
    print(f"Created {MOCKUP_PATH}")
    print(f"Created {OUTPUT_MOCKUP_PATH}")


if __name__ == "__main__":
    main()
