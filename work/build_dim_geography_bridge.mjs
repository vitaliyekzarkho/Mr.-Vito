import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = "C:/Users/User/Documents/Codex/2026-07-04/task-3-data-validation-capstone-report";
const buildDir = path.join(projectRoot, "Project", "Build Artifacts");
const outputDir = path.join(projectRoot, "outputs");
const buildPath = path.join(buildDir, "dim_geography_bridge.xlsx");
const outputPath = path.join(outputDir, "dim_geography_bridge.xlsx");

const headers = [
  "homelessness_region",
  "county",
  "nuts3_region",
  "nuts2_region",
  "notes",
];

const rows = [
  ["Dublin", "Dublin", "Dublin", "Eastern and Midland", "County-level Dublin is treated as one aggregate county unit"],
  ["Mid-East", "Kildare", "Mid-East", "Eastern and Midland", "Homelessness Mid-East excludes Louth if Louth is assigned to North-East"],
  ["Mid-East", "Meath", "Mid-East", "Eastern and Midland", "Homelessness Mid-East excludes Louth if Louth is assigned to North-East"],
  ["Mid-East", "Wicklow", "Mid-East", "Eastern and Midland", "Homelessness Mid-East excludes Louth if Louth is assigned to North-East"],
  ["Midlands", "Laois", "Midland", "Eastern and Midland", "Full NUTS3 match"],
  ["Midlands", "Longford", "Midland", "Eastern and Midland", "Full NUTS3 match"],
  ["Midlands", "Offaly", "Midland", "Eastern and Midland", "Full NUTS3 match"],
  ["Midlands", "Westmeath", "Midland", "Eastern and Midland", "Full NUTS3 match"],
  ["Mid-West", "Clare", "Mid-West", "Southern", "Full NUTS3 match"],
  ["Mid-West", "Limerick", "Mid-West", "Southern", "Full NUTS3 match"],
  ["Mid-West", "Tipperary", "Mid-West", "Southern", "Full NUTS3 match"],
  ["North-East", "Cavan", "Border", "Northern and Western", "Region crosses NUTS2 boundary"],
  ["North-East", "Louth", "Mid-East", "Eastern and Midland", "Region crosses NUTS2 boundary"],
  ["North-East", "Monaghan", "Border", "Northern and Western", "Region crosses NUTS2 boundary"],
  ["North-West", "Donegal", "Border", "Northern and Western", "Border NUTS3 is split across North-East and North-West"],
  ["North-West", "Leitrim", "Border", "Northern and Western", "Border NUTS3 is split across North-East and North-West"],
  ["North-West", "Sligo", "Border", "Northern and Western", "Border NUTS3 is split across North-East and North-West"],
  ["South-East", "Carlow", "South-East", "Southern", "Full NUTS3 match"],
  ["South-East", "Kilkenny", "South-East", "Southern", "Full NUTS3 match"],
  ["South-East", "Waterford", "South-East", "Southern", "Full NUTS3 match"],
  ["South-East", "Wexford", "South-East", "Southern", "Full NUTS3 match"],
  ["South-West", "Cork", "South-West", "Southern", "Full NUTS3 match"],
  ["South-West", "Kerry", "South-West", "Southern", "Full NUTS3 match"],
  ["West", "Galway", "West", "Northern and Western", "Full NUTS3 match"],
  ["West", "Mayo", "West", "Northern and Western", "Full NUTS3 match"],
  ["West", "Roscommon", "West", "Northern and Western", "Full NUTS3 match"],
];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("dim_geography_bridge");
sheet.showGridLines = false;

sheet.getRange(`A1:E${rows.length + 1}`).values = [headers, ...rows];
sheet.getRange("A1:E1").format = {
  fill: "#1F4E79",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
sheet.getRange(`A1:E${rows.length + 1}`).format.borders = {
  preset: "all",
  style: "thin",
  color: "#D9E2EA",
};
sheet.getRange("A:A").format.columnWidth = 22;
sheet.getRange("B:B").format.columnWidth = 18;
sheet.getRange("C:C").format.columnWidth = 18;
sheet.getRange("D:D").format.columnWidth = 24;
sheet.getRange("E:E").format.columnWidth = 62;
sheet.getRange(`A1:E${rows.length + 1}`).format.wrapText = true;
sheet.freezePanes.freezeRows(1);

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });

const inspect = await workbook.inspect({
  kind: "table",
  range: `dim_geography_bridge!A1:E${rows.length + 1}`,
  include: "values",
  tableMaxRows: 30,
  tableMaxCols: 5,
});
console.log(inspect.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(buildPath);
await output.save(outputPath);

console.log(JSON.stringify({ buildPath, outputPath, rows: rows.length, columns: headers.length }));
